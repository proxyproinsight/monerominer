#!/bin/bash

echo "=== Stopping Monero Mining ==="

# Kill screen sessions if running
screen -S xmrig -X quit 2>/dev/null && echo "Stopped XMRig"
screen -S monerod -X quit 2>/dev/null && echo "Stopped Monerod"

# Fallback: kill by process name
pkill -f xmrig 2>/dev/null
pkill -f monerod 2>/dev/null

echo "Mining stopped"
