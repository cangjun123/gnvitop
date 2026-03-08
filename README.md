# gnvitop

**Global nvitop** -- a web-based GPU monitoring dashboard that monitors **all** your remote GPU servers from a single page.
![Uploading 960cd5fae22199ece06060e7ec8862a4.jpg…]()

Like [nvitop](https://github.com/XuehaiPan/nvitop), but for **all your servers at once**, displayed as a beautiful web dashboard.

```
pip install gnvitop
gnvitop
```

## How It Works

1. Reads your `~/.ssh/config` automatically
2. SSH into each server and runs `nvidia-smi`
3. Displays everything in a real-time web dashboard
4. Auto-refreshes every 30 seconds

```
                          ┌──> Server A (nvidia-smi) ──> 4x A100
gnvitop ──> Browser ──>  ├──> Server B (nvidia-smi) ──> 8x V100
                          ├──> Server C (nvidia-smi) ──> 2x RTX 4090
                          └──> Server D ──> offline
```

## Installation

```bash
pip install gnvitop
```

## Usage

```bash
gnvitop                              # start and auto-open browser
gnvitop -p 8080                      # custom port
gnvitop --host 0.0.0.0              # expose to LAN
gnvitop --no-browser                 # don't auto-open browser
gnvitop --ssh-config /path/to/config # custom SSH config
gnvitop -v                           # show version
```

Or run as a module:

```bash
python -m gnvitop
```

## Prerequisites

1. **SSH config** -- your `~/.ssh/config` should have server entries:

```
Host gpu-server-01
    HostName 192.168.1.101
    User alice
    IdentityFile ~/.ssh/id_rsa

Host gpu-server-02
    HostName 192.168.1.102
    User bob
```

2. **SSH key auth** -- password-less login should be set up
3. **nvidia-smi** -- must be installed on the remote servers

## Features

- **Zero config** -- reads `~/.ssh/config` automatically, no setup needed
- **One command** -- `pip install gnvitop && gnvitop`, that's it
- **Auto browser** -- opens dashboard in your browser on start
- **Real-time** -- 30s auto-refresh with manual refresh button
- **Concurrent** -- queries all servers in parallel (10 workers)
- **Cached** -- 30s cache to avoid hammering your servers
- **Dark UI** -- clean, responsive dark-themed dashboard
- **At a glance** -- summary bar shows online hosts, total GPUs, idle GPUs, free memory
- **Color coded** -- green (online), yellow (no GPU), red (offline)
- **GPU details** -- utilization bars, memory bars, temperature with color alerts

## Comparison with nvitop

| Feature | nvitop | gnvitop |
|---------|--------|---------|
| Monitor local GPU | Yes | No |
| Monitor remote GPUs | No | Yes |
| Multiple servers | No | Yes |
| Interface | Terminal | Web browser |
| Setup | Run on each server | Run once, reads SSH config |

**gnvitop** is not a replacement for nvitop -- it's a complement. Use nvitop for detailed local GPU monitoring, use gnvitop to get an overview of all your GPU servers from one place.

## License

MIT
