#!/bin/bash
# Stop all mining processes

echo "🛑 Stopping mining services..."

pkill -f xmrig && echo "  ✓ Stopped XMRig" || echo "  - XMRig not running"
pkill -f monerod && echo "  ✓ Stopped Monerod" || echo "  - Monerod not running"
pkill -f "metrics-server" && echo "  ✓ Stopped Metrics" || echo "  - Metrics not running"
pkill -f "mining-dashboard" && echo "  ✓ Stopped Dashboard" || echo "  - Dashboard not running"
pkill -f "telegram-bot" && echo "  ✓ Stopped Telegram Bot" || echo "  - Telegram not running"

echo "✅ All services stopped"
