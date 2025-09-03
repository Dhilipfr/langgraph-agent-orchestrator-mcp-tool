import asyncio
import gradio as gr
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent

load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

ROOT_FOLDER = Path(__file__).parent.parent.absolute()
ENGAGEMENT_MCP_PATH = 'D:/Project/python/mcp_servers/engagement_mcp.py'
TEAM_MANAGEMENT_MCP_PATH = 'D:/Project/python/mcp_servers/team_management_mcp.py'   
mcp_config = {
    "engagement": {
        "command": "python",
        "args": [ENGAGEMENT_MCP_PATH],
        "transport": "stdio",
    },
    "team_management": {
        "command": "python",
        "args": [TEAM_MANAGEMENT_MCP_PATH],
        "transport": "stdio",
    }
}

ENGAGEMENT_SYSTEM_PROMPT = """You are a specialized agent focused on engagement information.
Your job is to provide detailed information about client engagements, projects, and their components.
Use the provided tools to look up engagement details, project structures, and engagement hierarchies.
Focus only on engagement-related information and be thorough in your responses."""

TEAM_MANAGEMENT_SYSTEM_PROMPT = """You are a specialized agent focused on team management information.
Your job is to provide detailed information about teams, team members, and their roles.
Use the provided tools to look up team compositions, member details, and organizational structures.
Focus only on team-related information and be thorough in your responses."""

SUPERVISOR_SYSTEM_PROMPT = """You are a supervisor agent responsible for coordinating specialized agents.
You have access to two specialized agents:
1. Engagement Agent: Expert in engagement information, projects, and their components
2. Team Management Agent: Expert in teams, team members, and organizational structures

Your job is to:
1. Break down user queries into sub-tasks for the appropriate specialized agents
2. Determine which agent should handle which part of the query
3. Integrate responses from specialized agents into a cohesive, comprehensive answer
4. Ensure all parts of the user's question are addressed

Be efficient in your delegation and thorough in your final response."""

user_query = "List out the component engagements of a specific group 'Office USA' along with the team members"
    

async def invoke_agent_orchestration(user_input: str) -> Any:
    print('Method invoked with query:', user_input)
    user_query = user_input
    client = MultiServerMCPClient(mcp_config)
    
    agents = {}
    
    async with client.session("engagement") as engagement_session:
        print('Engagement Session created')
        await engagement_session.initialize()
        engagement_tools = await client.get_tools(server_name="engagement")
        
        print("=== Engagement MCP Server Tools Loaded ===")
        for tool in engagement_tools:
            print(f"Tool: {tool.name} - {tool.description}")    
            
        engagement_agent = create_react_agent(
            name="EngagementAgent",
            model=model,
            tools=engagement_tools,
            prompt=SystemMessage(content=ENGAGEMENT_SYSTEM_PROMPT)
        )
        # print("=== Testing Engagement Agent direct execution ===")
        # eng_response = await engagement_agent.ainvoke({"messages": [user_query]})
        # print(eng_response["messages"][-1].content)
        agents["engagement"] = engagement_agent
    
    async with client.session("team_management") as team_management_session:
        print('Team Management Session created')
        await team_management_session.initialize()
        team_management_tools = await client.get_tools(server_name="team_management") 
        print("=== Team Management MCP Server Tools Loaded ===")
        for tool in team_management_tools:
            print(f"Tool: {tool.name} - {tool.description}")
        team_management_agent = create_react_agent(
            name="TeamManagementAgent",
            model=model,
            tools=team_management_tools,
            prompt=SystemMessage(content=TEAM_MANAGEMENT_SYSTEM_PROMPT)
        )
        agents["team_management"] = team_management_agent
    
    workflow = create_supervisor(
        [agents["engagement"], agents["team_management"]],
        model = model,
        prompt=SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT)
    )

    print("\n=== Invoking Supervisor Agent ===")
    app = workflow.compile()
    config = {"recursion_limit": 50, "configurable": {"thread_id": "123"}}
    
    result = await app.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_query
                }
            ]
        },
        config=config 
    )
    return result

def format_response(response_dict):
    """Format the response messages for better readability."""
    formatted_output = []
    
    for i, message in enumerate(response_dict.get('messages', [])):
        if hasattr(message, 'content') and message.content:
            role = getattr(message, 'name', None) or message.__class__.__name__
            formatted_output.append(f"[{role}]: {message.content}")
    
    return "\n\n".join(formatted_output)

def process_query(query):
    """Process the user query and return the formatted response."""
    if not query.strip():
        return "Please enter a query."
    
    try:
        response = asyncio.run(invoke_agent_orchestration(query))
        return format_response(response)
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
# Gradio interface
def create_gradio_interface():
    with gr.Blocks(title="Agent Orchestration System") as demo:
        gr.Markdown("# Agent Orchestration System")
        gr.Markdown("Ask questions about engagements and team management")
        
        with gr.Row():
            with gr.Column():
                query_input = gr.Textbox(
                    label="Your Query",
                    placeholder="e.g., List out the component engagements of a specific group 'office USA' along with the team members",
                    lines=3
                )
                submit_btn = gr.Button("Submit")
            
        with gr.Row():
            output = gr.Textbox(label="Response", lines=10)
            
        submit_btn.click(fn=process_query, inputs=query_input, outputs=output)
        
    return demo

if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch(share=False)
    # response = asyncio.run(invoke_agent_orchestration())
    # print("\n=== Final Response ===")
    # print(format_response(response))