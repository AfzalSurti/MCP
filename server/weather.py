from typing import Any # for type hints
import httpx # for HTTP requests
from mcp.server.fastmcp import FastMCP # for MCP server

mcp=FastMCP("weather")

NWS_API_BASE="https://api.weather.gov" # National Weather Service API base URL
USER_AGENT="weather-api/1.0" # User agent for HTTP requests 

async def make_nws_request(url:str)->dict[str,Any] | None:
    """Make a request to the NWS API and return the response"""
    headers={
        "User-Agent":USER_AGENT,
        "accept":"application/geo+json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response=await client.get(url,headers=headers,timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return None # Return None if the request fails


def format_alert(feature:dict)->str: # Format an alert feature as a string
    """Format an alert feature as a string"""
    props=feature["properties"]
    return f"""
        Event: {props.get("event","Unknown")}
        Area: {props.get("areaDesc","Unknown")}
        Severity:{props.get("severity","Unknown")}
        Description: {props.get("description","no description available")}
        Instructions: {props.get("instruction","no instructions available")}
        """

@mcp.tool()
async def get_alerts(state: str)->str:
    """Get the weather alerts for a US state
    
    Args:
        state: two-letter US state code (e.g. "CA" for California)
    Returns:
        A string with the weather alerts for the state, or "No alerts found" if no alerts are found
    """

    url=f"{NWS_API_BASE}/alerts/active/area/{state}"
    data=await make_nws_request(url)

    if not data or "features" not in data:
        return "No alerts found"

    if not data["features"]:
        return "no active alerts found"

    alerts=[format_alert(feature) for feature in data["features"]]
    return "\n\n".join(alerts)  