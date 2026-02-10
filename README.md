# SimpleFIN MCP Server

An MCP server that connects to [SimpleFIN](https://simplefin.org) to provide financial account data — balances, transactions, and net worth — to AI agents via the [Model Context Protocol](https://modelcontextprotocol.io).

## Why?
Rocketmoney is hella expensive, and was my original subscription before I learned about https://actualbudget.org/. But even then I'm way too lazy for that and we know LLMs are basically only good at data analysis, so this was made to provide quick insights I actually want to know about instead of one giant excel sheet. SimpleFin bridge itself is only $1.50/month which somehow costs about as much as the pikapod that is advertised to run it.

Built with [FastMCP](https://github.com/jlowin/fastmcp) (Python) and deployed as a stateless HTTP service.
Hell yes i used claude

## Setup

### 1. SimpleFIN Account

1. Create a SimpleFIN account at [simplefin.org](https://simplefin.org) and connect your banks.
2. Generate a **setup token** from the SimpleFIN dashboard, you will need to provide it to whatever is using the MCP.

### 2. Install & Run

First clone this repo and cd into it.
   
```bash
cd simplefin-mcp
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 src/server.py
```

The server listens on `0.0.0.0:8000` by default. The MCP endpoint is at `/mcp`. If you wanna change it just change the port line in 'src/server.py'

### 3. Claim Your Setup Token

Use the `claim_setup_token` tool (via MCP Inspector or your MCP client or Poke) to exchange the setup token for an **access URL**. With Poke you can just ask it and it will guide you through getting the token. Then set it as an environment variable:

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

## EC2
The regular instructions were made with this in mind since it was my use case, and plain linux server t2.micro server handles it great with minimal cost.

## Local Testing

```bash
npx @modelcontextprotocol/inspector
```

Open the Inspector UI and connect to `http://localhost:8000/mcp` using "Streamable HTTP" transport.

## License

MIT
