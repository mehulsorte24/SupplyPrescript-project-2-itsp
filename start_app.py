"""
SupplyPrescript Unified Launcher
Launches the SupplyPrescript AI Backend and serves the Enterprise UI.
"""

import sys
import webbrowser
from pathlib import Path
from backend.server import run_server

def main():
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    print("=================================================================")
    print("   SUPPLYPRESCRIPT — AI SUPPLY CHAIN INTELLIGENCE PLATFORM")
    print("=================================================================")
    print(f" * Unified Application URL: http://localhost:{port}")
    print(f" * REST API Health Check:   http://localhost:{port}/api/health")
    print(f" * Dashboard Endpoint:      http://localhost:{port}/api/dashboard")
    print("=================================================================")
    print("Opening browser...")

    try:
        webbrowser.open(f"http://localhost:{port}")
    except Exception:
        pass

    run_server(port)

if __name__ == "__main__":
    main()
