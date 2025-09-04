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
SERVICE_DESK_MCP_PATH = 'D:/Project/python/mcp_servers/service_desk_mcp.py'
IT_STAFF_MCP_PATH = 'D:/Project/python/mcp_servers/it_staff_mcp.py'   
mcp_config = {
    "service_desk": {
        "command": "python",
        "args": [SERVICE_DESK_MCP_PATH],
        "transport": "stdio",
    },
    "it_staff": {
        "command": "python",
        "args": [IT_STAFF_MCP_PATH],
        "transport": "stdio",
    }
}

SERVICE_DESK_SYSTEM_PROMPT = """You are a specialized agent focused on IT service desk information.
Your job is to provide detailed information about active tickets, system statuses, and IT incidents.
Use the provided tools to look up ticket details, system health, and current outages.
Focus only on IT service-related information and be thorough in your responses."""

IT_STAFF_SYSTEM_PROMPT = """You are a specialized agent focused on IT staff management information.
Your job is to provide detailed information about IT personnel availability, specialties, and on-call rotations.
Use the provided tools to look up available staff, specialist skills, and current on-call schedules.
Focus only on IT staff-related information and be thorough in your responses."""

SUPERVISOR_SYSTEM_PROMPT = """You are a supervisor agent responsible for coordinating specialized agents.
You have access to two specialized agents:
1. Service Desk Agent: Expert in IT tickets, system status, and incident information
2. IT Staff Agent: Expert in IT personnel availability, specialties, and on-call rotations

Your job is to:
1. Break down user queries into sub-tasks for the appropriate specialized agents
2. Determine which agent should handle which part of the query
3. Integrate responses from specialized agents into a cohesive, comprehensive answer
4. Ensure all parts of the user's question are addressed

Be efficient in your delegation and thorough in your final response."""

user_query = "What network specialists are available to help with the current critical network outage?"
    

async def invoke_agent_orchestration(user_input: str) -> Any:
    print('Method invoked with query:', user_input)
    user_query = user_input
    client = MultiServerMCPClient(mcp_config)
    
    
    agents = {}
    
    async with client.session("service_desk") as service_desk_session:
        print('Service Desk Session created')
        await service_desk_session.initialize()
        service_desk_tools = await client.get_tools(server_name="service_desk")
        
        print("=== Service Desk MCP Server Tools Loaded ===")
        for tool in service_desk_tools:
            print(f"Tool: {tool.name} - {tool.description}")    
            
        service_desk_agent = create_react_agent(
            name="ServiceDeskAgent",
            model=model,
            tools=service_desk_tools,
            prompt=SystemMessage(content=SERVICE_DESK_SYSTEM_PROMPT)
        )
        agents["service_desk"] = service_desk_agent
    
    async with client.session("it_staff") as it_staff_session:
        print('IT Staff Session created')
        await it_staff_session.initialize()
        it_staff_tools = await client.get_tools(server_name="it_staff") 
        print("=== IT Staff MCP Server Tools Loaded ===")
        for tool in it_staff_tools:
            print(f"Tool: {tool.name} - {tool.description}")
        it_staff_agent = create_react_agent(
            name="ITStaffAgent",
            model=model,
            tools=it_staff_tools,
            prompt=SystemMessage(content=IT_STAFF_SYSTEM_PROMPT)
        )
        agents["it_staff"] = it_staff_agent
    
    workflow = create_supervisor(
        [agents["service_desk"], agents["it_staff"]],
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
    with gr.Blocks(title="IT Service Management System") as demo:
        gr.Markdown("# IT Service Management System")
        gr.Markdown("Ask questions about IT incidents and staff availability")
        
        with gr.Row():
            with gr.Column():
                query_input = gr.Textbox(
                    label="Your Query",
                    placeholder="e.g., What network specialists are available to help with the current critical network outage?",
                    lines=3
                )
                submit_btn = gr.Button("Submit")
            
        with gr.Row():
            output = gr.Textbox(label="Response", lines=10)
            
        # Add example queries
        gr.Examples(
            examples=[
                "What network specialists are available to help with the current critical network outage?",
                "Who is on call this week and what high priority tickets need attention?",
                "Get active tickets prioritized as critical or high.",
                "Check the status of the VPN system.",
                "What active tickets involve the VPN and which staff in India can help?"
            ],
            inputs=query_input,
        )
            
        submit_btn.click(fn=process_query, inputs=query_input, outputs=output)
        
    return demo

if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch(share=False)
    # response = asyncio.run(invoke_agent_orchestration())
    # print("\n=== Final Response ===")
    # print(format_response(response))