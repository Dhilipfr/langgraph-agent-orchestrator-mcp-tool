from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Team Management MCP")


@mcp.tool()
def get_team_members(group_engagement: str) -> Any:
    """
    Get the team members for a specific group

    Args:
        group_engagement (str): The name of the group to get team members for

    Returns:
        Any: The team members for the specified group
    """
    print(f"Getting team members for: {group_engagement}")
    return {"group": group_engagement, "members": ["Dhilip", "John", "Alice", "Bob", "Charlie", "David", "Eve"]}

if __name__ == "__main__":
    print("Starting Team Management MCP")
    mcp.run(transport="stdio")