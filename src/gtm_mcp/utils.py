import os
from pathlib import Path
from typing import Dict, Any, List
from google.oauth2.credentials import Credentials
from google.auth.credentials import TokenState
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GTMAuth:
    """Handle Google Tag Manager authentication and service creation."""

    def __init__(self, token_file: Path, service_name: str, version: str, scopes: List[str]) -> None:
        """
        Initialize GTM authentication handler.

        Args:
            token_file: Path to store OAuth token
            service_name: Google API service name (e.g., 'tagmanager')
            version: API version (e.g., 'v2')
            scopes: List of OAuth scopes required
        """
        self.token_file = token_file
        self.service_name = service_name
        self.version = version
        self.scopes = scopes
        self.credentials = None

    def authenticate(self):
        """
        Authenticate with Google Tag Manager API and return service client.

        Returns:
            Google API service client
        """
        credentials = None

        # Load existing token if available
        if self.token_file.exists():
            try:
                credentials = Credentials.from_authorized_user_file(
                    str(self.token_file), self.scopes
                )
            except Exception as e:
                print(f"Warning: Could not load token file: {e}")
                credentials = None

        # Refresh expired credentials or run OAuth flow
        if credentials and credentials.token_state != TokenState.FRESH and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                self.token_file.parent.mkdir(parents=True, exist_ok=True)
                self.token_file.write_text(credentials.to_json())
            except Exception as e:
                print(f"Warning: Could not refresh token: {e}")
                credentials = None

        # Run OAuth flow if no valid credentials
        if not credentials or not credentials.valid:
            client_config = self._get_client_config()
            flow = InstalledAppFlow.from_client_config(client_config, self.scopes)
            credentials = flow.run_local_server(port=0)

            # Save credentials for future use
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            self.token_file.write_text(credentials.to_json())

        self.credentials = credentials
        service = build(self.service_name, self.version, credentials=credentials)
        return service

    def _get_client_config(self) -> Dict[str, Any]:
        """
        Get OAuth client configuration from environment variables.

        Users must set these environment variables:
        - GTM_CLIENT_ID: Your Google OAuth Client ID
        - GTM_CLIENT_SECRET: Your Google OAuth Client Secret
        - GTM_PROJECT_ID: Your Google Cloud Project ID

        See setup guide for instructions on creating these credentials.
        """
        client_id = os.getenv("GTM_CLIENT_ID")
        client_secret = os.getenv("GTM_CLIENT_SECRET")
        project_id = os.getenv("GTM_PROJECT_ID")

        if not client_id or not client_secret:
            raise ValueError(
                "Missing required OAuth credentials!\n\n"
                "Please set the following environment variables:\n"
                "  - GTM_CLIENT_ID\n"
                "  - GTM_CLIENT_SECRET\n"
                "  - GTM_PROJECT_ID (optional)\n\n"
                "See the setup guide for instructions:\n"
                "https://github.com/paolbtl/gtm-mcp/"
            )

        return {
            "installed": {
                "client_id": client_id,
                "project_id": project_id or "gtm-mcp",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": client_secret,
                "redirect_uris": ["http://localhost"]
            }
        }


def _authenticate(token_file: Path, service_name: str, version: str, scopes: List[str]):
    """
    Helper function to authenticate with Google Tag Manager API.

    Args:
        token_file: Path to store OAuth token
        service_name: Google API service name
        version: API version
        scopes: List of OAuth scopes

    Returns:
        Google API service client
    """
    auth = GTMAuth(token_file, service_name, version, scopes)
    return auth.authenticate()
