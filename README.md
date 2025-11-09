# 💰 Monero Miner - Make Money While You Sleep

Easy-to-use Monero (XMR) mining solution for Ocean Pool. Simple setup, automated mining, passive income generation.

## 🚀 Quick Start

### Prerequisites
- Python 3.6+
- XMRig mining software
- A Monero wallet address

### Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/proxyproinsight/monerominer.git
   cd monerominer
   ```

2. **Install XMRig**
   
   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt-get update
   sudo apt-get install git build-essential cmake libuv1-dev libssl-dev libhwloc-dev
   git clone https://github.com/xmrig/xmrig.git
   cd xmrig && mkdir build && cd build
   cmake .. && make -j$(nproc)
   ```
   
   **macOS:**
   ```bash
   brew install xmrig
   ```
   
   **Windows:**
   - Download from [XMRig Releases](https://github.com/xmrig/xmrig/releases)
   - Extract to the monerominer directory
   
   **Pre-built binaries:**
   - All platforms: https://github.com/xmrig/xmrig/releases

3. **Get a Monero Wallet**
   
   If you don't have a Monero wallet yet, get one from:
   - [MyMonero](https://mymonero.com) - Web/Mobile wallet
   - [Official Monero GUI](https://www.getmonero.org/downloads/) - Desktop wallet
   - Exchanges: Kraken, Binance, etc.

4. **Configure Your Wallet**
   ```bash
   python mine.py setup
   ```
   Enter your Monero wallet address when prompted.

5. **Start Mining!**
   ```bash
   python mine.py
   ```

## 💡 Usage

### Basic Commands

- **Start mining:**
  ```bash
  python mine.py
  ```

- **Setup/configure wallet:**
  ```bash
  python mine.py setup
  ```

- **View configuration:**
  ```bash
  python mine.py config
  ```

- **Help:**
  ```bash
  python mine.py help
  ```

### Advanced Configuration

Edit `mining_config.json` to customize:

```json
{
  "pool_url": "pool.hashvault.pro:443",
  "pool_port": 443,
  "wallet_address": "YOUR_WALLET_ADDRESS",
  "worker_name": "worker1",
  "threads": null,
  "tls": true,
  "algorithm": "rx/0"
}
```

**Configuration Options:**
- `pool_url`: Mining pool address
- `wallet_address`: Your Monero wallet for receiving rewards
- `worker_name`: Identifier for this mining machine
- `threads`: Number of CPU threads (null = auto-detect)
- `tls`: Enable TLS encryption
- `algorithm`: Mining algorithm (rx/0 for Monero RandomX)

## 🌙 Run While You Sleep

### Linux/macOS - Run in Background
```bash
# Start mining in background
nohup python mine.py > mining.log 2>&1 &

# Check if it's running
ps aux | grep mine.py

# Stop mining
pkill -f mine.py
```

### Linux - Run as Systemd Service (Recommended)
For automatic startup and better process management:

1. Edit `monerominer.service`:
   - Replace `YOUR_USERNAME` with your username
   - Replace `/path/to/monerominer` with actual path

2. Install the service:
   ```bash
   sudo cp monerominer.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable monerominer
   sudo systemctl start monerominer
   ```

3. Manage the service:
   ```bash
   # Check status
   sudo systemctl status monerominer
   
   # View logs
   sudo journalctl -u monerominer -f
   
   # Stop service
   sudo systemctl stop monerominer
   
   # Disable autostart
   sudo systemctl disable monerominer
   ```

### Windows - Run as Background Task
```cmd
# Start mining in background
start /B python mine.py > mining.log

# Or use Task Scheduler to run on startup
```

### Docker (Optional)
```bash
# Build Docker image
docker build -t monerominer .

# Run container
docker run -d --name miner monerominer
```

## 📊 Monitoring

### Check Mining Status
- Mining output is displayed in real-time
- Check hashrate, accepted shares, and pool connection
- View logs: `tail -f mining.log` (if running in background)

### Pool Dashboard
- Visit your pool's website
- Enter your wallet address to view:
  - Current hashrate
  - Pending balance
  - Payment history

## 💸 Getting Paid

- Mining rewards are automatically sent to your wallet address
- Payment threshold varies by pool (typically 0.1-0.3 XMR)
- Check your wallet for received payments
- Payments usually process every few hours or daily

## ⚡ Performance Tips

1. **Optimize CPU Usage:**
   - Set `threads` to your CPU core count minus 1-2
   - Example: 8-core CPU → use 6 threads

2. **Reduce Power Usage:**
   - Lower thread count for better efficiency
   - Enable power-saving features in BIOS

3. **Cooling:**
   - Ensure good ventilation
   - Monitor CPU temperatures
   - Consider thermal throttling settings

4. **24/7 Mining:**
   - Use dedicated hardware if possible
   - Monitor system stability
   - Set up automatic restart on crashes

## 🔒 Security Notes

- Never share your private keys or seed phrase
- Only your public wallet address is needed for mining
- Use official XMRig releases only
- Keep your wallet software updated
- Consider using a dedicated mining wallet

## ❓ Troubleshooting

### XMRig Not Found
- Install XMRig following the installation instructions
- Ensure xmrig binary is in PATH or current directory

### Mining Not Starting
- Verify wallet address is configured
- Check internet connection
- Ensure pool URL is correct
- Check firewall isn't blocking connections

### Low Hashrate
- Check CPU usage (should be high during mining)
- Verify thread count is optimized
- Ensure no other heavy processes running
- Consider hardware limitations

### Connection Issues
- Try different pool URL
- Check TLS setting matches pool requirements
- Verify pool is operational

## 📈 Expected Earnings

Mining profitability depends on:
- Your CPU performance (hashrate)
- Electricity costs
- Monero price
- Network difficulty

Use calculators to estimate:
- [MoneroOcean Calculator](https://moneroocean.stream/)
- [CryptoCompare Calculator](https://www.cryptocompare.com/mining/calculator/)

**Note:** Home CPU mining typically generates modest returns. Consider it passive income rather than primary income.

## 🤝 Contributing

Contributions welcome! Feel free to:
- Submit bug reports
- Suggest features
- Improve documentation
- Share optimization tips

## ⚖️ Legal & Disclaimer

- Cryptocurrency mining may be subject to regulations in your jurisdiction
- Check local laws before mining
- Be aware of electricity costs vs. mining returns
- This software is provided as-is without warranties
- Use at your own risk

## 📜 License

MIT License - Feel free to use and modify

## 🔗 Resources

- [Monero Official Site](https://www.getmonero.org/)
- [XMRig Documentation](https://xmrig.com/docs)
- [Monero Reddit](https://www.reddit.com/r/Monero/)
- [Mining Pools List](https://miningpoolstats.stream/monero)

---

**Happy Mining! Make that money while you sleep! 💰🌙** 
