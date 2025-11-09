#!/bin/bash
# Enable automatic Telegram notifications (every 4 hours)

CONFIG_FILE=~/monero-mining/telegram.conf

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Telegram not configured yet!"
    echo "Run: ~/monero-mining/setup-telegram.sh first"
    exit 1
fi

echo "Setting up automatic notifications..."

# Create cron job for every 4 hours
CRON_CMD="0 */4 * * * /home/dappy/monero-mining/send-status.sh > /dev/null 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "send-status.sh"; then
    echo "⚠️  Automatic notifications already enabled!"
    echo ""
    read -p "Do you want to change the frequency? (y/n): " CHANGE
    if [ "$CHANGE" != "y" ]; then
        exit 0
    fi
    # Remove old cron job
    crontab -l 2>/dev/null | grep -v "send-status.sh" | crontab -
fi

echo ""
echo "How often do you want updates?"
echo "1) Every hour"
echo "2) Every 2 hours"
echo "3) Every 4 hours (recommended)"
echo "4) Every 8 hours"
echo "5) Once daily (9 AM)"
read -p "Choose [1-5]: " FREQ

case $FREQ in
    1)
        CRON_CMD="0 * * * * /home/dappy/monero-mining/send-status.sh > /dev/null 2>&1"
        FREQ_TEXT="every hour"
        ;;
    2)
        CRON_CMD="0 */2 * * * /home/dappy/monero-mining/send-status.sh > /dev/null 2>&1"
        FREQ_TEXT="every 2 hours"
        ;;
    3)
        CRON_CMD="0 */4 * * * /home/dappy/monero-mining/send-status.sh > /dev/null 2>&1"
        FREQ_TEXT="every 4 hours"
        ;;
    4)
        CRON_CMD="0 */8 * * * /home/dappy/monero-mining/send-status.sh > /dev/null 2>&1"
        FREQ_TEXT="every 8 hours"
        ;;
    5)
        CRON_CMD="0 9 * * * /home/dappy/monero-mining/send-status.sh > /dev/null 2>&1"
        FREQ_TEXT="daily at 9 AM"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo ""
echo "✅ Automatic notifications enabled!"
echo "📱 You'll receive updates $FREQ_TEXT"
echo ""
echo "Commands:"
echo "  • Send now: ~/monero-mining/send-status.sh"
echo "  • Disable: crontab -e (remove the line with send-status.sh)"
echo ""

# Send initial notification
source "$CONFIG_FILE"
MSG="✅ *Auto-notifications enabled!*%0A%0AYou'll receive mining status updates $FREQ_TEXT."
curl -s "https://api.telegram.org/bot$BOT_TOKEN/sendMessage?chat_id=$CHAT_ID&text=$MSG&parse_mode=Markdown" > /dev/null

echo "📱 Confirmation sent to Telegram!"
