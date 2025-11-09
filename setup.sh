#!/bin/bash
set -e

echo "=== Monero Mining Setup Script ==="
echo "Setting up XMRig for CPU mining with MoneroOcean pool"
echo ""

# Install dependencies
echo "[1/4] Installing dependencies..."
sudo apt update
sudo apt install -y git build-essential cmake libuv1-dev libssl-dev libhwloc-dev wget

# Download and build XMRig
echo "[2/4] Downloading XMRig..."
cd ~/monero-mining
if [ ! -d "xmrig" ]; then
    git clone https://github.com/xmrig/xmrig.git
fi
cd xmrig
mkdir -p build && cd build

echo "[3/4] Building XMRig (this may take a few minutes)..."
cmake .. -DWITH_HWLOC=ON
make -j$(nproc)

# Download Monero daemon (monerod)
echo "[4/4] Downloading Monero daemon..."
LATEST_MONERO=$(curl -s https://api.github.com/repos/monero-project/monero/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")')
wget https://downloads.getmonero.org/cli/linux64 -O monero.tar.bz2
tar -xjf monero.tar.bz2
mv monero-x86_64-linux-gnu-* monero
rm monero.tar.bz2

echo ""
echo "=== Setup Complete! ==="
echo "Next steps:"
echo "1. Run ./start-mining.sh to begin mining"
echo "2. Monitor with: ./monitor.sh"
echo "3. Mining pool: MoneroOcean (pool.moneroocean.stream:10128)"
echo ""
