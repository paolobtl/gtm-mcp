#!/usr/bin/env python3
"""
GTM MCP Setup Script
Automatically configures GTM MCP for Claude Desktop by:
1. Creating a Google Cloud project
2. Enabling Tag Manager API
3. Creating OAuth credentials
4. Configuring Claude Desktop
"""

import json
import os
import platform
import sys
import time
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_config_path():
    """Get the Claude Desktop config path based on OS"""
    system = platform.system()

    if system == "Darwin":  # macOS
        return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    elif system == "Linux":
        return Path.home() / ".config/Claude/claude_desktop_config.json"
    elif system == "Windows":
        return Path(os.getenv("APPDATA")) / "Claude/claude_desktop_config.json"
    else:
        print(f"❌ Unsupported operating system: {system}")
        sys.exit(1)


def print_header():
    """Print welcome header"""
    print("\n" + "="*70)
    print("🚀 GTM MCP Automated Setup Wizard")
    print("="*70)
    print("\nThis script will automatically:")
    print("  1. Create a Google Cloud project")
    print("  2. Enable Tag Manager API")
    print("  3. Create OAuth credentials")
    print("  4. Configure Claude Desktop")
    print("\nYou'll only need to authenticate with your Google account.\n")


def get_user_credentials():
    """Authenticate user with Google Cloud"""
    print("🔐 Step 1: Authenticate with Google Cloud\n")
    print("A browser window will open for authentication...")
    print("Please sign in with the Google account you want to use.\n")

    # Scopes needed to manage GCP projects and credentials
    scopes = [
        'https://www.googleapis.com/auth/cloud-platform',
        'https://www.googleapis.com/auth/cloudplatformprojects'
    ]

    try:
        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": "YOUR_CLIENT_ID",  # We'll use a temporary client for setup
                    "client_secret": "YOUR_CLIENT_SECRET",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"]
                }
            },
            scopes=scopes
        )

        creds = flow.run_local_server(port=0)
        return creds

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\nPlease make sure you have gcloud installed and configured.")
        print("Run: gcloud auth application-default login")
        sys.exit(1)


def create_gcp_project(creds, project_name="gtm-mcp-project"):
    """Create a new GCP project"""
    print(f"\n📦 Step 2: Creating Google Cloud project '{project_name}'...")

    try:
        service = build('cloudresourcemanager', 'v1', credentials=creds)

        # Generate unique project ID
        import random
        import string
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        project_id = f"gtm-mcp-{suffix}"

        project_body = {
            'projectId': project_id,
            'name': project_name
        }

        request = service.projects().create(body=project_body)
        response = request.execute()

        print(f"✅ Project created: {project_id}")

        # Wait for project to be ready
        print("⏳ Waiting for project to be ready...")
        time.sleep(5)

        return project_id

    except HttpError as e:
        print(f"❌ Failed to create project: {e}")
        sys.exit(1)


def enable_tag_manager_api(creds, project_id):
    """Enable Tag Manager API for the project"""
    print(f"\n🔌 Step 3: Enabling Tag Manager API...")

    try:
        service = build('serviceusage', 'v1', credentials=creds)

        service_name = f"projects/{project_id}/services/tagmanager.googleapis.com"

        request = service.services().enable(name=service_name)
        request.execute()

        print("✅ Tag Manager API enabled")

        # Wait for API to be enabled
        time.sleep(3)

    except HttpError as e:
        print(f"❌ Failed to enable API: {e}")
        sys.exit(1)


def create_oauth_credentials(creds, project_id):
    """Create OAuth 2.0 credentials"""
    print(f"\n🔑 Step 4: Creating OAuth credentials...")

    try:
        # First, configure OAuth consent screen
        print("   Configuring OAuth consent screen...")
        # Note: This requires additional setup via API which is complex
        # For now, we'll guide the user to do this manually

        print("\n⚠️  Manual step required:")
        print(f"\n1. Go to: https://console.cloud.google.com/apis/credentials/consent?project={project_id}")
        print("2. Select 'External' and click 'Create'")
        print("3. Fill in:")
        print("   - App name: GTM MCP")
        print("   - User support email: (your email)")
        print("   - Developer contact: (your email)")
        print("4. Click 'Save and Continue' through all steps")
        print("5. Add yourself as a test user")
        print("\nPress Enter when done...")
        input()

        # Now create OAuth client
        print("\n   Creating OAuth client...")

        service = build('oauth2', 'v2', credentials=creds)

        # Create OAuth client via API (simplified)
        # In reality, we need to use a different API endpoint
        print("\n⚠️  Manual step required:")
        print(f"\n1. Go to: https://console.cloud.google.com/apis/credentials?project={project_id}")
        print("2. Click 'Create Credentials' → 'OAuth client ID'")
        print("3. Select 'Desktop app'")
        print("4. Name: 'GTM MCP Desktop Client'")
        print("5. Click 'Create'")
        print("6. Copy the Client ID and Client Secret")
        print("\nEnter your credentials below:\n")

        client_id = input("Client ID: ").strip()
        client_secret = input("Client Secret: ").strip()

        if not client_id or not client_secret:
            print("❌ Invalid credentials")
            sys.exit(1)

        return {
            'project_id': project_id,
            'client_id': client_id,
            'client_secret': client_secret
        }

    except HttpError as e:
        print(f"❌ Failed to create credentials: {e}")
        sys.exit(1)


def configure_claude(credentials):
    """Configure Claude Desktop with credentials"""
    print(f"\n⚙️  Step 5: Configuring Claude Desktop...")

    config_path = get_config_path()
    print(f"   Config location: {config_path}")

    # Load existing config
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            print("⚠️  Existing config is invalid, creating new one")
            config = {"mcpServers": {}}
    else:
        config = {"mcpServers": {}}

    # Check if gtm-mcp already configured
    if "gtm-mcp" in config.get("mcpServers", {}):
        print("⚠️  GTM MCP is already configured")
        response = input("   Update configuration? (y/n): ").strip().lower()
        if response != 'y':
            print("❌ Setup cancelled")
            return False

    # Add GTM MCP config
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    config["mcpServers"]["gtm-mcp"] = {
        "command": "gtm-mcp",
        "env": {
            "GTM_CLIENT_ID": credentials['client_id'],
            "GTM_CLIENT_SECRET": credentials['client_secret'],
            "GTM_PROJECT_ID": credentials['project_id']
        }
    }

    # Save config
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✅ Configuration saved")
    return True


def print_next_steps():
    """Print what to do next"""
    print("\n" + "="*70)
    print("🎉 Setup Complete!")
    print("="*70)
    print("\nNext steps:")
    print("\n1. Restart Claude Desktop completely")
    print("2. Ask Claude: 'List my GTM accounts'")
    print("3. A browser will open for OAuth authorization")
    print("4. Sign in and grant permissions")
    print("5. You're all set!\n")
    print("💡 Note: You'll see 'Google hasn't verified this app'")
    print("   This is normal - click Advanced → Continue\n")


def main():
    """Main setup flow"""
    try:
        print_header()

        # Check if gtm-mcp is installed (skip in dev mode)
        try:
            import gtm_mcp
        except ImportError:
            # In development mode, the package might not be installed yet
            # Check if we're running from source
            if not Path(__file__).parent.name == "gtm-mcp":
                print("❌ gtm-mcp package not found")
                print("\nPlease install first:")
                print("  pip install gtm-mcp")
                sys.exit(1)

        # Check if already configured
        config_path = get_config_path()
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    if "gtm-mcp" in config.get("mcpServers", {}):
                        print("✅ GTM MCP is already configured!")
                        print(f"\nConfig location: {config_path}")
                        response = input("\nRun setup again? (y/n): ").strip().lower()
                        if response != 'y':
                            print("\n👍 All set! No changes needed.")
                            return
            except json.JSONDecodeError:
                pass

        print("\n⚠️  Important: This is a simplified setup wizard.")
        print("    Some steps require manual configuration in Google Cloud Console.")
        print("    We'll guide you through each step.\n")

        response = input("Continue? (y/n): ").strip().lower()
        if response != 'y':
            print("\n❌ Setup cancelled")
            return

        # Guide user through manual setup
        print("\n" + "="*70)
        print("📋 Manual Setup Instructions")
        print("="*70)

        print("\nWe'll need to create OAuth credentials manually.")
        print("This is a one-time setup that takes about 5 minutes.\n")

        print("1️⃣  Create a Google Cloud Project:")
        print("   → https://console.cloud.google.com/")
        print("   → Click 'New Project'")
        print("   → Name: 'GTM MCP' (or anything you like)")
        print("   → Click 'Create'\n")

        project_id = input("Enter your Project ID: ").strip()
        if not project_id:
            print("❌ Project ID required")
            return

        print("\n2️⃣  Enable Tag Manager API:")
        print(f"   → https://console.cloud.google.com/apis/library/tagmanager.googleapis.com?project={project_id}")
        print("   → Click 'Enable'\n")
        input("Press Enter when done...")

        print("\n3️⃣  Configure OAuth Consent Screen:")
        print(f"   → https://console.cloud.google.com/apis/credentials/consent?project={project_id}")
        print("   → Select 'External'")
        print("   → App name: 'GTM MCP'")
        print("   → Your email for support and developer contact")
        print("   → Save and Continue through all steps")
        print("   → Add yourself as a test user\n")
        input("Press Enter when done...")

        print("\n4️⃣  Create OAuth Credentials:")
        print(f"   → https://console.cloud.google.com/apis/credentials?project={project_id}")
        print("   → 'Create Credentials' → 'OAuth client ID'")
        print("   → Application type: 'Desktop app'")
        print("   → Name: 'GTM MCP Desktop'")
        print("   → Click 'Create'\n")

        client_id = input("Enter Client ID: ").strip()
        client_secret = input("Enter Client Secret: ").strip()

        if not client_id or not client_secret:
            print("❌ Credentials required")
            return

        # Configure Claude
        credentials = {
            'project_id': project_id,
            'client_id': client_id,
            'client_secret': client_secret
        }

        if configure_claude(credentials):
            print_next_steps()

    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
