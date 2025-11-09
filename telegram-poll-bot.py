#!/usr/bin/env python3
"""
Telegram Bot Polling Handler for Mining Status
Continuously polls for /start and /status commands
"""
import os
import json
import subprocess
import time
import requests
from pathlib import Path

# Load config
config_file = Path.home() / "monero-mining" / "telegram.conf"
config = {}

if config_file.exists():
    with open(config_file) as f:
        for line in f:
            if line.startswith('#') or '=' not in line:
                continue
            key, value = line.strip().split('=', 1)
            config[key.strip()] = value.strip().strip('"')

BOT_TOKEN = config.get('BOT_TOKEN', '')
CHAT_ID = config.get('CHAT_ID', '')

def get_mining_status():
    """Get current mining status"""
    try:
        xmrig = subprocess.run(['pgrep', '-f', 'xmrig'], capture_output=True).returncode == 0
        xmrig_str = "✅ ONLINE" if xmrig else "❌ OFFLINE"
        
        # Get hashrate and pool info from XMRig API
        hashrate = "N/A"
        pool = "Unknown"
        shares = "0"
        balance = "0"
        
        try:
            import urllib.request
            req = urllib.request.Request("http://127.0.0.1:3001/1/summary")
            req.add_header("Authorization", "Bearer mining-dashboard")
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                hr = data.get('hashrate', {}).get('total', [0])[0]
                hashrate = f"{hr:.1f} H/s" if hr else "N/A"
                pool_url = data.get('connection', {}).get('pool', '')
                if 'moneroocean' in pool_url.lower():
                    pool = "MoneroOcean"
                shares = str(data.get('results', {}).get('shares_good', 0))
        except:
            pass
        
        # Get balance from MoneroOcean
        try:
            wallet = "49KKJwFdsu2SVtXSKQ3XDe2Ly2qsnjniFZhSyCQHiw7rMZo5VUzEy3YWueLK5siepaWpRKzL8vxVT9Dkbpok3kv62EdzT8c"
            resp = requests.get(f"https://api.moneroocean.stream/miner/{wallet}/stats", timeout=3)
            if resp.status_code == 200:
                pool_data = resp.json()
                balance_val = float(pool_data.get('amtDue', 0)) / 1e12
                balance = f"{balance_val:.6f} XMR"
        except:
            pass
        
        msg = f"⛏️ *MONERO MINING STATUS*\n\n"
        msg += f"*XMRig Miner:* {xmrig_str}\n"
        msg += f"*Pool:* {pool} (0% fee)\n"
        msg += f"*Hashrate:* {hashrate}\n"
        msg += f"*Shares:* {shares} accepted\n"
        msg += f"*Balance:* {balance}\n"
        msg += f"*Min Payout:* 0.003 XMR\n\n"
        
        if xmrig:
            msg += "⚡ *STATUS: ACTIVELY MINING*"
        else:
            msg += "❌ *STATUS: Miner offline*"
        
        return msg
    except Exception as e:
        return f"⚠️ Error getting status: {str(e)}"

def send_message(chat_id, text):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        resp = requests.post(url, data=data, timeout=5)
        return resp.status_code == 200
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def poll_updates():
    """Poll for new messages"""
    offset = 0
    # On first start, clear the backlog
    url_init = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        resp = requests.get(url_init, params={'limit': 1}, timeout=5)
        if resp.json().get('result'):
            offset = resp.json()['result'][-1]['update_id'] + 1
    except:
        pass
    
    print(f"🤖 Bot ready! Listening for /start and /status commands...")
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {
                'offset': offset,
                'timeout': 30,
                'allowed_updates': ['message']
            }
            
            resp = requests.get(url, params=params, timeout=35)
            updates = resp.json()
            
            if updates.get('ok'):
                for update in updates.get('result', []):
                    offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        msg = update['message']
                        text = msg.get('text', '').strip()
                        chat_id = msg['chat']['id']
                        
                        if text in ['/start', '/status']:
                            print(f"[{time.strftime('%H:%M:%S')}] Received: {text} from {chat_id}")
                            status = get_mining_status()
                            if send_message(chat_id, status):
                                print(f"[{time.strftime('%H:%M:%S')}] ✅ Status sent!")
                            else:
                                print(f"[{time.strftime('%H:%M:%S')}] ❌ Failed to send")
        
        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    print("🤖 Telegram Mining Bot polling started...")
    poll_updates()
