# gnvitop

**Global nvitop** --- a web-based GPU monitoring dashboard that monitors **all** your remote GPU servers from a single page.
![960cd5fae22199ece06060e7ec8862a4](https://github.com/user-attachments/assets/2ca35564-c891-4af9-9b30-5ebb0949ba99)


Like [nvitop](https://github.com/XuehaiPan/nvitop), but for **all your servers at once**, displayed as a beautiful web dashboard.

```
pip install gnvitop
gnvitop
```

## How It Works

1. Monitors **local GPU** automatically (no config needed)
2. Reads your `~/.ssh/config` and SSH into each remote server
3. Runs `nvidia-smi` to collect GPU stats and **per-GPU process/user info**
4. Displays everything in a real-time web dashboard with **current user highlight**
5. Auto-refreshes every 30 seconds

```
                          ┌──> localhost (nvidia-smi) ──> Local GPUs
gnvitop ──> Browser ──>  ├──> Server A (nvidia-smi) ──> 4x A100
                          ├──> Server B (nvidia-smi) ──> 8x V100
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
- **Local + Remote** -- monitors local GPU alongside all remote servers
- **Per-GPU users** -- shows which users occupy each GPU and their memory usage
- **User highlight** -- your own processes are highlighted in blue for quick identification
- **Auto browser** -- opens dashboard in your browser on start
- **Real-time** -- 30s auto-refresh with manual refresh button
- **Concurrent** -- queries all servers in parallel (10 workers)
- **Cached** -- 30s cache to avoid hammering your servers
- **Dark UI** -- clean, responsive dark-themed dashboard
- **At a glance** -- summary bar shows online hosts, total GPUs, idle GPUs, free memory
- **Color coded** -- green (online), yellow (no GPU), red (offline), blue (local)
- **GPU details** -- utilization bars, memory bars, temperature with color alerts

## Comparison with nvitop

| Feature | nvitop | gnvitop |
|---------|--------|---------|
| Monitor local GPU | Yes | Yes |
| Monitor remote GPUs | No | Yes |
| Multiple servers | No | Yes |
| Show per-GPU users | Yes | Yes |
| Highlight current user | No | Yes |
| Interface | Terminal | Web browser |
| Setup | Run on each server | Run once, reads SSH config |

**gnvitop** is not a replacement for nvitop -- it's a complement. Use nvitop for detailed local process-level GPU monitoring, use gnvitop to get an overview of all your GPU servers (including local) from one place.

## License

MIT
