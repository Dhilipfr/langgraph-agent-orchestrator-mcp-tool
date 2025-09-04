from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("IT Staff Management MCP")

@mcp.tool()
def get_available_staff(specialty: str = None) -> Any:
    """
    Get currently available IT staff, optionally filtered by specialty
    
    Args:
        specialty (str, optional): Filter by technical specialty (Network, Security, DevOps, etc.)
        
    Returns:
        Any: List of available staff with their details
    """
    print(f"Finding available staff with specialty: {specialty if specialty else 'Any'}")
    
    staff = [
        {"name": "Alice Chen", "specialty": "Network", "status": "Available", "location": "US East"},
        {"name": "Bob Smith", "specialty": "Security", "status": "Available", "location": "US West"},
        {"name": "Charlie Kumar", "specialty": "DevOps", "status": "On Call", "location": "India"},
        {"name": "Diana Lopez", "specialty": "Database", "status": "Available", "location": "US East"},
        {"name": "Ethan Park", "specialty": "Network", "status": "On Call", "location": "US West"},
        {"name": "Fiona Williams", "specialty": "Security", "status": "Off Duty", "location": "US East"},
        {"name": "George Thompson", "specialty": "Database", "status": "Off Duty", "location": "US West"},
        {"name": "Hannah Lee", "specialty": "Email", "status": "Available", "location": "US East"},
        {"name": "Ian Rodriguez", "specialty": "VPN", "status": "Available", "location": "India"}
    ]
    
    if specialty:
        return [person for person in staff if person["specialty"].lower() == specialty.lower()]
    return [person for person in staff if person["status"].lower() in ["available", "on call"]]

@mcp.tool()
def get_on_call_rotation() -> Any:
    """
    Get the current and upcoming on-call rotation schedule
    
    Returns:
        Any: On-call rotation details
    """
    print("Retrieving on-call rotation schedule")
    
    return {
        "current": {
            "primary": "Charlie Kumar (DevOps)",
            "secondary": "Ethan Park (Network)",
            "period": "May 15-21, 2023"
        },
        "upcoming": [
            {
                "primary": "Fiona Williams (Security)",
                "secondary": "Alice Chen (Network)",
                "period": "May 22-28, 2023"
            },
            {
                "primary": "Bob Smith (Security)",
                "secondary": "George Thompson (Database)",
                "period": "May 29-June 4, 2023"
            }
        ]
    }

@mcp.tool()
def get_staff_by_location(location: str) -> Any:
    """
    Get IT staff filtered by their location
    
    Args:
        location (str): Location to filter by (US East, US West, India, etc.)
        
    Returns:
        Any: List of staff at the specified location
    """
    print(f"Finding staff at location: {location}")
    
    staff = [
        {"name": "Alice Chen", "specialty": "Network", "status": "Available", "location": "US East"},
        {"name": "Bob Smith", "specialty": "Security", "status": "Available", "location": "US West"},
        {"name": "Charlie Kumar", "specialty": "DevOps", "status": "On Call", "location": "India"},
        {"name": "Diana Lopez", "specialty": "Database", "status": "Available", "location": "US East"},
        {"name": "Ethan Park", "specialty": "Network", "status": "On Call", "location": "US West"},
        {"name": "Fiona Williams", "specialty": "Security", "status": "Off Duty", "location": "US East"},
        {"name": "George Thompson", "specialty": "Database", "status": "Off Duty", "location": "US West"},
        {"name": "Hannah Lee", "specialty": "Email", "status": "Available", "location": "US East"},
        {"name": "Ian Rodriguez", "specialty": "VPN", "status": "Available", "location": "India"}
    ]
    
    return [person for person in staff if person["location"].lower() == location.lower()]

if __name__ == "__main__":
    print("Starting IT Staff Management MCP")
    mcp.run(transport="stdio")
