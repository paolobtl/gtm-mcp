#!/usr/bin/env python3
"""
GTM MCP Setup Script
Guides users through configuring GTM MCP for Claude Desktop by:
1. Creating Google Cloud OAuth credentials
2. Configuring Claude Desktop automatically
"""

import json
import os
import platform
import sys
from pathlib import Path


def get_config_path():
    """Get the Claude Desktop config path based on OS"""
    system = platform.system()

    if system == "Darwin":  # macOS
        # Verify it's actually macOS with mac_ver()
        mac_ver = platform.mac_ver()[0]
        if mac_ver:
            print(f"   Detected macOS version: {mac_ver}")
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"

    elif system == "Linux":
        # Check if we can get more specific Linux distribution info
        try:
            os_release = platform.freedesktop_os_release()
            distro_name = os_release.get('NAME', 'Unknown Linux')
            print(f"   Detected: {distro_name}")
        except (OSError, AttributeError):
            # freedesktop_os_release not available or file not found
            print(f"   Detected: Linux")

        # Follow XDG Base Directory specification
        xdg_config = os.getenv("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / "Claude" / "claude_desktop_config.json"
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"

    elif system == "Windows":
        # Get Windows version info for better error messages
        try:
            win_ver = platform.win32_ver()
            if win_ver[0]:  # release
                print(f"   Detected Windows {win_ver[0]}")
                # Check for Windows 10/11 specific editions
                try:
                    edition = platform.win32_edition()
                    if edition:
                        print(f"   Edition: {edition}")
                except AttributeError:
                    pass  # win32_edition() not available in older Python versions
        except AttributeError:
            print(f"   Detected: Windows")

        # Use APPDATA for Windows, which is the standard location for app configs
        appdata = os.getenv("APPDATA")
        if not appdata:
            print("❌ APPDATA environment variable not found")
            print("   This is unusual for Windows. Please check your system configuration.")
            sys.exit(1)
        return Path(appdata) / "Claude" / "claude_desktop_config.json"

    else:
        print(f"❌ Unsupported operating system: {system}")
        print(f"   Detected: {platform.platform()}")
        print(f"   Machine: {platform.machine()}")
        print(f"   Architecture: {platform.architecture()}")
        print("\n   Please report this issue at: https://github.com/paolobtl/gtm-mcp/issues")
        sys.exit(1)


def print_header():
    """Print welcome header"""
    print("\n" + "="*70)
    print("🚀 GTM MCP Setup Wizard")
    print("="*70)
    print("\nThis script will guide you through:")
    print("  1. Creating Google Cloud OAuth credentials (~5 minutes)")
    print("  2. Configuring Claude Desktop automatically")
    print("\nYou'll need a Google account with access to Google Tag Manager.\n")


def configure_claude(credentials):
    """Configure Claude Desktop with credentials"""
    print(f"\n⚙️  Configuring Claude Desktop...")

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
            if not Path(__file__).parent.name == "gtm_mcp":
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

        response = input("Continue with setup? (y/n): ").strip().lower()
        if response != 'y':
            print("\n❌ Setup cancelled")
            return

        # Guide user through manual setup
        print("\n" + "="*70)
        print("📋 Setup Instructions")
        print("="*70)

        print("\nWe'll create OAuth credentials in Google Cloud Console.")
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
