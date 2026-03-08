#!/usr/bin/env python3
"""CLI entry point for gpu-monitor."""

import argparse
import os
import sys
import webbrowser
import threading


def main():
    parser = argparse.ArgumentParser(
        prog="gpu-monitor",
        description="Web-based GPU monitoring dashboard for remote servers via SSH.",
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=5050,
        help="Port to run the server on (default: 5050)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open browser automatically",
    )
    parser.add_argument(
        "--ssh-config",
        default=None,
        help="Path to SSH config file (default: ~/.ssh/config)",
    )

    args = parser.parse_args()

    # Check SSH config exists
    ssh_config = args.ssh_config or os.path.expanduser("~/.ssh/config")
    if not os.path.exists(ssh_config):
        print(f"Warning: SSH config not found at {ssh_config}")
        print("GPU Monitor will start but no hosts will be queried.")
        print("Create ~/.ssh/config or use --ssh-config to specify a path.\n")

    # Set custom SSH config path if provided
    if args.ssh_config:
        from . import server
        server.SSH_CONFIG_PATH = args.ssh_config

    from .server import app

    url = f"http://{args.host}:{args.port}"
    print(f"GPU Monitor v{_get_version()} starting on {url}")
    print(f"Reading SSH config from: {ssh_config}")
    print("Press Ctrl+C to stop.\n")

    if not args.no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    app.run(host=args.host, port=args.port, debug=False)


def _get_version():
    from . import __version__
    return __version__


if __name__ == "__main__":
    main()
