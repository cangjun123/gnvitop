# GPU Monitor

A web-based GPU monitoring dashboard for remote servers via SSH. Like `nvitop`, but as a web dashboard that reads your `~/.ssh/config` and monitors all your GPU servers in one page.

![Python](https://img.shields.io/badge/python-3.7+-blue) ![PyPI](https://img.shields.io/badge/pip_install-gpu--monitor-green)

## Install

```bash
pip install gpu-monitor
```

Or install from source:

```bash
git clone https://github.com/Linwei94/GPU-monitor.git
cd GPU-monitor
pip install .
```

## Usage

```bash
gpu-monitor
```

That's it. The browser will open automatically at `http://127.0.0.1:5050`.

### Options

```
gpu-monitor                        # Start with defaults
gpu-monitor -p 8080                # Custom port
gpu-monitor --host 0.0.0.0        # Expose to network
gpu-monitor --no-browser           # Don't auto-open browser
gpu-monitor --ssh-config /path/to/config  # Custom SSH config path
```

You can also run it as a Python module:

```bash
python -m gpu_monitor
```

## Prerequisites

- `~/.ssh/config` with your server entries
- SSH key-based authentication set up
- `nvidia-smi` installed on remote servers

### SSH Config Example

```
Host gpu-server-01
    HostName 192.168.1.101
    User admin
    Port 22
    IdentityFile ~/.ssh/id_rsa

Host gpu-server-02
    HostName 192.168.1.102
    User admin
```

All hosts in your SSH config will be queried for GPU information.

## Features

- Auto-reads `~/.ssh/config` - zero configuration
- Auto-opens browser on start
- Real-time monitoring with 30s auto-refresh
- Concurrent SSH queries (10 workers) with caching
- Summary: online hosts, total GPUs, idle GPUs, free memory
- Color-coded: green = online, yellow = no GPU, red = offline
- GPU utilization & memory progress bars
- Temperature monitoring with alerts
- Dark-themed responsive UI

## Architecture

```
pip install gpu-monitor && gpu-monitor

    Browser ──> Flask (localhost:5050) ──SSH──> Server 1 (nvidia-smi)
                                       ──SSH──> Server 2 (nvidia-smi)
                                       ──SSH──> Server N (nvidia-smi)
```

## License

MIT
