# MCP Server + Foundry Agent: Football Statistics

A complete tutorial showing how to build a custom **MCP (Model Context Protocol) server** on **Azure Functions** and connect it to a **Microsoft Foundry Agent** powered by GPT-5-mini.

## What You'll Build

- **MCP Server** (Azure Functions) with 3 tools: search players, get stats, compare players
- **Foundry Agent** that uses the MCP server to answer football statistics questions
- In-memory database of 8 top football players with detailed season stats

## Project Structure

```
├── mcp-server/              # Azure Functions MCP server
│   ├── function_app.py      # MCP tools: search, stats, compare
│   ├── host.json            # Extension bundle config (Preview)
│   └── requirements.txt     # azure-functions==1.25.0b3
├── agent/                   # Foundry Agent client
│   ├── create_agent.py      # Create agent + run test conversation
│   └── requirements.txt     # azure-ai-projects>=2.0.0
└── docs/                    # Tutorial blog article
    └── index.html           # Full HTML tutorial
```

## Quick Start

### 1. Deploy the MCP Server

```bash
cd mcp-server
func azure functionapp publish <your-function-app> --python
```

### 2. Get the MCP System Key

```bash
az functionapp keys list -n <your-function-app> -g <your-rg> --query systemKeys.mcp_extension -o tsv
```

### 3. Run the Agent

```bash
cd agent
pip install -r requirements.txt

export FOUNDRY_ENDPOINT="https://<resource>.services.ai.azure.com/api/projects/<project>"
export MCP_SERVER_URL="https://<function-app>.azurewebsites.net/runtime/webhooks/mcp"
export MCP_SERVER_KEY="<your-mcp-system-key>"

python create_agent.py
```

## Tutorial

Read the full step-by-step tutorial: **[Building an MCP Server + Foundry Agent](https://maciejrubczynski.github.io/foundry-mcp-football/)**

## Key Technologies

- **Azure Functions** with MCP extension (Preview bundle 4.32.0+)
- **azure-functions 1.25.0b3** (beta, required for `@app.mcp_tool()` decorators)
- **azure-ai-projects v2 SDK** (`MCPTool`, `PromptAgentDefinition`, Conversations API)
- **GPT-5-mini** via Microsoft Foundry
- **MCP (Model Context Protocol)** — Streamable HTTP transport

## License

MIT
