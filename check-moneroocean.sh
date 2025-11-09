#!/bin/bash
# Quick MoneroOcean mining status checker

WALLET="49KKJwFdsu2SVtXSKQ3XDe2Ly2qsnjniFZhSyCQHiw7rMZo5VUzEy3YWueLK5siepaWpRKzL8vxVT9Dkbpok3kv62EdzT8c"

echo "========================================"
echo "   MONEROOCEAN MINING STATUS"
echo "========================================"
echo

# Get local XMRig stats
if curl -s "http://127.0.0.1:3001/1/summary" -H "Authorization: Bearer mining-dashboard" >/dev/null 2>&1; then
    curl -s "http://127.0.0.1:3001/1/summary" -H "Authorization: Bearer mining-dashboard" | python3 -c "
import sys, json
d = json.load(sys.stdin)
hr = d['hashrate']['total']
uptime = d['uptime']
shares_good = d.get('results', {}).get('shares_good', 0)
shares_total = d.get('results', {}).get('shares_total', 0)
hr0 = hr[0] if hr[0] else 0
hr1 = hr[1] if hr[1] else 0
hr2 = hr[2] if hr[2] else 0

print(f'''📊 LOCAL MINER:
  Hashrate: {hr0:.2f} H/s (1m: {hr1:.2f}, 15m: {hr2:.2f})
  Uptime: {uptime//3600}h {(uptime%3600)//60}m
  Shares: {shares_good} accepted, {shares_total - shares_good} rejected
  Pool: gulf.moneroocean.stream
''')
"
else
    echo "❌ XMRig API not responding (is miner running?)"
fi

echo
echo "🌐 POOL DASHBOARD:"
echo "   https://moneroocean.stream/?address=${WALLET:0:20}..."
echo
echo "💰 Check your balance and payouts at the link above!"
echo "   Minimum payout: 0.003 XMR (~2-3 days)"
echo
echo "========================================"
