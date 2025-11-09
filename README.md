# Monero Mining Setup

**Wallet Address:** `49KKJwFdsu2SVtXSKQ3XDe2Ly2qsnjniFZhSyCQHiw7rMZo5VUzEy3YWueLK5siepaWpRKzL8vxVT9Dkbpok3kv62EdzT8c`

## Hardware
- **CPU:** Intel Core i7-4790 (8 threads @ 3.60GHz)
- **Expected Hashrate:** ~2-3 KH/s
- **Power Draw:** ~100-150W
- **Estimated Earnings:** $0.10-0.30/day (check [WhatToMine](https://whattomine.com))

## Setup

### 1. Install
```bash
cd ~/monero-mining
chmod +x setup.sh
./setup.sh
```

This will:
- Install dependencies (git, cmake, build tools)
- Download and build XMRig (CPU miner)
- Download P2Pool (decentralized pool, 0% fees)
- Download Monero daemon (monerod)

### 2. Start Mining
```bash
chmod +x start-mining.sh
./start-mining.sh
```

Choose option 2 for background mode (recommended).

### 3. Monitor
```bash
chmod +x monitor.sh
./monitor.sh
```

Or view individual components:
- **XMRig:** `screen -r xmrig`
- **P2Pool:** `screen -r p2pool`
- **Monerod:** `screen -r monerod`
- **P2Pool Web UI:** http://localhost:3380

### 4. Stop Mining
```bash
chmod +x stop-mining.sh
./stop-mining.sh
```

## Configuration

### XMRig Config
Located at: `~/monero-mining/config.json`

Key settings:
- **Pool:** 127.0.0.1:3333 (local P2Pool)
- **Threads:** Using all 8 CPU threads
- **Huge Pages:** Enabled for better performance
- **Donate Level:** 1% (default)

### P2Pool Setup
- **Mode:** Mini pool (recommended for <50 KH/s)
- **Host:** Local monerod node
- **Port:** 3333 (stratum), 3380 (web UI)

## Optimization Tips

1. **Enable Huge Pages** (recommended for +20% hashrate):
```bash
sudo sysctl -w vm.nr_hugepages=1280
echo "vm.nr_hugepages=1280" | sudo tee -a /etc/sysctl.conf
```

2. **Monitor Temperature:**
```bash
sudo apt install lm-sensors
sensors
```

3. **Check Power Usage:**
```bash
sudo apt install powertop
sudo powertop
```

4. **CPU Governor (max performance):**
```bash
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

## Expected Performance
- **i7-4790:** ~2,000-3,000 H/s
- **Power:** ~100-150W
- **XMR per day:** ~0.002-0.003 XMR
- **USD per day:** ~$0.10-0.30 (at $100/XMR)

**Note:** First sync takes 12-24 hours for monerod. Mining starts immediately but payouts require blockchain sync.

## Troubleshooting

**Low hashrate?**
- Enable huge pages (see above)
- Check CPU thermal throttling: `sensors`
- Reduce background processes

**P2Pool not connecting?**
- Wait for monerod to sync (check with `screen -r monerod`)
- Verify monerod is running: `pgrep monerod`

**XMRig errors?**
- Check config: `cat ~/monero-mining/config.json`
- View logs: `screen -r xmrig`

## Resources
- [XMRig Docs](https://xmrig.com/docs)
- [P2Pool Guide](https://p2pool.io)
- [Monero Calculator](https://www.cryptocompare.com/mining/calculator/xmr)
