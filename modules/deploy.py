#!/usr/bin/env python3
"""
SpokeStack Deployment Wizard

Deploy the modular agent platform to Railway, Docker, or locally.
Guides you through everything step by step.

Usage:
    python deploy.py                 # Interactive wizard
    python deploy.py railway         # Railway deployment
    python deploy.py local           # Local development
    python deploy.py docker          # Docker Compose
"""

import os
import sys
import json
import subprocess
import shutil
import time

# Colors
G = "\033[92m"  # green
Y = "\033[93m"  # yellow
R = "\033[91m"  # red
B = "\033[94m"  # blue
W = "\033[97m"  # white
D = "\033[0m"   # reset
BOLD = "\033[1m"


def header():
    print(f"""
{B}╔═══════════════════════════════════════════════╗
║     {W}{BOLD}SpokeStack Deployment Wizard{D}{B}              ║
║     {W}Modular Agent Platform v2.0{D}{B}               ║
╚═══════════════════════════════════════════════╝{D}
""")


def check(label: str, ok: bool, detail: str = ""):
    icon = f"{G}✓{D}" if ok else f"{R}✗{D}"
    print(f"  {icon} {label}" + (f"  {Y}({detail}){D}" if detail else ""))
    return ok


def cmd_exists(name: str) -> bool:
    return shutil.which(name) is not None


def run(command: str, capture=True, check_code=False) -> tuple[int, str]:
    try:
        result = subprocess.run(
            command, shell=True, capture_output=capture, text=True, timeout=60
        )
        return result.returncode, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return 1, "timeout"
    except Exception as e:
        return 1, str(e)


def get_openrouter_key() -> str:
    """Get or prompt for OpenRouter API key."""
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if key:
        return key

    print(f"\n  {Y}OpenRouter API key not found in environment.{D}")
    print(f"  Get one at: {B}https://openrouter.ai/keys{D}")
    print()
    key = input(f"  Enter your OpenRouter API key: ").strip()
    return key


# =============================================================================
# Railway Deployment
# =============================================================================

def deploy_railway():
    print(f"\n{B}▸ Railway Deployment{D}\n")

    # Check prerequisites
    print(f"  {W}Checking prerequisites...{D}")
    has_railway = check("Railway CLI installed", cmd_exists("railway"))
    has_git = check("Git installed", cmd_exists("git"))

    if not has_railway:
        print(f"\n  Install Railway CLI:")
        print(f"  {G}npm install -g @railway/cli{D}")
        print(f"  Then run: {G}railway login{D}")
        return

    # Check login
    code, _ = run("railway whoami")
    check("Railway authenticated", code == 0, "run 'railway login' if not")
    if code != 0:
        print(f"\n  Run: {G}railway login{D}")
        return

    # Get API key
    api_key = get_openrouter_key()
    if not api_key:
        print(f"\n  {R}API key required. Get one at https://openrouter.ai/keys{D}")
        return

    print(f"\n  {W}Choose deployment mode:{D}")
    print(f"  {G}1{D} → Combined (single service, all 46 agents) — {Y}Recommended to start{D}")
    print(f"  {G}2{D} → Multi-service (9 services, one per module) — {Y}Production scale{D}")
    print()
    choice = input("  Choice [1]: ").strip() or "1"

    if choice == "1":
        deploy_railway_combined(api_key)
    elif choice == "2":
        deploy_railway_multi(api_key)
    else:
        print(f"  {R}Invalid choice{D}")


def deploy_railway_combined(api_key: str):
    """Deploy all modules as a single Railway service."""
    print(f"\n  {B}▸ Combined mode: one service, all 46 agents{D}\n")

    # Check if we're already in a Railway project
    code, project = run("railway status --json 2>/dev/null")

    if code != 0:
        print(f"  Creating Railway project...")
        code, _ = run("railway init")
        if code != 0:
            print(f"  {R}Failed to create project. Run 'railway init' manually.{D}")
            return

    # Set environment variables
    print(f"  Setting environment variables...")
    run(f'railway variables set OPENROUTER_API_KEY="{api_key}"')
    run('railway variables set PORT=8000')
    run('railway variables set RAILWAY_DOCKERFILE_PATH=modules/Dockerfile.combined')

    # Create the combined Dockerfile
    print(f"  Deploying...")
    code, output = run("railway up --detach", capture=False)

    if code == 0:
        print(f"\n  {G}✓ Deployed!{D}")
        print(f"\n  Get your URL:")
        print(f"  {G}railway domain{D}")
        print(f"\n  View logs:")
        print(f"  {G}railway logs{D}")
    else:
        print(f"\n  {R}Deployment failed. Check 'railway logs' for details.{D}")


def deploy_railway_multi(api_key: str):
    """Guide multi-service Railway deployment."""
    modules = [
        ("mission-control", 8000, "Dockerfile.mission-control"),
        ("foundation", 8001, "Dockerfile.module"),
        ("studio", 8002, "Dockerfile.module"),
        ("brand", 8003, "Dockerfile.module"),
        ("research", 8004, "Dockerfile.module"),
        ("strategy", 8005, "Dockerfile.module"),
        ("operations", 8006, "Dockerfile.module"),
        ("client", 8007, "Dockerfile.module"),
        ("distribution", 8008, "Dockerfile.module"),
    ]

    print(f"\n  {B}▸ Multi-service mode: 9 Railway services{D}\n")
    print(f"  This creates 9 services in your Railway project.")
    print(f"  Each module runs independently and mission-control orchestrates.\n")
    print(f"  {W}Steps:{D}")
    print()

    print(f"  {G}1.{D} Go to your Railway project dashboard")
    print(f"  {G}2.{D} For each module, click {W}\"+ New\" → \"Empty Service\"{D}")
    print(f"  {G}3.{D} Connect your GitHub repo to each service")
    print(f"  {G}4.{D} Configure each service as shown below:\n")

    for name, port, dockerfile in modules:
        print(f"  {B}━━━ {name} (port {port}) ━━━{D}")
        print(f"  Dockerfile Path: {G}modules/{dockerfile}{D}")
        if "module" in dockerfile:
            print(f"  Build Args:      {G}MODULE={name}{D}")
        print(f"  Variables:")
        print(f"    {Y}MODULE_PORT{D}={port}")
        print(f"    {Y}OPENROUTER_API_KEY{D}={api_key[:12]}...")
        if name == "mission-control":
            for mod_name, mod_port, _ in modules[1:]:
                print(f"    {Y}{mod_name.upper().replace('-','_')}_URL{D}=http://{mod_name}.railway.internal:{mod_port}")
        print()

    print(f"  {W}Internal networking:{D}")
    print(f"  Railway auto-creates internal DNS: {G}<service-name>.railway.internal{D}")
    print(f"  Only mission-control needs a public domain.\n")
    print(f"  {W}Tip:{D} Add a shared variable group for OPENROUTER_API_KEY")
    print(f"  so all services share the same key.\n")


# =============================================================================
# Local Development
# =============================================================================

def deploy_local():
    print(f"\n{B}▸ Local Development{D}\n")

    api_key = get_openrouter_key()
    if not api_key:
        print(f"  {R}API key required.{D}")
        return

    # Check Python
    check("Python 3.11+", sys.version_info >= (3, 11), f"Python {sys.version_info.major}.{sys.version_info.minor}")

    # Install deps
    print(f"\n  Installing dependencies...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    code, _ = run("pip install -r requirements.txt")
    check("Dependencies installed", code == 0)

    # Write .env
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    with open(env_path, "w") as f:
        f.write(f"OPENROUTER_API_KEY={api_key}\n")
    check(".env created", True)

    print(f"\n  {G}Ready!{D} Start with:")
    print(f"  {G}cd modules && python combined.py{D}")
    print(f"\n  Then open: {B}http://localhost:8000{D}")
    print(f"  API docs: {B}http://localhost:8000/docs{D}")


# =============================================================================
# Docker Compose
# =============================================================================

def deploy_docker():
    print(f"\n{B}▸ Docker Compose Deployment{D}\n")

    has_docker = check("Docker installed", cmd_exists("docker"))
    has_compose = check("Docker Compose installed", cmd_exists("docker") and run("docker compose version")[0] == 0)

    if not has_docker:
        print(f"\n  Install Docker: {B}https://docs.docker.com/get-docker/{D}")
        return

    api_key = get_openrouter_key()
    if not api_key:
        return

    # Write .env
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    with open(env_path, "w") as f:
        f.write(f"OPENROUTER_API_KEY={api_key}\n")
    check(".env created", True)

    print(f"\n  {W}Choose mode:{D}")
    print(f"  {G}1{D} → Combined (one container, all agents)")
    print(f"  {G}2{D} → Multi-service (9 containers via docker-compose)")
    print()
    choice = input("  Choice [1]: ").strip() or "1"

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if choice == "1":
        print(f"\n  Building combined image...")
        code, _ = run("docker build -f Dockerfile.combined -t spokestack .", capture=False)
        if code == 0:
            print(f"\n  {G}✓ Built!{D} Run with:")
            print(f"  {G}docker run -p 8000:8000 --env-file .env spokestack{D}")
    elif choice == "2":
        print(f"\n  Starting all services...")
        code, _ = run("docker compose up -d --build", capture=False)
        if code == 0:
            print(f"\n  {G}✓ All services running!{D}")
            print(f"  Mission Control: {B}http://localhost:8000{D}")
            print(f"  View logs: {G}docker compose logs -f{D}")


# =============================================================================
# Main
# =============================================================================

def main():
    header()

    if len(sys.argv) > 1:
        target = sys.argv[1].lower()
        if target == "railway":
            deploy_railway()
        elif target == "local":
            deploy_local()
        elif target == "docker":
            deploy_docker()
        else:
            print(f"  {R}Unknown target: {target}{D}")
            print(f"  Options: railway, local, docker")
        return

    print(f"  {W}Where do you want to deploy?{D}\n")
    print(f"  {G}1{D} → {W}Railway{D}         Cloud, auto-scaling, $5/mo+")
    print(f"  {G}2{D} → {W}Local{D}           Dev mode, your machine")
    print(f"  {G}3{D} → {W}Docker Compose{D}  Any server with Docker")
    print()

    choice = input("  Choice [1]: ").strip() or "1"

    if choice == "1":
        deploy_railway()
    elif choice == "2":
        deploy_local()
    elif choice == "3":
        deploy_docker()
    else:
        print(f"  {R}Invalid choice{D}")


if __name__ == "__main__":
    main()
