#!/bin/bash

echo "=== Monero Mining Monitor ==="
echo ""

# Check if processes are running
MONEROD=$(pgrep -f monerod)
XMRIG=$(pgrep -f xmrig)

echo "Status:"
if [ -n "$MONEROD" ]; then
    echo "  ✓ Monerod running (PID: $MONEROD)"
else
    echo "  ✗ Monerod NOT running"
fi

if [ -n "$XMRIG" ]; then
    echo "  ✓ XMRig running (PID: $XMRIG)"
else
    echo "  ✗ XMRig NOT running"
fi

echo ""
echo "CPU Usage:"
top -bn1 | grep -E "xmrig|monerod" | grep -v grep

echo ""
echo "Mining Pool: MoneroOcean"
echo "  Pool address: pool.moneroocean.stream:10128"
echo "  Website: https://moneroocean.stream"

echo ""
echo "Hashrate (XMRig):"
if [ -n "$XMRIG" ]; then
    curl -s http://127.0.0.1:8080/1/summary 2>/dev/null | grep -oP '"hashrate":\{"total":\[\K[^]]+' || echo "  API not available (wait for XMRig to start)"
fi

echo ""
echo "Temperature & Power:"
sensors 2>/dev/null | grep -E "Core|Package" || echo "  Install lm-sensors: sudo apt install lm-sensors"

echo ""
echo "Commands:"
echo "  - View XMRig logs:  screen -r xmrig (or check ~/monero-mining/xmrig.log)"
echo "  - Check pool stats: https://moneroocean.stream (search your wallet address)"
echo "  - Stop mining:      ./stop-mining.sh"
