#!/usr/bin/env python3
"""Lightweight Monero mining dashboard server.

Serves a single HTML page on port 8888 that combines:
- Local XMRig miner status and hashrate
- System CPU / memory utilisation
- Pool stats from MoneroOcean API

All dependencies are from the Python standard library, so the service can be
managed easily via systemd without extra packages.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

# Path to the miner configuration file
dapp_root = Path("/home/dappy")
MONERO_CONFIG = dapp_root / "monero-mining" / "config.json"

# Default value in case config cannot be read
MONERO_WALLET = ""


def load_wallet() -> None:
    """Load Monero wallet from the miner config."""
    global MONERO_WALLET

    if MONERO_CONFIG.exists():
        try:
            with MONERO_CONFIG.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            pools = data.get("pools", [])
            if pools:
                MONERO_WALLET = pools[0].get("user", "")
        except (json.JSONDecodeError, OSError):
            MONERO_WALLET = ""


load_wallet()


def fetch_json(url: str, timeout: float = 8.0) -> dict:
    """Return decoded JSON from a URL or {} on failure."""
    try:
        req = urllib.request.Request(url)
        # Add access token for XMRig API
        if "127.0.0.1:3001" in url:
            req.add_header("Authorization", "Bearer mining-dashboard")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode("utf-8")
        return json.loads(text)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError):
        return {}


def get_system_stats() -> dict:
    """Return CPU and memory utilisation as simple strings."""
    cpu_usage = subprocess.getoutput(
        "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1}'"
    ).strip()
    if cpu_usage:
        try:
            cpu_usage = f"{float(cpu_usage):.1f}%"
        except ValueError:
            cpu_usage = f"{cpu_usage}%"
    else:
        cpu_usage = "N/A"

    mem_line = subprocess.getoutput("free -h | grep Mem").split()
    mem_percent = subprocess.getoutput("free | grep Mem | awk '{printf \"%.1f\", $3/$2 * 100.0}'").strip()
    if len(mem_line) >= 3:
        mem_used, mem_total = mem_line[2], mem_line[1]
    else:
        mem_used, mem_total = "N/A", "N/A"
    if mem_percent:
        mem_percent = f"{mem_percent}%"
    else:
        mem_percent = "N/A"

    # Detect GPU
    gpu_detected = False
    gpu_info = "No GPU detected"
    
    # Check for NVIDIA GPU
    nvidia_check = subprocess.getoutput("which nvidia-smi 2>/dev/null")
    if nvidia_check:
        nvidia_gpu = subprocess.getoutput("nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null")
        if nvidia_gpu and "NVIDIA" in nvidia_gpu:
            gpu_detected = True
            gpu_info = nvidia_gpu.strip()
    
    # Check for AMD GPU via lspci
    if not gpu_detected:
        amd_check = subprocess.getoutput("lspci | grep -i 'vga\\|3d\\|display' | grep -i 'amd\\|radeon' 2>/dev/null")
        if amd_check:
            gpu_detected = True
            gpu_info = "AMD GPU detected"
    
    # Fallback: check any GPU via lspci
    if not gpu_detected:
        any_gpu = subprocess.getoutput("lspci | grep -i 'vga\\|3d\\|display' 2>/dev/null")
        if any_gpu:
            # Extract first GPU line
            first_line = any_gpu.split('\n')[0] if any_gpu else ""
            if "Intel" not in first_line or "AMD" in any_gpu or "NVIDIA" in any_gpu:
                gpu_info = "Integrated GPU (CPU mining only)"

    return {
        "cpu_usage": cpu_usage,
        "mem_used": mem_used,
        "mem_total": mem_total,
        "mem_percent": mem_percent,
        "gpu_detected": gpu_detected,
        "gpu_info": gpu_info,
    }


def get_process_snapshot(name: str) -> dict:
    """Return basic process info (running flag, CPU%, MEM%)."""
    snapshot = {"running": False, "cpu": "0", "mem": "0"}
    output = subprocess.getoutput(f"ps aux | grep '{name}' | grep -v grep | sort -k3 -nr | head -1")
    if output:
        parts = output.split()
        if len(parts) >= 11:
            snapshot["running"] = True
            snapshot["cpu"] = parts[2]  # %CPU
            snapshot["mem"] = parts[3]  # %MEM
    return snapshot


def get_monero_pool_stats() -> dict:
    """Fetch hashrate / balance from MoneroOcean pool and XMRig API."""
    if not MONERO_WALLET:
        return {"wallet": "Not set", "hashrate": "N/A", "balance": "0", "paid": "0", "workers": "0", "pool": "N/A"}

    # Try XMRig API first for local hashrate
    xmrig_data = fetch_json("http://127.0.0.1:3001/1/summary")
    local_hashrate = "0"
    workers = "1"
    pool_name = "MoneroOcean"
    
    if xmrig_data and "hashrate" in xmrig_data:
        total_hashrate = xmrig_data["hashrate"].get("total", [0])
        local_hashrate = str(total_hashrate[0] if total_hashrate else 0)
        # Count active threads
        threads = xmrig_data.get("hashrate", {}).get("threads", [])
        workers = str(len([t for t in threads if t and t[0] > 0]))
        # Get pool from connection
        connection = xmrig_data.get("connection", {})
        pool_url = connection.get("pool", "")
        if "moneroocean" in pool_url.lower():
            pool_name = "MoneroOcean"

    # Get pool stats from MoneroOcean API
    stats = fetch_json(f"https://api.moneroocean.stream/miner/{MONERO_WALLET}/stats")
    pool_hashrate = local_hashrate  # Default to local
    balance = "0"
    paid = "0"

    if stats:
        # MoneroOcean API structure
        pool_hashrate = str(stats.get("hash", 0) or local_hashrate)
        balance = str(float(stats.get("amtDue", 0) or 0) / 1e12)  # Convert from piconero to XMR
        paid = str(float(stats.get("amtPaid", 0) or 0) / 1e12)

    # Use local hashrate if pool shows 0 (miner just started)
    if pool_hashrate == "0" and local_hashrate != "0":
        pool_hashrate = local_hashrate

    return {
        "wallet": MONERO_WALLET,
        "hashrate": pool_hashrate,
        "balance": balance,
        "paid": paid,
        "workers": workers,
        "pool": pool_name,
    }


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        stats = get_system_stats()
        monero = get_monero_pool_stats()
        xmrig_proc = get_process_snapshot("xmrig")

        monero_status = "🟢 ONLINE" if xmrig_proc["running"] else "🔴 OFFLINE"

        try:
            balance_xmr = float(monero["balance"])
        except ValueError:
            balance_xmr = 0.0
        try:
            paid_xmr = float(monero["paid"])
        except ValueError:
            paid_xmr = 0.0
        try:
            hashrate_float = float(monero["hashrate"])
        except ValueError:
            hashrate_float = 0.0

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>⚡ ELITE MONERO MINING CENTER ⚡</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    background: linear-gradient(135deg, #0078D4 0%, #0063B1 25%, #004B8D 50%, #003666 75%, #002952 100%);
                    background-attachment: fixed;
                    color: #fff; 
                    padding: 20px;
                    min-height: 100vh;
                }}
                .container {{ 
                    max-width: 1200px; 
                    margin: 0 auto; 
                }}
                .header {{
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    padding: 25px 35px;
                    margin-bottom: 25px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.18);
                }}
                h1 {{ 
                    font-size: 2.5em; 
                    font-weight: 300; 
                    letter-spacing: 2px;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
                    margin-bottom: 8px;
                }}
                .subtitle {{
                    font-size: 1.1em;
                    color: #E1F5FF;
                    font-weight: 300;
                    opacity: 0.9;
                }}
                .grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
                    gap: 20px; 
                    margin-bottom: 20px;
                }}
                .card {{ 
                    background: rgba(255, 255, 255, 0.12); 
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2); 
                    border-radius: 15px; 
                    padding: 25px; 
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }}
                .card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
                }}
                .card.xmr {{ 
                    border-left: 4px solid #FF6B35;
                }}
                .card.system {{
                    border-left: 4px solid #4FC3F7;
                }}
                .card-header {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 20px;
                    padding-bottom: 15px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
                }}
                .card-icon {{
                    font-size: 2.5em;
                    margin-right: 15px;
                }}
                h2 {{ 
                    font-size: 1.4em; 
                    font-weight: 400;
                }}
                .status-badge {{
                    display: inline-block;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 0.9em;
                    font-weight: 600;
                    margin: 10px 0;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                }}
                .status-online {{
                    background: linear-gradient(135deg, #4CAF50, #45A049);
                }}
                .status-offline {{
                    background: linear-gradient(135deg, #F44336, #D32F2F);
                }}
                .stat-row {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px 0;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }}
                .stat-row:last-child {{
                    border-bottom: none;
                }}
                .label {{ 
                    text-transform: uppercase; 
                    font-size: 0.75em; 
                    letter-spacing: 1.5px; 
                    color: #B3E5FC;
                    font-weight: 600;
                }}
                .value {{ 
                    font-size: 1.3em; 
                    font-weight: 600;
                    color: #FFFFFF;
                    text-align: right;
                }}
                .value-large {{
                    font-size: 2em;
                    font-weight: 300;
                    color: #FFF;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
                }}
                .wallet-address {{
                    font-family: 'Courier New', monospace;
                    font-size: 0.75em;
                    background: rgba(0, 0, 0, 0.3);
                    padding: 8px;
                    border-radius: 5px;
                    word-break: break-all;
                    margin: 8px 0;
                }}
                footer {{ 
                    text-align: center; 
                    margin-top: 25px;
                    padding: 20px;
                    background: rgba(255, 255, 255, 0.08);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    color: #E1F5FF;
                    font-size: 0.9em;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                }}
                .pulse {{
                    animation: pulse 2s infinite;
                }}
                @keyframes pulse {{
                    0%, 100% {{ opacity: 1; }}
                    50% {{ opacity: 0.7; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚡ ELITE MONERO MINING CENTER ⚡</h1>
                    <div class="subtitle">High-Performance CPU Mining Dashboard</div>
                </div>

                <div class="grid">
                    <div class="card xmr">
                        <div class="card-header">
                            <div class="card-icon">🔷</div>
                            <h2>Monero Miner (XMRig)</h2>
                        </div>
                        <div class="status-badge {'status-online' if xmrig_proc['running'] else 'status-offline'} pulse">
                            {monero_status}
                        </div>
                        <div class="stat-row">
                            <div class="label">Hashrate (10s avg)</div>
                            <div class="value-large">{monero['hashrate']} H/s</div>
                        </div>
                        <div class="stat-row">
                            <div class="label">Active Threads</div>
                            <div class="value">{monero.get('workers', '0')} / 8</div>
                        </div>
                        <div class="stat-row">
                            <div class="label">CPU Usage</div>
                            <div class="value">{xmrig_proc['cpu']}%</div>
                        </div>
                        <div class="stat-row">
                            <div class="label">Memory Usage</div>
                            <div class="value">{xmrig_proc['mem']}%</div>
                        </div>
                        <div class="stat-row">
                            <div class="label">Mining Pool</div>
                            <div class="value" style="font-size: 0.9em;">{monero.get('pool', 'MoneroOcean')}</div>
                        </div>
                        <div class="stat-row">
                            <div class="label">Balance</div>
                            <div class="value">{balance_xmr:.6f} XMR</div>
                        </div>
                        <div class="stat-row">
                            <div class="label">Total Paid</div>
                            <div class="value">{paid_xmr:.6f} XMR</div>
                        </div>
                        <div class="stat-row">
                            <div class="label">Payout Minimum</div>
                            <div class="value" style="font-size: 0.9em;">0.003 XMR</div>
                        </div>
                        <div class="label" style="margin-top: 15px;">Wallet Address</div>
                        <div class="wallet-address">{monero['wallet'] or 'Not configured'}</div>
                    </div>

                    <div class="card system">
                        <div class="card-header">
                            <div class="card-icon">⚙️</div>
                            <h2>System Resources</h2>
                        </div>
                        <div class="stat-row">
                            <div class="label">Total CPU Usage</div>
                            <div class="value-large">{stats['cpu_usage']}</div>
                        </div>
                        <div class="stat-row">
                            <div class="label">Memory Usage</div>
                            <div class="value">{stats['mem_percent']}</div>
                        </div>
                        <div class="stat-row">
                            <div class="label">Memory Details</div>
                            <div class="value">{stats['mem_used']} / {stats['mem_total']}</div>
                        </div>
                        <div class="stat-row">
                            <div class="label">GPU Hardware</div>
                            <div class="value" style="font-size: 0.85em;">{'✅ ' + stats['gpu_info'] if stats.get('gpu_detected') else '❌ ' + stats['gpu_info']}</div>
                        </div>
                        <div class="stat-row">
                            <div class="label">Hostname</div>
                            <div class="value">{os.uname().nodename}</div>
                        </div>
                        <div class="stat-row">
                            <div class="label">Platform</div>
                            <div class="value">Linux</div>
                        </div>
                    </div>
                </div>

                <footer>
                    <div>🔄 Last updated: {timestamp}</div>
                    <div style="margin-top: 8px; opacity: 0.8;">
                        Auto-refresh every 30 seconds • Pool: MoneroOcean (0% fee, 0.003 XMR minimum)
                    </div>
                </footer>
            </div>
            <script>setTimeout(() => window.location.reload(), 30000);</script>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format: str, *args) -> None:  # noqa: D401, ANN001
        """Silence default request logging to keep logs clean."""
        return


def main() -> None:
    host = "0.0.0.0"
    port = 8888
    httpd = HTTPServer((host, port), DashboardHandler)
    print(f"Dashboard running on http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
