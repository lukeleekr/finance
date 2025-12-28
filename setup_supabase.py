#!/usr/bin/env python3
"""
Automated Supabase Project Setup
Creates project via API and configures both .env and Claude MCP settings.
"""

import json
import os
import sys
import time
from pathlib import Path
from getpass import getpass

try:
    import requests
except ImportError:
    print("Installing required package: requests")
    os.system(f"{sys.executable} -m pip install requests")
    import requests


def setup_supabase(access_token: str):
    """
    Complete Supabase setup using access token.

    Args:
        access_token: Your Supabase personal access token
    """
    base_url = "https://api.supabase.com/v1"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    print("\n" + "=" * 70)
    print("🚀 Automated Supabase Project Setup")
    print("=" * 70)

    # Step 1: List organizations
    print("\n[1/6] 📋 Fetching your organizations...")
    try:
        resp = requests.get(f"{base_url}/organizations", headers=headers)
        resp.raise_for_status()
        orgs = resp.json()
    except Exception as e:
        print(f"❌ Error fetching organizations: {e}")
        return

    if not orgs:
        print("❌ No organizations found. Create one at https://app.supabase.com")
        return

    print(f"✅ Found {len(orgs)} organization(s)")
    for i, org in enumerate(orgs, 1):
        print(f"   {i}. {org.get('name')} (ID: {org.get('id')})")

    # Select organization
    if len(orgs) == 1:
        selected_org = orgs[0]
        print(f"\n✓ Using: {selected_org.get('name')}")
    else:
        choice = int(input(f"\nSelect organization (1-{len(orgs)}): ")) - 1
        selected_org = orgs[choice]

    org_id = selected_org.get("id")

    # Step 2: Check existing projects
    print("\n[2/6] 📦 Checking for existing projects...")
    try:
        resp = requests.get(
            f"{base_url}/projects",
            headers=headers,
            params={"org_id": org_id}
        )
        resp.raise_for_status()
        existing = resp.json()
    except Exception as e:
        print(f"⚠️  Could not fetch projects: {e}")
        existing = []

    if existing:
        print(f"✅ Found {len(existing)} existing project(s):")
        for proj in existing:
            print(f"   - {proj.get('name')} (ref: {proj.get('ref')})")

        use_existing = input("\nUse existing project? (y/n): ").lower().strip()
        if use_existing == 'y':
            for i, proj in enumerate(existing, 1):
                print(f"   {i}. {proj.get('name')}")
            choice = int(input(f"Select (1-{len(existing)}): ")) - 1
            project = existing[choice]
            project_ref = project.get('ref')
            project_url = f"https://{project_ref}.supabase.co"
            region = project.get('region', 'us-east-1')

            # Get API keys
            print(f"\n[3/6] 🔑 Fetching API keys for {project_ref}...")
            try:
                resp = requests.get(
                    f"{base_url}/projects/{project_ref}/api-keys",
                    headers=headers
                )
                resp.raise_for_status()
                keys = resp.json()
                anon_key = next((k['api_key'] for k in keys if k.get('name') == 'anon'), '')
                service_key = next((k['api_key'] for k in keys if k.get('name') == 'service_role'), '')
                print("✅ API keys retrieved")
            except Exception as e:
                print(f"⚠️  Could not fetch keys: {e}")
                anon_key = service_key = ""

            db_password = getpass("\nEnter database password: ").strip()

            # Skip to configuration
            configure_everything(
                access_token, project_ref, project_url,
                anon_key, service_key, db_password, region
            )
            return

    # Step 3: Create new project
    print("\n[3/6] 🏗️  Creating new Supabase project...")

    project_name = input("Project name (e.g., 'Finance Platform'): ").strip()

    # Select region
    regions = {
        "1": ("us-east-1", "US East (N. Virginia)"),
        "2": ("us-west-1", "US West (N. California)"),
        "3": ("eu-west-1", "EU West (Ireland)"),
        "4": ("eu-central-1", "EU Central (Frankfurt)"),
        "5": ("ap-southeast-1", "Asia Pacific (Singapore)"),
        "6": ("ap-northeast-1", "Asia Pacific (Tokyo)")
    }

    print("\nAvailable regions:")
    for key, (code, name) in regions.items():
        print(f"   {key}. {name} ({code})")

    region_choice = input("Select region (1-6, default: 1): ").strip() or "1"
    region = regions[region_choice][0]

    # Database password
    print("\n🔒 Database password (minimum 12 characters)")
    while True:
        db_password = getpass("Password: ").strip()
        if len(db_password) >= 12:
            confirm = getpass("Confirm: ").strip()
            if db_password == confirm:
                break
            print("❌ Passwords don't match")
        else:
            print("❌ Minimum 12 characters required")

    # Create project
    print(f"\n🚀 Creating '{project_name}' in {region}...")
    print("   (This may take 1-2 minutes...)")

    try:
        resp = requests.post(
            f"{base_url}/projects",
            headers=headers,
            json={
                "name": project_name,
                "organization_id": org_id,
                "region": region,
                "plan": "free",
                "db_pass": db_password,
                "db_region": region
            }
        )
        resp.raise_for_status()
        project = resp.json()
        project_ref = project.get('ref')
        project_url = f"https://{project_ref}.supabase.co"

        print(f"✅ Project created!")
        print(f"   ID: {project.get('id')}")
        print(f"   Ref: {project_ref}")
        print(f"   URL: {project_url}")
    except Exception as e:
        print(f"❌ Failed to create project: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Response: {e.response.text}")
        return

    # Step 4: Wait and fetch API keys
    print(f"\n[4/6] 🔑 Fetching API keys...")
    print("   Waiting for project provisioning...")

    anon_key = service_key = ""
    for attempt in range(5):
        time.sleep(3)
        try:
            resp = requests.get(
                f"{base_url}/projects/{project_ref}/api-keys",
                headers=headers
            )
            if resp.status_code == 200:
                keys = resp.json()
                anon_key = next((k['api_key'] for k in keys if k.get('name') == 'anon'), '')
                service_key = next((k['api_key'] for k in keys if k.get('name') == 'service_role'), '')
                if anon_key and service_key:
                    print("✅ API keys retrieved")
                    break
        except:
            pass
        print(f"   Attempt {attempt + 1}/5...")

    if not anon_key:
        print("⚠️  Keys not ready yet. You can get them later from:")
        print(f"   https://app.supabase.com/project/{project_ref}/settings/api")

    # Step 5 & 6: Configure everything
    configure_everything(
        access_token, project_ref, project_url,
        anon_key, service_key, db_password, region
    )


def configure_everything(
    access_token, project_ref, project_url,
    anon_key, service_key, db_password, region
):
    """Configure .env file and Claude MCP settings."""

    # Configure .env
    print("\n[5/6] 💾 Creating .env file...")

    env_content = f"""# Supabase Configuration
# Auto-generated by setup_supabase.py

# ============================================
# SUPABASE - Python Client
# ============================================
SUPABASE_URL={project_url}
SUPABASE_KEY={anon_key}
SUPABASE_SERVICE_ROLE_KEY={service_key}

# ============================================
# SUPABASE - MCP Server Reference
# ============================================
# These are configured in ~/.claude/settings.json
# SUPABASE_ACCESS_TOKEN=(your access token)
# SUPABASE_PROJECT_REF={project_ref}
# SUPABASE_REGION={region}

# Project database password (keep secure!)
SUPABASE_DB_PASSWORD={db_password}

# ============================================
# PROJECT SETTINGS
# ============================================
DEBUG=true
LOG_LEVEL=info

# ============================================
# FINANCIAL DATA SOURCES
# ============================================
# ALPHA_VANTAGE_API_KEY=
# FINNHUB_API_KEY=
"""

    with open(".env", "w") as f:
        f.write(env_content)

    print("✅ .env file created")

    # Configure Claude MCP settings
    print("\n[6/6] ⚙️  Configuring Claude Code MCP settings...")

    settings_path = Path.home() / ".claude" / "settings.json"

    # Read existing settings
    if settings_path.exists():
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        # Backup
        backup_path = settings_path.with_suffix('.json.backup')
        with open(backup_path, 'w') as f:
            json.dump(settings, f, indent=2)
    else:
        settings = {}

    # Add MCP server
    if "mcpServers" not in settings:
        settings["mcpServers"] = {}

    settings["mcpServers"]["supabase"] = {
        "type": "http",
        "url": f"https://mcp.supabase.com/mcp?project_ref={project_ref}",
        "headers": {
            "Authorization": f"Bearer {access_token}"
        }
    }

    # Write settings
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)

    print(f"✅ Claude settings updated")

    # Success summary
    print("\n" + "=" * 70)
    print("✅ SETUP COMPLETE!")
    print("=" * 70)
    print(f"\n📊 Project Dashboard:")
    print(f"   https://app.supabase.com/project/{project_ref}")
    print(f"\n📝 Configuration Files:")
    print(f"   - .env (project credentials)")
    print(f"   - ~/.claude/settings.json (MCP server)")
    print(f"\n🔄 Next Steps:")
    print(f"   1. Restart Claude Code")
    print(f"   2. Supabase MCP should now be connected")
    print(f"\n⚠️  Security Reminders:")
    print(f"   - Never commit .env to git")
    print(f"   - Use dev/test projects only with MCP")
    print(f"   - Keep SERVICE_ROLE_KEY secret")


def main():
    """Main entry point."""
    print("🔐 Supabase Access Token Required")
    print("Get it from: https://app.supabase.com/account/tokens\n")

    access_token = os.getenv("SUPABASE_ACCESS_TOKEN")
    if not access_token:
        access_token = getpass("Enter your Supabase Access Token: ").strip()

    if not access_token:
        print("❌ Access token required")
        sys.exit(1)

    setup_supabase(access_token)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
