# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An MCP (Model Context Protocol) server that connects to SimpleFIN to provide financial account data. Built with FastMCP (Python) and httpx for stateless HTTP deployment. Exposes tools for account balances, transactions, and net worth calculation.

## Commands

```bash
# Setup environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run server (listens on 0.0.0.0:8000)
python src/server.py

# Test locally with MCP Inspector (connect to http://localhost:8000/mcp)
npx @modelcontextprotocol/inspector
```

There is no linting or test framework configured.

## Architecture

Single-file server at `src/server.py`. The FastMCP instance exposes tools over stateless HTTP transport at the `/mcp` endpoint (not root `/`). Tools are async Python functions decorated with `@mcp.tool`.

**Key configuration:** `stateless_http=True` is required for the HTTP transport to work correctly — removing it causes 400 errors.

**Environment variables:**
- `PORT` (default 8000) — server listen port
- `ENVIRONMENT` (default "development") — deployment environment
- `SIMPLEFIN_ACCESS_URL` — SimpleFIN credentials in `https://user:pass@host/simplefin` format. Obtained via the `claim_setup_token` tool.

**Deployment:** Render.com via `render.yaml`. The deployed URL must include the `/mcp` path suffix. Set `SIMPLEFIN_ACCESS_URL` as a secret env var in the Render dashboard.

## Tools

- `claim_setup_token(setup_token)` — One-time setup: decodes and claims a SimpleFIN setup token, returns the access URL
- `get_accounts()` — Lists all connected accounts with balances (no transactions)
- `get_transactions(account_id, start_date, end_date, include_pending)` — Fetches transactions for an account within a YYYY-MM-DD date range (~60 day max)
- `get_net_worth()` — Sums balances across all accounts grouped by currency

All tools return `{"success": True/False, ...}` and never raise exceptions to the caller.
