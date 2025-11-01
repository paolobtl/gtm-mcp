"""MCP server for Google Tag Manager."""
import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from dotenv import load_dotenv

from .gtm_client import GTMClient
from .tools import GTMTools

# Load environment variables
load_dotenv()

class GTMMCPServer:
    """MCP Server for Google Tag Manager operations."""
    
    def __init__(self):
        self.server = Server("gtm-mcp")
        self.gtm_client = None
        self.tools = GTMTools()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Return list of available GTM tools."""
            return [
                Tool(
                    name="gtm_list_accounts",
                    description="List all accessible GTM accounts",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="gtm_list_containers",
                    description="List all containers in a GTM account",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "account_id": {
                                "type": "string",
                                "description": "GTM Account ID"
                            }
                        },
                        "required": ["account_id"]
                    }
                ),
                Tool(
                    name="gtm_list_tags",
                    description="List all tags in a container workspace",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "container_path": {
                                "type": "string",
                                "description": "Full container path (e.g., accounts/123/containers/456)"
                            },
                            "workspace_id": {
                                "type": "string",
                                "description": "Workspace ID (optional, uses default if not provided)"
                            }
                        },
                        "required": ["container_path"]
                    }
                ),
                Tool(
                    name="gtm_get_tag",
                    description="Get detailed configuration of a specific tag",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tag_path": {
                                "type": "string",
                                "description": "Full tag path (e.g., accounts/123/containers/456/workspaces/7/tags/8)"
                            }
                        },
                        "required": ["tag_path"]
                    }
                ),
                Tool(
                    name="gtm_create_tag",
                    description="Create a new tag in a GTM container",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_path": {
                                "type": "string",
                                "description": "Full workspace path"
                            },
                            "tag_name": {
                                "type": "string",
                                "description": "Name for the new tag"
                            },
                            "tag_type": {
                                "type": "string",
                                "description": "Type of tag (e.g., 'ua', 'ga4', 'html')"
                            },
                            "tag_config": {
                                "type": "object",
                                "description": "Tag configuration parameters"
                            },
                            "firing_trigger_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of trigger IDs that should fire this tag"
                            }
                        },
                        "required": ["workspace_path", "tag_name", "tag_type"]
                    }
                ),
                Tool(
                    name="gtm_update_tag",
                    description="Update an existing tag in a GTM container",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tag_path": {
                                "type": "string",
                                "description": "Full tag path (e.g., accounts/123/containers/456/workspaces/7/tags/8)"
                            },
                            "tag_data": {
                                "type": "object",
                                "description": "Complete tag data object to update"
                            }
                        },
                        "required": ["tag_path", "tag_data"]
                    }
                ),
                Tool(
                    name="gtm_list_triggers",
                    description="List all triggers in a container workspace",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_path": {
                                "type": "string",
                                "description": "Full workspace path"
                            }
                        },
                        "required": ["workspace_path"]
                    }
                ),
                Tool(
                    name="gtm_create_trigger",
                    description="Create a new trigger in a GTM container",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_path": {
                                "type": "string",
                                "description": "Full workspace path"
                            },
                            "trigger_name": {
                                "type": "string",
                                "description": "Name for the new trigger"
                            },
                            "trigger_type": {
                                "type": "string",
                                "description": "Type of trigger",
                                "enum": [
                                    "pageview", "domReady", "windowLoaded", "customEvent",
                                    "triggerGroup", "init", "consentInit", "serverPageview",
                                    "always", "firebaseAppException", "firebaseAppUpdate",
                                    "firebaseCampaign", "firebaseFirstOpen", "firebaseInAppPurchase",
                                    "firebaseNotificationDismiss", "firebaseNotificationForeground",
                                    "firebaseNotificationOpen", "firebaseNotificationReceive",
                                    "firebaseOsUpdate", "firebaseSessionStart", "firebaseUserEngagement",
                                    "formSubmission", "click", "linkClick", "jsError",
                                    "historyChange", "timer", "ampClick", "ampTimer",
                                    "ampScroll", "ampVisibility", "youTubeVideo",
                                    "scrollDepth", "elementVisibility"
                                ]
                            },
                            "trigger_config": {
                                "type": "object",
                                "description": "Trigger configuration parameters"
                            }
                        },
                        "required": ["workspace_path", "trigger_name", "trigger_type"]
                    }
                ),
                Tool(
                    name="gtm_list_variables",
                    description="List all variables in a container workspace",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_path": {
                                "type": "string",
                                "description": "Full workspace path"
                            }
                        },
                        "required": ["workspace_path"]
                    }
                ),
                Tool(
                    name="gtm_get_variable",
                    description="Get detailed configuration of a specific variable",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "variable_path": {
                                "type": "string",
                                "description": "Full variable path (e.g., accounts/123/containers/456/workspaces/7/variables/8)"
                            }
                        },
                        "required": ["variable_path"]
                    }
                ),
                Tool(
                    name="gtm_create_variable",
                    description="Create a new variable in a GTM container",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_path": {
                                "type": "string",
                                "description": "Full workspace path"
                            },
                            "variable_name": {
                                "type": "string",
                                "description": "Name for the new variable"
                            },
                            "variable_type": {
                                "type": "string",
                                "description": "Type of variable. Common types: 'c' (constant), 'v' (data layer variable), 'jsm' (javascript variable), 'u' (URL variable), 'k' (cookie)"
                            },
                            "variable_config": {
                                "type": "object",
                                "description": "Variable configuration. For constant: {value: 'string'}, for data layer: {data_layer_name: 'name'}, for cookie: {cookie_name: 'name'}, etc."
                            }
                        },
                        "required": ["workspace_path", "variable_name", "variable_type"]
                    }
                ),
                Tool(
                    name="gtm_publish_container",
                    description="Create and publish a new version of a GTM container",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_path": {
                                "type": "string",
                                "description": "Full workspace path"
                            },
                            "version_name": {
                                "type": "string",
                                "description": "Name for the new version"
                            },
                            "version_notes": {
                                "type": "string",
                                "description": "Notes describing changes in this version"
                            }
                        },
                        "required": ["workspace_path", "version_name"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[TextContent]:
            """Handle tool execution."""
            if not self.gtm_client:
                self.gtm_client = GTMClient()
            
            try:
                result = await self.tools.execute_tool(name, arguments, self.gtm_client)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error executing tool: {str(e)}")]
    
async def main():
    """Main entry point."""
    server_instance = GTMMCPServer()

    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            server_instance.server.create_initialization_options()
        )

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()