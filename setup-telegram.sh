#!/bin/bash
# Telegram notification configuration for Monero Mining

echo "╔═══════════════════════════════════════════════════════╗"
echo "║     📱 TELEGRAM BOT SETUP                             ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

CONFIG_FILE=~/monero-mining/telegram.conf

# Check if already configured
if [ -f "$CONFIG_FILE" ]; then
    echo "⚠️  Telegram is already configured!"
    echo "Current settings in: $CONFIG_FILE"
    echo ""
    read -p "Do you want to reconfigure? (y/n): " RECONFIG
    if [ "$RECONFIG" != "y" ]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

echo "📋 Step 1: Get your Bot Token from @BotFather"
echo "   (In Telegram: /start @BotFather, then /newbot)"
echo ""
read -p "Enter your Bot Token: " BOT_TOKEN

if [ -z "$BOT_TOKEN" ]; then
    echo "❌ Bot token cannot be empty!"
    exit 1
fi

echo ""
echo "📋 Step 2: Get your Chat ID from @userinfobot"
echo "   (In Telegram: /start @userinfobot)"
echo ""
read -p "Enter your Chat ID: " CHAT_ID

if [ -z "$CHAT_ID" ]; then
    echo "❌ Chat ID cannot be empty!"
    exit 1
fi

# Save configuration
cat > "$CONFIG_FILE" << EOL
# Telegram Bot Configuration
BOT_TOKEN="$BOT_TOKEN"
CHAT_ID="$CHAT_ID"
EOL

chmod 600 "$CONFIG_FILE"

echo ""
echo "✅ Configuration saved to: $CONFIG_FILE"
echo ""

# Test the bot
echo "🧪 Testing Telegram connection..."
TEST_MSG="🎉 Monero Mining Bot Connected!%0A%0A✅ Telegram notifications are now active.%0A⛏️ You'll receive mining updates here."

RESPONSE=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/sendMessage?chat_id=$CHAT_ID&text=$TEST_MSG")

if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "✅ SUCCESS! Test message sent to Telegram!"
    echo ""
    echo "📱 You should see a message in your Telegram now."
    echo ""
    echo "Next steps:"
    echo "  • Run: ~/monero-mining/send-status.sh (manual status)"
    echo "  • Run: ~/monero-mining/enable-auto-notify.sh (automatic updates)"
else
    echo "❌ Failed to send test message."
    echo "Response: $RESPONSE"
    echo ""
    echo "Check your Bot Token and Chat ID and try again."
    exit 1
fi
