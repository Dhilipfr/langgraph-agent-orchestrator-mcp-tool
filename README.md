# Agent Orchestration System

This project implements an agent orchestration system using LangGraph and the Model Context Protocol (MCP). It coordinates specialized agents for team management and engagement information through a supervisor that delegates tasks and integrates responses.

## Project Structure

```
.
├── .env                      # Environment variables (OpenAI API key)
├── pyproject.toml            # Python project configuration
├── uv.lock                   # Dependency lock file for uv package manager
├── langgraph/                # LangGraph implementation
│   └── agent_orchestration.py # Main orchestration logic
└── mcp_servers/              # Model Context Protocol servers
    ├── engagement_mcp.py     # MCP server for engagement information
    └── team_management_mcp.py # MCP server for team management
```

## Setup Instructions

1. **Create and activate a virtual environment**:
   ```bash
   uv virtualenv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Run the application**:
   ```bash
   python langgraph/agent_orchestration.py
   ```

4. **Verify Python installation path** (if needed):
   ```bash
   (Get-Command python).path -replace '\\','/'
   ```

5. **Inspect MCP servers** (optional):
   ```bash
   npx @modelcontextprotocol/inspector
   ```

## How It Works

This project demonstrates the orchestration of multiple AI agents using LangGraph and the Model Context Protocol:

1. **MCP Servers**: Two specialized MCP servers handle different domains:
   - `engagement_mcp.py`: Provides information about client engagements and projects
   - `team_management_mcp.py`: Manages team member information

2. **Agent Orchestration**: The `agent_orchestration.py` file:
   - Creates specialized agents with appropriate tools from each MCP server
   - Sets up a supervisor agent that coordinates between the specialized agents
   - Presents a Gradio UI for user interaction

3. **Workflow**:
   - User submits a query through the Gradio interface
   - The supervisor agent breaks down the query into subtasks
   - Specialized agents use their tools to gather information
   - The supervisor integrates the responses into a cohesive answer

## Example Queries

- "List out the component engagements of a specific group 'Office USA' along with the team members"
- "What team members are assigned to the Chennai engagement?"
- "Show me all engagements in India and their respective team leads"

## Technologies Used

- **LangGraph**: Framework for building stateful, multi-agent workflows
- **Model Context Protocol (MCP)**: Protocol for standardized interaction with language models
- **Gradio**: Web interface for AI applications
- **OpenAI**: GPT models for agent intelligence
- **UV**: Fast Python package installer and resolver

## Requirements

- Python 3.10+
- OpenAI API key (configured in .env file)
