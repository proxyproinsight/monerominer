#!/bin/bash
set -e

WALLET="49KKJwFdsu2SVtXSKQ3XDe2Ly2qsnjniFZhSyCQHiw7rMZo5VUzEy3YWueLK5siepaWpRKzL8vxVT9Dkbpok3kv62EdzT8c"
MINING_DIR=~/monero-mining

echo "=== Starting Monero Mining with MoneroOcean ==="
echo ""

# Check if setup was completed
if [ ! -f "$MINING_DIR/xmrig/build/xmrig" ]; then
    echo "Error: XMRig not found. Run ./setup.sh first!"
    exit 1
fi

# Create systemd service files or use screen/tmux
echo "Choose your mining mode:"
echo "1) Foreground (all in one terminal, Ctrl+C to stop)"
echo "2) Background (using screen sessions)"
read -p "Enter choice [1-2]: " CHOICE

case $CHOICE in
    1)
        echo ""
        echo "Starting Monero daemon..."
        cd $MINING_DIR/monero
        ./monerod --zmq-pub tcp://127.0.0.1:18083 --disable-dns-checkpoints --enable-dns-blocklist --out-peers 16 --in-peers 32 &
        MONEROD_PID=$!
        
        echo "Waiting for monerod to sync (this takes time on first run)..."
        sleep 10
        
        echo "Starting XMRig miner connected to MoneroOcean pool..."
        cd $MINING_DIR/xmrig/build
        sudo ./xmrig --config=$MINING_DIR/config.json
        
        # Cleanup on exit
        kill $MONEROD_PID 2>/dev/null
        ;;
    2)
        # Check if screen is installed
        if ! command -v screen &> /dev/null; then
            echo "Installing screen..."
            sudo apt install -y screen
        fi
        
        echo "Starting monerod in screen session 'monerod'..."
        screen -dmS monerod bash -c "cd $MINING_DIR/monero && ./monerod --zmq-pub tcp://127.0.0.1:18083 --disable-dns-checkpoints --enable-dns-blocklist --out-peers 16 --in-peers 32"
        
        echo "Waiting for monerod to initialize..."
        sleep 15
        
        echo "Starting XMRig in screen session 'xmrig'..."
        screen -dmS xmrig bash -c "cd $MINING_DIR/xmrig/build && sudo ./xmrig --config=$MINING_DIR/config.json"
        
        echo ""
        echo "=== Mining Started in Background ==="
        echo "View sessions:"
        echo "  - Monerod: screen -r monerod"
        echo "  - XMRig:   screen -r xmrig"
        echo ""
        echo "Detach from screen: Ctrl+A then D"
        echo "Stop mining: ./stop-mining.sh"
        echo "Monitor: ./monitor.sh"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
