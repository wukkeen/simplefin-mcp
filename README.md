# SimpleFIN MCP Server

An MCP server that connects to [SimpleFIN](https://simplefin.org) to provide financial account data — balances, transactions, and net worth — to AI agents via the [Model Context Protocol](https://modelcontextprotocol.io).

Well yes i used claude and codex.

## Why?
Rocketmoney is hella expensive, and was my original subscription before I learned about https://actualbudget.org/. But even then I'm way too lazy for that and we know LLMs are basically only good at data analysis, so this was made to provide quick insights I actually want to know about instead of one giant excel sheet. SimpleFin bridge itself is only $1.50/month which somehow costs about as much as the pikapod that is advertised to run it.

Built with [FastMCP](https://github.com/jlowin/fastmcp) (Python) and deployed as a stateless HTTP service.

## Setup

### EC2 / Really any Linux VM (recommended and essentially free with given credits)

1. Create a SimpleFIN account at [simplefin.org](https://simplefin.org), connect your banks, and generate a **setup token**.
2. Self-host or provision a small Linux VM (EC2 works great, it's what this was made for). Open the port you plan to use (default `8000`) or put it behind a reverse proxy.
3. SSH into the server and install:

```bash
git clone https://github.com/joaqu/simplefin-mcp.git
cd simplefin-mcp
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

4. Set your environment variables in `.env` (example below). The API key is required.

```bash
ENVIRONMENT=production
PORT=8000
SIMPLEFIN_MCP_API_KEY=your-strong-random-token
SIMPLEFIN_ACCESS_URL=https://user:pass@host/simplefin [get this from your agent]
```

5. Use the `claim_setup_token` tool (via MCP Inspector or your MCP client or Poke) to exchange the setup token for an **access URL**, then paste it into `SIMPLEFIN_ACCESS_URL`.
6. Start the server:

```bash
python3 src/server.py
```

The server listens on `0.0.0.0:$PORT`. Change the port in your '.env'. The MCP endpoint is at `/mcp`.

### Connect an MCP Client

Point your MCP client at the server URL with the `/mcp` path suffix (e.g. `http://your-server:8000/mcp`). Use "Streamable HTTP" transport and include the bearer header:

```
Authorization: Bearer <SIMPLEFIN_MCP_API_KEY>
```
In poke and many other agent's this is the API key field.

## Tools

| Tool | Description |
|------|-------------|
| `claim_setup_token` | One-time setup — claims a SimpleFIN setup token and returns the access URL |
| `get_accounts` | Lists all connected accounts with current balances |
| `get_transactions` | Fetches transactions for an account within a date range (~60 day max) |
| `get_net_worth` | Calculates total net worth across all accounts by currency |

## Resources

| Resource URI | Description |
|--------------|-------------|
| `resource://simplefin/usage` | Usage guide and privacy notes for this MCP server |

## Tool-Only Access

This server exposes resources as tools for clients that do not support MCP resources.
Use the following tools:

- `list_resources` returns available resource metadata.
- `read_resource` returns the resource content by URI.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | — | Server listen port (required). Render sets this automatically. |
| `ENVIRONMENT` | `development` | Deployment environment |
| `SIMPLEFIN_ACCESS_URL` | — | SimpleFIN credentials (`https://user:pass@host/simplefin`). Obtained via `claim_setup_token`. |
| `SIMPLEFIN_MCP_API_KEY` | — | Bearer token required for MCP requests. |

The server reads environment variables from a local `.env` file if present. (Recommended)

## Deployment (Render, optional)

If you prefer a managed deploy instead of running your own VM, a `render.yaml` is included for deploying to [Render](https://render.com).

1. Create a new Web Service on Render and connect your repository
2. Render will detect the `render.yaml` configuration automatically
3. Set `SIMPLEFIN_ACCESS_URL` as a secret environment variable in the Render dashboard
4. Set `SIMPLEFIN_MCP_API_KEY` as a secret environment variable in the Render dashboard

Your server will be available at `https://your-service-name.onrender.com/mcp`.

## Local Testing

```bash
npx @modelcontextprotocol/inspector
```

Open the Inspector UI and connect to `http://localhost:8000/mcp` using "Streamable HTTP" transport.
Set the `Authorization: Bearer <SIMPLEFIN_MCP_API_KEY>` header in the Inspector connection settings.

## License

MIT
