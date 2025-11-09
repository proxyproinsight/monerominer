#!/bin/bash
# TELEGRAM BOT LAUNCHER - Wire up Telegram alerts to mining operations

set -e

MINING_DIR=~/monero-mining
BOT_FILE="$MINING_DIR/telegram-bot-v3-enterprise.py"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  📱 WIRING TELEGRAM BOT TO MINING OPERATIONS              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if bot file exists
if [ ! -f "$BOT_FILE" ]; then
    echo "❌ Bot file not found: $BOT_FILE"
    exit 1
fi

# Make executable
chmod +x "$BOT_FILE"

# Check if already running
if screen -ls | grep -q "telegram"; then
    echo "⚠️  Telegram bot already running"
    echo ""
    echo "View bot:"
    echo "  screen -r telegram"
    echo ""
    exit 0
fi

echo "[1/3] Starting Telegram bot in background..."
screen -dmS telegram python3 "$BOT_FILE"
sleep 2

echo "[2/3] Verifying bot is running..."
if screen -ls | grep -q "telegram"; then
    echo "✅ Telegram bot launched successfully"
else
    echo "❌ Failed to launch bot"
    exit 1
fi

echo "[3/3] Sending test message..."
sleep 2

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          ✅ TELEGRAM BOT CONNECTED & ACTIVE               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📱 Bot Configuration:"
echo "  Chat ID: 918711377"
echo "  Token: 7985955460:AAGzefdC9c9nbEP5wEPN0eoBRhuCxqYRX5s"
echo ""
echo "📊 Features:"
echo "  ✓ Real-time mining status"
echo "  ✓ Low hashrate alerts"
echo "  ✓ High rejection rate alerts"
echo "  ✓ Balance threshold notifications"
echo "  ✓ Miner offline detection"
echo "  ✓ Hourly status reports"
echo ""
echo "📱 View Bot Logs:"
echo "  screen -r telegram"
echo ""
echo "❌ Stop Bot:"
echo "  screen -S telegram -X quit"
echo ""
echo "📝 Full Logs:"
echo "  tail -f $MINING_DIR/logs/telegram_bot.log"
echo ""
