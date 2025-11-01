# GTM MCP Server

A Model Context Protocol (MCP) server that enables Claude to interact with Google Tag Manager.

## Table of Contents

- [Features](#features)
- [Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
- [Complete Setup Guide](#-complete-setup-guide)
  - [Part 1: Install the Package](#part-1-install-the-package)
  - [Part 2: Create Google Cloud OAuth Credentials](#part-2-create-google-cloud-oauth-credentials)
    - [Step 1: Create a Google Cloud Project](#step-1-create-a-google-cloud-project)
    - [Step 2: Enable Tag Manager API](#step-2-enable-tag-manager-api)
    - [Step 3: Configure OAuth Consent Screen](#step-3-configure-oauth-consent-screen)
    - [Step 4: Create OAuth Credentials](#step-4-create-oauth-credentials)
    - [Step 5: Save Your Credentials](#step-5-save-your-credentials)
  - [Part 3: Configure Claude Desktop](#part-3-configure-claude-desktop)
  - [Part 4: Restart and Authorize](#part-4-restart-and-authorize)
- [Available Tools](#%EF%B8%8F-available-tools)
- [How Authentication Works](#-how-authentication-works)
- [Upgrade](#upgrade)
- [Troubleshooting](#-troubleshooting)
- [Security Notes](#-security-notes)
- [Development](#-development)
  - [Running Tests](#running-tests)
- [License](#-license)
- [Contributing](#-contributing)
- [Getting Help](#-getting-help)


## Features
[⬆ top](#gtm-mcp-server)
- List GTM accounts and containers
- Manage tags, triggers, and variables
- Create and publish container versions
- Full workspace management

---

## 🚀 Quick Start
[⬆ top](#gtm-mcp-server)
### Prerequisites

- Python 3.10 or higher
- Claude Desktop (or any MCP-compatible client like Cursor)
- A Google account with access to Google Tag Manager

---

## 📋 Complete Setup Guide
[⬆ top](#gtm-mcp-server)
### Part 1: Install the Package

```bash
pip install gtm-mcp
```

See [PyPi](https://pypi.org/project/gtm-mcp/)


---

### Part 2: Create Google Cloud OAuth Credentials
[⬆ top](#gtm-mcp-server)
#### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown (top left)
3. Click **"New Project"**
4. Enter a project name (e.g., "My GTM MCP Server")
5. Click **"Create"**
6. Wait for the project to be created and select it

#### Step 2: Enable Tag Manager API

1. In your project, go to **"APIs & Services"** → **"Library"**
2. Search for **"Tag Manager API"**
3. Click on it and click **"Enable"**
4. Wait for it to enable (may take a minute)

#### Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** (unless you have a Google Workspace)
3. Click **"Create"**
4. Fill in required fields:
   - **App name**: My GTM MCP (or whatever you like)
   - **User support email**: Your email
   - **Developer contact email**: Your email
5. Click **"Save and Continue"**
6. Click **"Update"** then **"Save and Continue"**
7. Add your email as a **test user**
8.  Click **"Save and Continue"**

#### Step 4: Create OAuth Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Select **"Desktop app"** as the application type
4. Enter a name: "GTM MCP Desktop Client"
5. Click **"Create"**
6. **IMPORTANT**: A dialog appears with your credentials - **DO NOT CLOSE IT YET**

#### Step 5: Save Your Credentials

From the dialog that appeared:

1. Copy the **Client ID** (looks like: `123456789-abc123.apps.googleusercontent.com`)
2. Copy the **Client secret** (looks like: `GOCSPX-...`)
3. Note your **Project ID** from the Google Cloud Console (top bar, next to project name)
4. Save these somewhere safe - you'll need them in the next step

You can also download the JSON file, but you only need the three values above.

---

### Part 3: Configure Claude Desktop
[⬆ top](#gtm-mcp-server)
Edit your Claude Desktop config file:

- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Claude Code** `~/.claude.json`

Add your credentials:

```json
{
  "mcpServers": {
    "gtm-mcp": {
      "command": "gtm-mcp",
      "env": {
        "GTM_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GTM_CLIENT_SECRET": "GOCSPX-your-client-secret",
        "GTM_PROJECT_ID": "your-project-id"
      }
    }
  }
}
```

**Replace the values** with your actual credentials from Part 2, Step 5.

> **Note**: If you have other MCP servers configured, just add the `"gtm-mcp"` entry to the existing `"mcpServers"` object.

---

### Part 4: Restart and Authorize
[⬆ top](#gtm-mcp-server)
1. **Restart Claude Desktop** completely (close and reopen)

2. Ask Claude to use a GTM tool (e.g., "List my GTM accounts")

3. **First-time authorization** - a browser window will open automatically:
   - Sign in with your Google account
   - You'll see **"Google hasn't verified this app"** warning
   - Click **"Advanced"** → **"Go to [Your App Name] (unsafe)"**
   - This is safe because **you created the app yourself**
   - Grant the requested permissions
   - You'll see "The authentication flow has completed"
   - Return to Claude Desktop

4. Your authorization is saved locally - you won't need to do this again!

---

## 🛠️ Available Tools
[⬆ top](#gtm-mcp-server) </br>
Once configured, Claude will have access to these GTM tools:

| Tool | Description |
|------|-------------|
| `gtm_list_accounts` | List all your GTM accounts |
| `gtm_list_containers` | List containers in an account |
| `gtm_list_tags` | List tags in a workspace |
| `gtm_get_tag` | Get detailed configuration of a specific tag |
| `gtm_create_tag` | Create a new tag |
| `gtm_update_tag` | Update an existing tag |
| `gtm_list_triggers` | List triggers in a workspace |
| `gtm_create_trigger` | Create a new trigger |
| `gtm_list_variables` | List variables in a workspace |
| `gtm_create_variable` | Create a new variable (constant, data layer, cookie, URL, etc.) |
| `gtm_publish_container` | Create and publish a new container version |

---

## 🔐 How Authentication Works
[⬆ top](#gtm-mcp-server) </br>
This MCP server uses **OAuth 2.0** to securely access Google Tag Manager:

1. **You create OAuth credentials** in your own Google Cloud project
2. **You configure** those credentials in Claude Desktop
3. **First use**: Browser opens to authorize access to your GTM account
4. **Your tokens** are saved locally on your machine (`~/.gtm-mcp-token.json`) for future use

### Why Do I Need My Own OAuth Credentials?

For security and privacy:
- ✅ You maintain full control over the OAuth app
- ✅ No shared credentials between users
- ✅ You can revoke access anytime
- ✅ Your credentials stay private
- ✅ Compliant with Google's OAuth policies

---
## Upgrade

Run `pip install --upgrade gtm-mcp`

---
## ❓ Troubleshooting
[⬆ top](#gtm-mcp-server)
### "Missing required OAuth credentials" Error

**Problem**: The MCP server can't find your credentials.

**Solution**: Make sure you:
- Set the environment variables correctly in `claude_desktop_config.json` (or `~/.claude.json`)
- Restarted Claude Desktop after editing the config
- Used the correct format (no extra quotes in JSON)
- The config file is valid JSON (use a JSON validator if unsure)

### "Google hasn't verified this app" Warning

**Problem**: Google shows a security warning during first authorization.

**Solution**: This is **completely normal** for personal OAuth apps. Since you created the OAuth app yourself, Google shows this warning.

To proceed: Click **"Advanced"** → **"Go to [App Name] (unsafe)"**

This is safe because **you control the app**.

### Can't Access GTM Accounts

**Possible causes**:
- Your Google account doesn't have access to any GTM accounts
- You didn't grant all requested permissions during authorization
- Tag Manager API isn't enabled in your Google Cloud project

**Solution**:
1. Verify your Google account has GTM access
2. Re-authorize by deleting `~/.gtm-mcp-token.json` and trying again
3. Check that Tag Manager API is enabled in Google Cloud Console

### Connection Issues

**Debugging steps**:
1. Verify Claude Desktop is completely restarted
2. Check Claude Desktop logs for MCP server errors
3. Verify `gtm-mcp` command works: run `gtm-mcp` in terminal
4. Check your config file is valid JSON
5. Ensure all three environment variables are set correctly

### Package Not Found After Install

**Problem**: `gtm-mcp` command not found after installation.

**Solution**:
```bash
# Ensure pip install location is in PATH
pip install --user gtm-mcp

# Or use pipx for isolated installation
pipx install gtm-mcp
```

### Revoking Access

To revoke access to your GTM account:
1. Go to [Google Account Permissions](https://myaccount.google.com/permissions)
2. Find your app name in the list
3. Click **"Remove access"**
4. Delete the local token file: `rm ~/.gtm-mcp-token.json`

You can re-authorize anytime by using any GTM tool in Claude again.

---

## 🔒 Security Notes
[⬆ top](#gtm-mcp-server)
- **Your OAuth credentials are yours alone** - keep them private
- **Never share your Client Secret** - treat it like a password
- Your access tokens are stored locally: `~/.gtm-mcp-token.json`
- You can regenerate credentials anytime in Google Cloud Console
- You can revoke access anytime from your Google account settings
- This server only accesses GTM - no other Google services

---

## 💻 Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

---

## 📝 License
[⬆ top](#gtm-mcp-server)
see [LICENSE](https://github.com/paolobtl/gtm-mcp/blob/main/LICENSE) file for details

---

## 🤝 Contributing
[⬆ top](#gtm-mcp-server)
Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

For bugs and feature requests, please [open an issue](https://github.com/paolobtl/gtm-mcp/issues).

---

## 🆘 Getting Help
[⬆ top](#gtm-mcp-server)
If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section above
2. Review Claude Desktop logs for error messages
3. Verify your Google Cloud project has Tag Manager API enabled
4. Ensure environment variables are set correctly in the config
5. [Open an issue](https://github.com/paolobtl/gtm-mcp/issues) on GitHub with:
   - Your operating system
   - Python version (`python --version`)
   - Error messages from Claude Desktop logs
   - Steps to reproduce the issue

---
