#!/usr/bin/env python3
import os
import base64
import calendar
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from fastmcp import FastMCP

mcp = FastMCP("SimpleFIN MCP Server")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_access_url() -> tuple[str, str, str]:
    """Parse SIMPLEFIN_ACCESS_URL into (base_url, username, password).

    Raises ValueError if the env var is missing or malformed.
    """
    raw = os.environ.get("SIMPLEFIN_ACCESS_URL", "").strip()
    if not raw:
        raise ValueError(
            "SIMPLEFIN_ACCESS_URL is not set. "
            "Use the claim_setup_token tool to obtain an access URL, "
            "then set it as the SIMPLEFIN_ACCESS_URL environment variable."
        )
    parsed = urlparse(raw)
    if not parsed.username or not parsed.password:
        raise ValueError(
            "SIMPLEFIN_ACCESS_URL is malformed — expected "
            "https://username:password@host/simplefin format."
        )
    base_url = f"{parsed.scheme}://{parsed.hostname}"
    if parsed.port:
        base_url += f":{parsed.port}"
    base_url += parsed.path
    return base_url, parsed.username, parsed.password


def _date_to_unix(date_str: str) -> int:
    """Convert a YYYY-MM-DD date string to a unix timestamp (UTC midnight)."""
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(calendar.timegm(dt.timetuple()))


async def _simplefin_get(endpoint: str, params: dict | None = None) -> dict:
    """Authenticated GET against the SimpleFIN API.

    Returns the parsed JSON response or raises on HTTP/network errors.
    """
    base_url, username, password = _parse_access_url()
    url = f"{base_url}{endpoint}"
    async with httpx.AsyncClient(
        auth=(username, password), timeout=30.0
    ) as client:
        resp = await client.get(url, params=params)
        if resp.status_code == 403:
            raise ValueError(
                "Authentication failed (HTTP 403). "
                "Your access URL may be invalid — try claiming a new setup token."
            )
        if resp.status_code == 402:
            raise ValueError(
                "Payment required (HTTP 402). "
                "Your SimpleFIN subscription may need renewal at "
                "https://simplefin.org."
            )
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool(description=(
    "One-time setup: claim a SimpleFIN setup token to obtain an access URL. "
    "The setup token is a base64-encoded URL provided by SimpleFIN when you "
    "create a connection. This tool decodes it, claims the access URL, and "
    "returns it. Store the returned access URL as the SIMPLEFIN_ACCESS_URL "
    "environment variable."
))
async def claim_setup_token(setup_token: str) -> dict:
    """Claim a SimpleFIN setup token and return the access URL."""
    try:
        claim_url = base64.b64decode(setup_token).decode("utf-8")
    except Exception:
        return {"success": False, "error": "Invalid setup token — could not base64-decode it."}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(claim_url)
            resp.raise_for_status()
            access_url = resp.text.strip()
    except httpx.HTTPStatusError as exc:
        return {
            "success": False,
            "error": (
                f"Failed to claim token (HTTP {exc.response.status_code}). "
                "The token may have already been claimed — each token can only "
                "be used once. Generate a new one at https://simplefin.org."
            ),
        }
    except httpx.RequestError as exc:
        return {"success": False, "error": f"Network error claiming token: {exc}"}

    return {
        "success": True,
        "access_url": access_url,
        "instructions": (
            "Set this access URL as the SIMPLEFIN_ACCESS_URL environment variable "
            "to enable the other SimpleFIN tools."
        ),
    }


@mcp.tool(description=(
    "List all connected financial accounts with current balances. "
    "Returns account names, institutions, currencies, and balances. "
    "Call this first to discover available accounts before fetching transactions."
))
async def get_accounts() -> dict:
    """Retrieve all accounts with balances (no transaction details)."""
    try:
        data = await _simplefin_get("/accounts", params={"balances-only": "1"})
    except ValueError as exc:
        return {"success": False, "error": str(exc)}
    except httpx.HTTPStatusError as exc:
        return {"success": False, "error": f"HTTP {exc.response.status_code}: {exc.response.text}"}
    except httpx.RequestError as exc:
        return {"success": False, "error": f"Network error: {exc}"}

    errors = data.get("errors", [])
    accounts = []
    for acct in data.get("accounts", []):
        accounts.append({
            "id": acct.get("id"),
            "name": acct.get("name"),
            "org": acct.get("org", {}).get("name"),
            "currency": acct.get("currency"),
            "balance": acct.get("balance"),
            "available_balance": acct.get("available-balance"),
            "balance_date": acct.get("balance-date"),
        })

    result = {"success": True, "accounts": accounts}
    if errors:
        result["errors"] = errors
    return result


@mcp.tool(description=(
    "Get transactions for a specific account within a date range. "
    "Dates should be in YYYY-MM-DD format. The API supports roughly 60-day "
    "ranges. Returns transactions sorted most-recent-first."
))
async def get_transactions(
    account_id: str,
    start_date: str,
    end_date: str,
    include_pending: bool = True,
) -> dict:
    """Retrieve transactions for a given account and date range."""
    try:
        start_ts = _date_to_unix(start_date)
    except ValueError:
        return {"success": False, "error": f"Invalid start_date format: {start_date}. Use YYYY-MM-DD."}

    try:
        end_ts = _date_to_unix(end_date)
    except ValueError:
        return {"success": False, "error": f"Invalid end_date format: {end_date}. Use YYYY-MM-DD."}

    params = {
        "account": account_id,
        "start-date": str(start_ts),
        "end-date": str(end_ts),
        "pending": "1" if include_pending else "0",
    }

    try:
        data = await _simplefin_get("/accounts", params=params)
    except ValueError as exc:
        return {"success": False, "error": str(exc)}
    except httpx.HTTPStatusError as exc:
        return {"success": False, "error": f"HTTP {exc.response.status_code}: {exc.response.text}"}
    except httpx.RequestError as exc:
        return {"success": False, "error": f"Network error: {exc}"}

    errors = data.get("errors", [])

    # Find the matching account in the response
    target_account = None
    for acct in data.get("accounts", []):
        if acct.get("id") == account_id:
            target_account = acct
            break

    if target_account is None:
        return {
            "success": False,
            "error": f"Account {account_id} not found in response. Verify the account ID with get_accounts.",
        }

    transactions = []
    for txn in target_account.get("transactions", []):
        transactions.append({
            "id": txn.get("id"),
            "posted": txn.get("posted"),
            "amount": txn.get("amount"),
            "description": txn.get("description"),
            "payee": txn.get("payee"),
            "memo": txn.get("memo"),
            "pending": txn.get("pending"),
            "transacted_at": txn.get("transacted_at"),
        })

    # Sort most-recent-first by posted date
    transactions.sort(key=lambda t: t.get("posted") or 0, reverse=True)

    result = {
        "success": True,
        "account_id": account_id,
        "account_name": target_account.get("name"),
        "start_date": start_date,
        "end_date": end_date,
        "transaction_count": len(transactions),
        "transactions": transactions,
    }
    if errors:
        result["errors"] = errors
    return result


@mcp.tool(description=(
    "Calculate total net worth across all connected accounts. "
    "Sums balances grouped by currency. Useful for a quick financial overview."
))
async def get_net_worth() -> dict:
    """Sum balances across all accounts, grouped by currency."""
    try:
        data = await _simplefin_get("/accounts", params={"balances-only": "1"})
    except ValueError as exc:
        return {"success": False, "error": str(exc)}
    except httpx.HTTPStatusError as exc:
        return {"success": False, "error": f"HTTP {exc.response.status_code}: {exc.response.text}"}
    except httpx.RequestError as exc:
        return {"success": False, "error": f"Network error: {exc}"}

    errors = data.get("errors", [])
    totals: dict[str, float] = {}
    accounts = []

    for acct in data.get("accounts", []):
        currency = acct.get("currency", "USD")
        balance = acct.get("balance")
        if balance is not None:
            balance = float(balance)
            totals[currency] = totals.get(currency, 0.0) + balance
            accounts.append({
                "name": acct.get("name"),
                "org": acct.get("org", {}).get("name"),
                "currency": currency,
                "balance": balance,
            })

    # Round totals to 2 decimal places
    net_worth = {cur: round(val, 2) for cur, val in totals.items()}

    result = {"success": True, "net_worth": net_worth, "accounts": accounts}
    if errors:
        result["errors"] = errors
    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"

    print(f"Starting SimpleFIN MCP server on {host}:{port}")

    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True,
    )
