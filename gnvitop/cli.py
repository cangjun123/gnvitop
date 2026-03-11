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

    # Detect if running inside an SSH session
    is_ssh = bool(os.environ.get("SSH_CONNECTION") or os.environ.get("SSH_TTY"))

    # In SSH mode, auto-bind to 0.0.0.0 so the dashboard is network-accessible
    # (unless user explicitly set --host)
    host = args.host
    user_set_host = any(
        arg in ("--host",) for arg in os.sys.argv[1:]
    )
    if is_ssh and not user_set_host:
        host = "0.0.0.0"

    print(f"gnvitop v{__version__} starting...")
    print(f"Reading SSH config from: {ssh_config}")

    if is_ssh:
        # SSH_CONNECTION format: client_ip client_port server_ip server_port
        ssh_conn = os.environ.get("SSH_CONNECTION", "")
        parts = ssh_conn.split()
        server_ip = parts[2] if len(parts) >= 3 else "this_server_ip"

        access_url = f"http://{server_ip}:{args.port}"
        print()
        print(f"  SSH session detected — dashboard is accessible at:")
        print(f"  \033[1;36m{access_url}\033[0m")
        print()
        print(f"  If the above URL is not reachable (e.g. behind a firewall),")
        print(f"  set up port forwarding from your local machine:")
        print(f"    ssh -L {args.port}:127.0.0.1:{args.port} {server_ip}")
        print(f"  Then open http://localhost:{args.port}")
    else:
        url = f"http://{host}:{args.port}"
        print(f"  Dashboard: \033[1;36m{url}\033[0m")

    print()
    print("Press Ctrl+C to stop.\n")

    if not args.no_browser and not is_ssh:
        url = f"http://{host}:{args.port}"
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    app.run(host=host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
