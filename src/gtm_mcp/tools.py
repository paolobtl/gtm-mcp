"""GTM tool implementations for MCP."""

from typing import Any, Dict, Optional
from .gtm_client import GTMClient


class GTMTools:
    """Container for GTM tool implementations."""

    async def execute_tool(
        self, name: str, arguments: Optional[Dict[str, Any]], client: GTMClient
    ) -> Dict[str, Any]:
        """Execute a tool by name."""
        tool_map = {
            "gtm_list_accounts": self._list_accounts,
            "gtm_list_containers": self._list_containers,
            "gtm_list_tags": self._list_tags,
            "gtm_get_tag": self._get_tag,
            "gtm_create_tag": self._create_tag,
            "gtm_update_tag": self._update_tag,
            "gtm_list_triggers": self._list_triggers,
            "gtm_create_trigger": self._create_trigger,
            "gtm_list_variables": self._list_variables,
            "gtm_get_variable": self._get_variable,
            "gtm_create_variable": self._create_variable,
            "gtm_publish_container": self._publish_container,
        }

        handler = tool_map.get(name)
        if not handler:
            raise ValueError(f"Unknown tool: {name}")

        return await handler(arguments or {}, client)

    async def _list_accounts(
        self, args: Dict[str, Any], client: GTMClient
    ) -> Dict[str, Any]:
        """List GTM accounts."""
        accounts = client.list_accounts()
        return {
            "accounts": [
                {
                    "accountId": acc.get("accountId"),
                    "name": acc.get("name"),
                    "path": acc.get("path"),
                }
                for acc in accounts
            ]
        }

    async def _list_containers(
        self, args: Dict[str, Any], client: GTMClient
    ) -> Dict[str, Any]:
        """List containers in an account."""
        account_id = args["account_id"]
        containers = client.list_containers(account_id)
        return {
            "containers": [
                {
                    "containerId": cont.get("containerId"),
                    "name": cont.get("name"),
                    "path": cont.get("path"),
                    "publicId": cont.get("publicId"),
                }
                for cont in containers
            ]
        }

    async def _list_tags(
        self, args: Dict[str, Any], client: GTMClient
    ) -> Dict[str, Any]:
        """List tags in a workspace."""
        container_path = args["container_path"]
        workspace_id = args.get("workspace_id")

        # Get workspace path
        if not workspace_id:
            workspaces = client.list_workspaces(container_path)
            if workspaces:
                workspace_path = workspaces[0]["path"]  # Use default workspace
            else:
                raise ValueError("No workspaces found in container")
        else:
            workspace_path = f"{container_path}/workspaces/{workspace_id}"

        tags = client.list_tags(workspace_path)
        return {
            "tags": [
                {
                    "tagId": tag.get("tagId"),
                    "name": tag.get("name"),
                    "type": tag.get("type"),
                    "path": tag.get("path"),
                }
                for tag in tags
            ]
        }

    async def _get_tag(self, args: Dict[str, Any], client: GTMClient) -> Dict[str, Any]:
        """Get detailed tag configuration."""
        tag_path = args["tag_path"]
        tag = client.get_tag(tag_path)
        return {"tag": tag}

    async def _create_tag(
        self, args: Dict[str, Any], client: GTMClient
    ) -> Dict[str, Any]:
        """Create a new tag."""
        workspace_path = args["workspace_path"]

        tag_data = {"name": args["tag_name"], "type": args["tag_type"]}

        if "tag_config" in args:
            tag_data["parameter"] = self._build_parameters(args["tag_config"])

        if "firing_trigger_ids" in args:
            tag_data["firingTriggerId"] = args["firing_trigger_ids"]

        result = client.create_tag(workspace_path, tag_data)
        return {
            "success": True,
            "tag": {
                "tagId": result.get("tagId"),
                "name": result.get("name"),
                "path": result.get("path"),
            },
        }

    async def _update_tag(
        self, args: Dict[str, Any], client: GTMClient
    ) -> Dict[str, Any]:
        """Update an existing tag."""
        tag_path = args["tag_path"]
        tag_data = args["tag_data"]

        result = client.update_tag(tag_path, tag_data)
        return {
            "success": True,
            "tag": {
                "tagId": result.get("tagId"),
                "name": result.get("name"),
                "path": result.get("path"),
            },
        }

    async def _list_triggers(
        self, args: Dict[str, Any], client: GTMClient
    ) -> Dict[str, Any]:
        """List triggers in a workspace."""
        workspace_path = args["workspace_path"]
        triggers = client.list_triggers(workspace_path)
        return {
            "triggers": [
                {
                    "triggerId": trigger.get("triggerId"),
                    "name": trigger.get("name"),
                    "type": trigger.get("type"),
                    "path": trigger.get("path"),
                }
                for trigger in triggers
            ]
        }

    async def _create_trigger(
        self, args: Dict[str, Any], client: GTMClient
    ) -> Dict[str, Any]:
        """Create a new trigger."""
        workspace_path = args["workspace_path"]

        trigger_data = {"name": args["trigger_name"], "type": args["trigger_type"]}

        if "trigger_config" in args:
            config = args["trigger_config"]

            # Handle trigger groups with trigger ID references
            if args["trigger_type"] == "triggerGroup" and "trigger_ids" in config:
                trigger_data["parameter"] = [
                    {
                        "type": "list",
                        "key": "triggerIds",
                        "list": [
                            {"type": "triggerReference", "value": str(trigger_id)}
                            for trigger_id in config["trigger_ids"]
                        ],
                    }
                ]

            # If config contains GTM API fields directly, merge them into trigger_data
            # This allows passing complete trigger configurations
            api_fields = [
                "filter",
                "autoEventFilter",
                "customEventFilter",
                "waitForTags",
                "visibilitySelector",
                "visiblePercentageMin",
                "continuousTimeMinMilliseconds",
                "visiblePercentageMax",
                "maxTimerLengthSeconds",
                "checkValidation",
                "waitForTagsTimeout",
                "uniqueTriggerId",
                "horizontalScrollPercentageList",
                "verticalScrollPercentageList",
                "totalTimeMinMilliseconds",
                "interval",
                "intervalSeconds",
                "limit",
                "videoPercentageList",
                "triggerStartDelay",
                "elementId",
                "selector",
                "notes",
                "parameter",
                "eventName",
            ]
            event_types = [
                "eventTypeUnspecified",
                "pageview",
                "domReady",
                "windowLoaded",
                "customEvent",
                "triggerGroup",
                "init",
                "consentInit",
                "serverPageview",
                "always",
                "firebaseAppException",
                "firebaseAppUpdate",
                "firebaseCampaign",
                "firebaseFirstOpen",
                "firebaseInAppPurchase",
                "firebaseNotificationDismiss",
                "firebaseNotificationForeground",
                "firebaseNotificationOpen",
                "firebaseNotificationReceive",
                "firebaseOsUpdate",
                "firebaseSessionStart",
                "firebaseUserEngagement",
                "formSubmission",
                "click",
                "linkClick",
                "jsError",
                "historyChange",
                "timer",
                "ampClick",
                "ampTimer",
                "ampScroll",
                "ampVisibility",
                "youTubeVideo",
                "scrollDepth",
                "elementVisibility",
            ]
            for field in api_fields:
                if field in config:
                    # Don't override parameter if it was already set for trigger groups
                    if (
                        field == "parameter"
                        and args["trigger_type"] == "triggerGroup"
                        and "trigger_ids" in config
                    ):
                        continue
                    trigger_data[field] = config[field]

            # Legacy support for simplified configurations
            if (
                args["trigger_type"] == "customEvent"
                and "event_name" in config
                and "customEventFilter" not in config
            ):
                match_type = config.get("match_type", "equals")
                trigger_data["customEventFilter"] = [
                    {
                        "type": match_type,
                        "parameter": [
                            {"type": "template", "key": "arg0", "value": "{{_event}}"},
                            {
                                "type": "template",
                                "key": "arg1",
                                "value": config["event_name"],
                            },
                        ],
                    }
                ]

        result = client.create_trigger(workspace_path, trigger_data)
        return {
            "success": True,
            "trigger": {
                "triggerId": result.get("triggerId"),
                "name": result.get("name"),
                "path": result.get("path"),
            },
        }

    async def _publish_container(
        self, args: Dict[str, Any], client: GTMClient
    ) -> Dict[str, Any]:
        """Create and publish a container version."""
        workspace_path = args["workspace_path"]
        version_name = args["version_name"]
        version_notes = args.get("version_notes", "")

        # Create version
        version = client.create_version(workspace_path, version_name, version_notes)
        version_path = version.get("containerVersion", {}).get("path")

        if not version_path:
            raise ValueError("Failed to create version")

        # Publish version
        result = client.publish_version(version_path)
        return {
            "success": True,
            "version": {
                "versionId": result.get("containerVersion", {}).get(
                    "containerVersionId"
                ),
                "name": result.get("containerVersion", {}).get("name"),
                "published": True,
            },
        }

    async def _list_variables(
        self, args: Dict[str, Any], client: GTMClient
    ) -> Dict[str, Any]:
        """List variables in a workspace."""
        workspace_path = args["workspace_path"]
        variables = client.list_variables(workspace_path)
        return {
            "variables": [
                {
                    "variableId": var.get("variableId"),
                    "name": var.get("name"),
                    "type": var.get("type"),
                    "path": var.get("path"),
                }
                for var in variables
            ]
        }

    async def _get_variable(
        self, args: Dict[str, Any], client: GTMClient
    ) -> Dict[str, Any]:
        """Get detailed variable configuration."""
        variable_path = args["variable_path"]
        variable = client.get_variable(variable_path)
        return {"variable": variable}

    async def _create_variable(
        self, args: Dict[str, Any], client: GTMClient
    ) -> Dict[str, Any]:
        """Create a new variable."""
        workspace_path = args["workspace_path"]

        variable_data = {"name": args["variable_name"], "type": args["variable_type"]}

        # Add variable configuration based on type
        if "variable_config" in args:
            config = args["variable_config"]

            # Build parameters based on variable type
            if args["variable_type"] == "c":  # Constant
                variable_data["parameter"] = [
                    {
                        "type": "template",
                        "key": "value",
                        "value": config.get("value", ""),
                    }
                ]
            elif args["variable_type"] == "jsm":  # Custom JavaScript Variable
                variable_data["parameter"] = [
                    {
                        "type": "template",
                        "key": "javascript",
                        "value": config.get("javascript", ""),
                    }
                ]
            elif args["variable_type"] == "u":  # URL variable
                variable_data["parameter"] = [
                    {
                        "type": "template",
                        "key": "component",
                        "value": config.get("component", "URL"),
                    }
                ]
            elif args["variable_type"] == "v":  # Data Layer Variable
                variable_data["parameter"] = [
                    {
                        "type": "template",
                        "key": "name",
                        "value": config.get("data_layer_name", ""),
                    },
                    {
                        "type": "integer",
                        "key": "dataLayerVersion",
                        "value": config.get("version", "2"),
                    },
                ]
            elif args["variable_type"] == "k":  # First-Party Cookie
                variable_data["parameter"] = [
                    {
                        "type": "template",
                        "key": "name",
                        "value": config.get("cookie_name", ""),
                    }
                ]
            elif (
                args["variable_type"] == "awec"
            ):  # User-Provided Data (Enhanced Conversions)
                # Build user data parameters with proper template type for variable references
                params = [{"type": "template", "key": "mode", "value": "MANUAL"}]
                # Add user data fields
                user_data_fields = [
                    "email",
                    "phone_number",
                    "first_name",
                    "last_name",
                    "street",
                    "city",
                    "region",
                    "postal_code",
                    "country",
                ]
                for field in user_data_fields:
                    if field in config:
                        params.append(
                            {"type": "template", "key": field, "value": config[field]}
                        )
                variable_data["parameter"] = params
            else:
                # Generic parameter handling
                variable_data["parameter"] = self._build_parameters(config)

        result = client.create_variable(workspace_path, variable_data)
        return {
            "success": True,
            "variable": {
                "variableId": result.get("variableId"),
                "name": result.get("name"),
                "type": result.get("type"),
                "path": result.get("path"),
            },
        }

    def _build_parameters(self, config: Dict[str, Any]) -> list:
        """Build parameter list from configuration dictionary."""
        parameters = []
        for key, value in config.items():
            if isinstance(value, list):
                # Handle list/map parameters (for lookup tables, etc.)
                parameters.append(
                    {
                        "type": "list",
                        "key": key,
                        "list": [
                            {
                                "type": "map",
                                "map": [
                                    {"type": "template", "key": k, "value": str(v)}
                                    for k, v in item.items()
                                ],
                            }
                            for item in value
                        ],
                    }
                )
            else:
                parameters.append({"type": "template", "key": key, "value": str(value)})
        return parameters
