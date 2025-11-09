#!/bin/bash
# TIER-1 SYSTEM OPTIMIZATION FOR MONERO MINING
# Automatically optimizes Linux kernel for maximum mining performance

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🚀 MONERO MINING SYSTEM OPTIMIZATION (ENTERPRISE GRADE)  ║"
echo "╚════════════════════════════════════════════════════════════╝"

# 1. Huge Pages Setup (Critical for RandomX)
echo "[1/6] Enabling 1GB Huge Pages..."
sudo bash -c 'echo "vm.nr_hugepages=9" >> /etc/sysctl.conf' 2>/dev/null || true
sudo bash -c 'echo "vm.nr_overcommit_memory=1" >> /etc/sysctl.conf' 2>/dev/null || true
sudo sysctl -w vm.nr_hugepages=9 2>/dev/null
sudo sysctl -p > /dev/null 2>&1 || true

# 2. CPU Frequency Scaling (Maximize performance)
echo "[2/6] Configuring CPU frequency scaling..."
if command -v cpupower &> /dev/null; then
    sudo cpupower frequency-set -g performance 2>/dev/null || true
elif [ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor ]; then
    for i in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo "performance" | sudo tee $i > /dev/null
    done
fi

# 3. Network Optimization (Reduce latency)
echo "[3/6] Optimizing network parameters..."
sudo bash -c 'cat >> /etc/sysctl.conf << EOF
net.core.somaxconn=65535
net.ipv4.tcp_max_syn_backlog=65535
net.ipv4.ip_local_port_range=1024 65535
net.ipv4.tcp_tw_reuse=1
net.ipv4.tcp_fin_timeout=30
net.core.netdev_max_backlog=65535
EOF' 2>/dev/null || true
sudo sysctl -p > /dev/null 2>&1 || true

# 4. Swap Optimization
echo "[4/6] Configuring swap..."
sudo sysctl -w vm.swappiness=10 2>/dev/null
sudo sysctl -w vm.vfs_cache_pressure=50 2>/dev/null

# 5. Disable Power Management
echo "[5/6] Disabling power management features..."
sudo bash -c 'echo "powersave" > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor' 2>/dev/null || true
for cpu in /sys/devices/system/cpu/cpu*/cpuidle/state*/disable; do
    echo "1" | sudo tee $cpu > /dev/null 2>&1 || true
done

# 6. Monitor settings
echo "[6/6] Setting up monitoring..."
mkdir -p ~/monero-mining/logs

# Check results
echo ""
echo "✓ System Optimization Complete!"
echo ""
echo "Huge Pages:"
grep "nr_hugepages" /proc/sys/vm/nr_hugepages
echo ""
echo "CPU Governor:"
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo "CPU governor management not available"
echo ""
echo "Next step: Run ./start-mining.sh"
