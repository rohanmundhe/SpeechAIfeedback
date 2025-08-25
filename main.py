#!/usr/bin/env python3
"""
Main entry point for Vercel deployment
"""
import subprocess
import sys
import os

def handler(event, context):
    """Vercel handler function"""
    # Set Streamlit config for production
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_SERVER_PORT"] = "8080"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    # Run Streamlit app
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8080",
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ]
    
    subprocess.run(cmd)

if __name__ == "__main__":
    handler(None, None)