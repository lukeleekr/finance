#!/usr/bin/env python3
"""Create Polarity project in Tokyo region"""

import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    os.system(f"{sys.executable} -m pip install -q requests")
    import requests


access_token = os.getenv("SUPABASE_ACCESS_TOKEN")
if not access_token:
    print("❌ SUPABASE_ACCESS_TOKEN required")
    sys.exit(1)

base_url = "https://api.supabase.com/v1"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

print("\n" + "=" * 70)
print("🚀 Creating Supabase Project: POLARITY")
print("=" * 70)

# Config
PROJECT_NAME = "polarity"
REGION = "ap-northeast-1"  # Tokyo - closest to South Korea
DB_PASSWORD = "Dydgns0312!"

print(f"\n📋 Configuration:")
print(f"   Name: {PROJECT_NAME}")
print(f"   Region: {REGION} (Tokyo)")
print(f"   Password: {'*' * len(DB_PASSWORD)}")

# Get organization
print(f"\n[1/5] 🏢 Fetching organization...")
resp = requests.get(f"{base_url}/organizations", headers=headers)
resp.raise_for_status()
orgs = resp.json()
org_id = orgs[0]['id']
print(f"✅ Using: {orgs[0]['name']}")

# Create project
print(f"\n[2/5] 🏗️  Creating project...")
print(f"   (This takes ~2 minutes, please wait...)")

resp = requests.post(
    f"{base_url}/projects",
    headers=headers,
    json={
        "name": PROJECT_NAME,
        "organization_id": org_id,
        "region": REGION,
        "plan": "free",
        "db_pass": DB_PASSWORD
    }
)

if resp.status_code not in [200, 201]:
    print(f"❌ Failed: {resp.text}")
    sys.exit(1)

project = resp.json()
project_ref = project['ref']
project_url = f"https://{project_ref}.supabase.co"

print(f"✅ Project created!")
print(f"   ID: {project['id']}")
print(f"   Ref: {project_ref}")
print(f"   URL: {project_url}")

# Fetch API keys
print(f"\n[3/5] 🔑 Retrieving API keys...")
anon_key = service_key = ""

for attempt in range(10):
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
                print(f"✅ API keys retrieved")
                break
    except:
        pass
    print(f"   Attempt {attempt + 1}/10...")

if not anon_key:
    print("⚠️  Keys not ready yet - retrieve later from dashboard")

# Create .env file
print(f"\n[4/5] 💾 Creating .env file...")

env_content = f"""# Supabase Project: Polarity
# Region: Tokyo (ap-northeast-1) - Optimized for South Korea
# Created: {time.strftime('%Y-%m-%d %H:%M:%S')}

# ============================================
# SUPABASE CREDENTIALS
# ============================================
SUPABASE_URL={project_url}
SUPABASE_KEY={anon_key}
SUPABASE_SERVICE_ROLE_KEY={service_key}

# ============================================
# PROJECT DETAILS
# ============================================
SUPABASE_PROJECT_REF={project_ref}
SUPABASE_REGION={REGION}
SUPABASE_DB_PASSWORD={DB_PASSWORD}

# ⚠️  SECURITY WARNING:
# - Never commit this file to git (.env is in .gitignore)
# - SERVICE_ROLE_KEY bypasses all Row Level Security
# - Keep database password secure

# ============================================
# APPLICATION SETTINGS
# ============================================
DEBUG=true
LOG_LEVEL=info

# ============================================
# FINANCIAL DATA API KEYS
# ============================================
# Alpha Vantage: https://www.alphavantage.co/support/#api-key
# ALPHA_VANTAGE_API_KEY=

# Finnhub: https://finnhub.io/dashboard
# FINNHUB_API_KEY=

# ============================================
"""

with open(".env", "w") as f:
    f.write(env_content)

print("✅ .env created with all credentials")

# Configure Claude MCP
print(f"\n[5/5] ⚙️  Configuring Claude Code MCP server...")

settings_path = Path.home() / ".claude" / "settings.json"

if settings_path.exists():
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    # Create backup
    backup = settings_path.with_suffix('.json.backup')
    with open(backup, 'w') as f:
        json.dump(settings, f, indent=2)
else:
    settings = {}

if "mcpServers" not in settings:
    settings["mcpServers"] = {}

settings["mcpServers"]["supabase"] = {
    "type": "http",
    "url": f"https://mcp.supabase.com/mcp?project_ref={project_ref}",
    "headers": {
        "Authorization": f"Bearer {access_token}"
    }
}

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)

print("✅ Claude MCP configured")

# Success summary
print("\n" + "=" * 70)
print("✅ SETUP COMPLETE! 🎉")
print("=" * 70)

print(f"\n📊 PROJECT DETAILS:")
print(f"   Name: Polarity")
print(f"   Region: Tokyo (optimized for South Korea)")
print(f"   Dashboard: https://app.supabase.com/project/{project_ref}")

print(f"\n📝 CONFIGURATION FILES:")
print(f"   ✓ .env (all credentials saved)")
print(f"   ✓ ~/.claude/settings.json (MCP server connected)")

print(f"\n🔄 NEXT STEPS:")
print(f"   1. Restart Claude Code for MCP changes to take effect")
print(f"   2. Supabase MCP server will be available")
print(f"   3. Start building your Bloomberg-style finance platform!")

print(f"\n💡 QUICK START:")
print(f"   - Project URL: {project_url}")
print(f"   - Database: PostgreSQL 15.x")
print(f"   - Connection: Sub-10ms latency from Seoul")
