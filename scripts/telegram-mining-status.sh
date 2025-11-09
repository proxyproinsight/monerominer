#!/bin/bash
# Elite Mining Status - Telegram Notification Script
# Sends comprehensive mining status updates every 60 minutes

# Source the Telegram configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../telegram.conf"

if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
else
    echo "Error: telegram.conf not found at $CONFIG_FILE"
    exit 1
fi

# Function to send Telegram message
send_telegram() {
    local message="$1"
    curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=${message}" \
        -d "parse_mode=HTML" > /dev/null
}

# Function to fetch JSON from URL
fetch_json() {
    curl -s "$1" 2>/dev/null || echo "{}"
}

# Check if processes are running
xmrig_running=$(pgrep -x xmrig > /dev/null && echo "✅ ONLINE" || echo "❌ OFFLINE")
nextgen_running=$(pgrep -x nextgen-miner > /dev/null && echo "✅ ONLINE" || echo "❌ OFFLINE")

# Get system stats
cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{printf "%.1f%%", 100 - $1}')
mem_stats=$(free -h | grep Mem | awk '{print $3 "/" $2}')
hostname=$(hostname)

# Get Monero stats from config
monero_config="/home/dappy/monero-mining/config.json"
if [[ -f "$monero_config" ]]; then
    monero_wallet=$(jq -r '.pools[0].user // "N/A"' "$monero_config" 2>/dev/null || echo "N/A")
else
    monero_wallet="N/A"
fi

# Fetch Monero stats from MoneroOcean pool
if [[ "$monero_wallet" != "N/A" ]]; then
    # Try XMRig API first for real-time hashrate
    xmrig_api=$(fetch_json "http://127.0.0.1:3001/1/summary" | jq -r --arg token "mining-dashboard" \
        --arg auth "Authorization: Bearer mining-dashboard" '.')
    
    if [[ -n "$xmrig_api" && "$xmrig_api" != "{}" ]]; then
        monero_hashrate=$(echo "$xmrig_api" | jq -r '.hashrate.total[0] // 0' 2>/dev/null || echo "0")
        monero_hashrate=$(printf "%.2f" "$monero_hashrate")
    else
        monero_hashrate="0"
    fi
    
    # Get pool stats from MoneroOcean
    moneroocean_data=$(fetch_json "https://api.moneroocean.stream/miner/${monero_wallet}/stats")
    if [[ -n "$moneroocean_data" && "$moneroocean_data" != "{}" ]]; then
        pool_hashrate=$(echo "$moneroocean_data" | jq -r '.hash // 0' 2>/dev/null || echo "0")
        # Use pool hashrate if available, otherwise use local
        if [[ "$pool_hashrate" != "0" ]]; then
            monero_hashrate="$pool_hashrate"
        fi
        # Convert from piconero to XMR (divide by 1e12)
        monero_balance=$(echo "$moneroocean_data" | jq -r '(.amtDue // 0) / 1000000000000' 2>/dev/null || echo "0")
        monero_balance=$(printf "%.8f" "$monero_balance")
        monero_paid=$(echo "$moneroocean_data" | jq -r '(.amtPaid // 0) / 1000000000000' 2>/dev/null || echo "0")
        monero_paid=$(printf "%.8f" "$monero_paid")
    else
        monero_balance="0"
        monero_paid="0"
    fi
else
    monero_hashrate="N/A"
    monero_balance="0"
    monero_paid="0"
fi

# Format the message
timestamp=$(date "+%Y-%m-%d %H:%M:%S UTC" -u)

message="<b>⚡ ELITE MONERO MINING REPORT ⚡</b>

<b>🔷 Monero (XMRig)</b>
Status: ${xmrig_running}
Pool: MoneroOcean (0% fee)
Hashrate: ${monero_hashrate} H/s
Balance: ${monero_balance} XMR
Total Paid: ${monero_paid} XMR
Minimum Payout: 0.003 XMR
Wallet: <code>${monero_wallet:0:12}...${monero_wallet: -8}</code>

<b>⚙️ System Resources</b>
CPU Usage: ${cpu_usage}
Memory: ${mem_stats}
Host: ${hostname}

<i>📅 ${timestamp}</i>
<i>💰 Next payout: ~2-3 days • Updates every 60 min</i>"

# Send the message
send_telegram "$message"

# Log the notification
echo "[$(date)] Mining status sent to Telegram" >> /home/dappy/monero-mining/logs/telegram-notifications.log
