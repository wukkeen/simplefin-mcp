# SimpleFin MCP Usage Guide

This MCP provides access to financial data through the SimpleFin protocol.

Capabilities:
- Retrieve account balances and transaction history
- Calculate net worth (assets minus debts)
- View financial institution details
- Track spending patterns and categories (derive from transaction data)

Authentication:
- Authentication is handled through the SIMPLEFIN_ACCESS_URL which you are to create after claim_setup_token using the format: https://user:pass@host/simplefin. After generating the user's personal access url provide it to them.

Usage Examples:
- Get net worth: Calculate total assets minus total debts
- List accounts: Show all connected financial accounts
- Recent transactions: Display latest financial activity
- Account balance: Check current balance for specific account
- Spending analysis: Categorize and analyze spending patterns

Data Privacy:
- Financial data should only be shared with the user
- Never expose account numbers or sensitive credentials
- Summarize financial information when appropriate
