from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Service Desk MCP")

@mcp.tool()
def get_active_tickets(priority: str = None) -> Any:
    """
    Get active tickets in the system, optionally filtered by priority
    
    Args:
        priority (str, optional): Filter by priority (Critical, High, Medium, Low)
        
    Returns:
        Any: List of active tickets with details
    """
    print(f"Getting active tickets with priority: {priority if priority else 'All'}")
    
    tickets = [
        {"id": "INC-001", "title": "Network outage in US East DC", "priority": "Critical", "status": "In Progress", "affected_system": "Network"},
        {"id": "INC-002", "title": "Email service degradation", "priority": "High", "status": "Under Investigation", "affected_system": "Email"},
        {"id": "INC-003", "title": "VPN access issues", "priority": "Medium", "status": "Assigned", "affected_system": "VPN"},
        {"id": "REQ-001", "title": "New laptop setup", "priority": "Low", "status": "Pending", "affected_system": "Hardware"}
    ]
    
    if priority:
        return [ticket for ticket in tickets if ticket["priority"].lower() == priority.lower()]
    return tickets

@mcp.tool()
def get_system_status(system_name: str = None) -> Any:
    """
    Get current status of IT systems
    
    Args:
        system_name (str, optional): Name of specific system to check
        
    Returns:
        Any: System status information
    """
    print(f"Checking system status for: {system_name if system_name else 'All systems'}")
    
    systems = {
        "CRM": {"status": "Operational", "uptime": "99.98%", "last_incident": "15 days ago"},
        "Email": {"status": "Degraded", "uptime": "97.5%", "last_incident": "2 hours ago"},
        "VPN": {"status": "Disrupted", "uptime": "85.2%", "last_incident": "4 hours ago"},
        "ERP": {"status": "Operational", "uptime": "99.99%", "last_incident": "45 days ago"},
        "Network": {"status": "Critical Outage", "uptime": "78.5%", "last_incident": "1 hour ago"}
    }
    
    if system_name and system_name in systems:
        return {system_name: systems[system_name]}
    return systems

if __name__ == "__main__":
    print("Starting Service Desk MCP")
    mcp.run(transport="stdio")
