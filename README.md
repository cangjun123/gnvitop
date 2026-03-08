# GPU Monitor

A real-time GPU monitoring dashboard that monitors NVIDIA GPUs across multiple remote servers via SSH.

**[Live Demo](https://linwei94.github.io/GPU-monitor/)**

![Dark themed GPU monitoring dashboard](https://img.shields.io/badge/theme-dark-0f172a) ![Python](https://img.shields.io/badge/python-3.7+-blue) ![Flask](https://img.shields.io/badge/flask-latest-green)

## Features

- Real-time monitoring of NVIDIA GPUs across multiple SSH-accessible servers
- Auto-refresh every 30 seconds (configurable)
- Summary statistics: online hosts, total GPUs, idle GPUs, free memory
- Color-coded status indicators (green = online, yellow = no GPU, red = offline)
- GPU utilization and memory usage progress bars
- Temperature monitoring with color-coded alerts
- Responsive dark-themed UI
- Concurrent SSH queries with caching

## Quick Start

### Prerequisites

- Python 3.7+
- SSH access to remote GPU servers (key-based authentication)
- `nvidia-smi` installed on remote servers

### Installation

```bash
# Clone the repository
git clone https://github.com/Linwei94/GPU-monitor.git
cd GPU-monitor

# Install dependencies
pip install flask paramiko

# Start the server
python app.py
```

Open your browser and visit `http://localhost:5050`.

### SSH Configuration

The tool reads from your `~/.ssh/config` file automatically. Make sure your SSH config has entries like:

```
Host gpu-server-01
    HostName 192.168.1.101
    User admin
    Port 22
    IdentityFile ~/.ssh/id_rsa
```

All hosts in your SSH config will be queried for GPU information.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Browser    │────>│  Flask API   │────>│  Remote Servers   │
│  (index.html)│<────│  (app.py)    │<────│  (nvidia-smi)     │
└─────────────┘     └──────────────┘     └──────────────────┘
```

| Component | Description |
|-----------|-------------|
| `index.html` | Single-page frontend with vanilla JS |
| `app.py` | Flask backend with SSH + caching |
| `/api/gpus` | Returns cached GPU data (30s TTL) |
| `/api/refresh` | Forces immediate data refresh |

## GitHub Pages Demo

The [live demo](https://linwei94.github.io/GPU-monitor/) runs with mock data to showcase the dashboard UI. To monitor your own GPUs, deploy the full Flask application on your network.

## License

MIT
