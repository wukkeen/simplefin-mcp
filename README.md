# SimpleFIN MCP Server

An MCP server that connects to [SimpleFIN](https://simplefin.org) to provide financial account data — balances, transactions, and net worth — to AI agents via the [Model Context Protocol](https://modelcontextprotocol.io).

Built with [FastMCP](https://github.com/jlowin/fastmcp) (Python) and deployed as a stateless HTTP service.
Hell yes i used claude

## Setup

### 1. SimpleFIN Account

1. Create a SimpleFIN account at [simplefin.org](https://simplefin.org) and connect your bank
2. Generate a **setup token** from the SimpleFIN dashboard

### 2. Install & Run

```bash
git clone <your-repo-url>
cd simplefin-mcp
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/server.py
```

The server listens on `0.0.0.0:8000` by default. The MCP endpoint is at `/mcp`.

### 3. Claim Your Setup Token

Use the `claim_setup_token` tool (via MCP Inspector or your MCP client) to exchange the setup token for an **access URL**. Then set it as an environment variable:

```bash
export SIMPLEFIN_ACCESS_URL="https://user:pass@host/simplefin"
```

Restart the server — the other tools will now authenticate against the SimpleFIN API.

### 4. Connect an MCP Client

Point your MCP client at the server URL with the `/mcp` path suffix (e.g. `http://localhost:8000/mcp`). Use "Streamable HTTP" transport.

## Tools

| Tool | Description |
|------|-------------|
| `claim_setup_token` | One-time setup — claims a SimpleFIN setup token and returns the access URL |
| `get_accounts` | Lists all connected accounts with current balances |
| `get_transactions` | Fetches transactions for an account within a date range (~60 day max) |
| `get_net_worth` | Calculates total net worth across all accounts by currency |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server listen port |
| `ENVIRONMENT` | `development` | Deployment environment |
| `SIMPLEFIN_ACCESS_URL` | — | SimpleFIN credentials (`https://user:pass@host/simplefin`). Obtained via `claim_setup_token`. |

## Deployment (Render)

A `render.yaml` is included for deploying to [Render](https://render.com).

1. Create a new Web Service on Render and connect your GitLab repository
2. Render will detect the `render.yaml` configuration automatically
3. Set `SIMPLEFIN_ACCESS_URL` as a secret environment variable in the Render dashboard

Your server will be available at `https://your-service-name.onrender.com/mcp`.

## Local Testing

```bash
npx @modelcontextprotocol/inspector
```

Open the Inspector UI and connect to `http://localhost:8000/mcp` using "Streamable HTTP" transport.

## License

MIT
