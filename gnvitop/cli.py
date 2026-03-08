#!/usr/bin/env python3
"""CLI entry point for gnvitop."""

import argparse
import os
import webbrowser
import threading


def main():
    parser = argparse.ArgumentParser(
        prog="gnvitop",
        description="Global nvitop: web-based GPU monitoring dashboard for remote servers via SSH.",
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
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show version and exit",
    )

    args = parser.parse_args()

    from . import __version__

    if args.version:
        print(f"gnvitop {__version__}")
        return

    # Check SSH config exists
    ssh_config = args.ssh_config or os.path.expanduser("~/.ssh/config")
    if not os.path.exists(ssh_config):
        print(f"Warning: SSH config not found at {ssh_config}")
        print("gnvitop will start but no hosts will be queried.")
        print("Create ~/.ssh/config or use --ssh-config to specify a path.\n")

    # Set custom SSH config path if provided
    if args.ssh_config:
        from . import server
        server.SSH_CONFIG_PATH = args.ssh_config

    from .server import app

    url = f"http://{args.host}:{args.port}"
    print(f"gnvitop v{__version__} starting on {url}")
    print(f"Reading SSH config from: {ssh_config}")
    print("Press Ctrl+C to stop.\n")

    if not args.no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
