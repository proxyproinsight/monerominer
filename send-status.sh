#!/bin/bash
# Send mining status to Telegram

CONFIG_FILE=~/monero-mining/telegram.conf

# Check if configured
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Telegram not configured yet!"
    exit 1
fi

# Load config
source "$CONFIG_FILE"

# Get current sync status
screen -r monerod -X hardcopy /tmp/sync_status.log 2>/dev/null
CURRENT=$(grep "Synced" /tmp/sync_status.log | tail -1 | grep -oP 'Synced \K[0-9]+' | head -1)
TOTAL=3536707

if [ -z "$CURRENT" ]; then
    CURRENT=0
fi

PERCENT=$(echo "scale=1; $CURRENT * 100 / $TOTAL" | bc)
REMAINING=$((TOTAL - CURRENT))

# Check processes
MONEROD_OK=$(pgrep -f monerod > /dev/null && echo "Yes" || echo "No")
XMRIG_OK=$(pgrep -f xmrig > /dev/null && echo "Yes" || echo "No")

# Build simple message
MSG="MONERO MINING UPDATE%0A%0A"
MSG+="Blockchain Sync: ${PERCENT}%%%0A"
MSG+="Blocks: ${CURRENT} of ${TOTAL}%0A"
MSG+="Remaining: ${REMAINING}%0A%0A"
MSG+="Monerod: ${MONEROD_OK}%0A"
MSG+="XMRig: ${XMRIG_OK}%0A"
MSG+="Pool: MoneroOcean%0A%0A"

if [ $(echo "$PERCENT >= 99" | bc) -eq 1 ]; then
    MSG+="STATUS: MINING ACTIVE"
else
    MSG+="STATUS: Syncing blockchain"
fi

# Send to Telegram
RESPONSE=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/sendMessage?chat_id=$CHAT_ID&text=$MSG")

if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "✅ Status sent to Telegram!"
else
    echo "❌ Failed to send"
fi
