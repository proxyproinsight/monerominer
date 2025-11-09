#!/usr/bin/env python3
"""
Monero Mining Script for Ocean Pool
Easy-to-use Monero miner - make money while you sleep!
"""

import subprocess
import sys
import os
import platform
import json
from pathlib import Path

# Configuration
CONFIG = {
    "pool_url": "pool.hashvault.pro:443",  # Ocean-compatible pool
    "pool_port": 443,
    "wallet_address": "YOUR_WALLET_ADDRESS_HERE",  # Replace with your Monero wallet
    "worker_name": "worker1",
    "threads": None,  # None = auto-detect optimal threads
    "tls": True,
    "algorithm": "rx/0"  # RandomX algorithm for Monero
}

CONFIG_FILE = "mining_config.json"


def load_config():
    """Load configuration from file if it exists"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                loaded_config = json.load(f)
                CONFIG.update(loaded_config)
                print(f"✓ Loaded configuration from {CONFIG_FILE}")
        except Exception as e:
            print(f"⚠ Could not load config file: {e}")
    return CONFIG


def save_config():
    """Save current configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(CONFIG, f, indent=2)
        print(f"✓ Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"⚠ Could not save config file: {e}")


def check_xmrig_installed():
    """Check if XMRig is installed"""
    try:
        # Try to find xmrig in common locations
        possible_paths = [
            "xmrig",
            "./xmrig",
            "/usr/local/bin/xmrig",
            "/usr/bin/xmrig",
            "xmrig/xmrig"
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, 
                                      timeout=5)
                if result.returncode == 0:
                    print(f"✓ Found XMRig at: {path}")
                    return path
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        return None
    except Exception as e:
        print(f"Error checking for XMRig: {e}")
        return None


def print_installation_instructions():
    """Print instructions for installing XMRig"""
    system = platform.system().lower()
    
    print("\n" + "="*60)
    print("XMRig Installation Instructions")
    print("="*60)
    
    if system == "linux":
        print("\nFor Ubuntu/Debian:")
        print("  sudo apt-get update")
        print("  sudo apt-get install git build-essential cmake libuv1-dev libssl-dev libhwloc-dev")
        print("  git clone https://github.com/xmrig/xmrig.git")
        print("  cd xmrig && mkdir build && cd build")
        print("  cmake .. && make -j$(nproc)")
        print("\nOr download pre-built binary:")
        print("  https://github.com/xmrig/xmrig/releases")
        
    elif system == "darwin":  # macOS
        print("\nFor macOS (using Homebrew):")
        print("  brew install xmrig")
        print("\nOr download pre-built binary:")
        print("  https://github.com/xmrig/xmrig/releases")
        
    elif system == "windows":
        print("\nFor Windows:")
        print("  Download pre-built binary from:")
        print("  https://github.com/xmrig/xmrig/releases")
        print("  Extract and place xmrig.exe in this directory")
    
    print("\n" + "="*60)


def setup_wallet():
    """Interactive wallet setup"""
    print("\n" + "="*60)
    print("Wallet Setup")
    print("="*60)
    
    if CONFIG["wallet_address"] == "YOUR_WALLET_ADDRESS_HERE":
        print("\n⚠ No wallet address configured!")
        print("\nYou need a Monero wallet address to receive mining rewards.")
        print("Get one from:")
        print("  - MyMonero (https://mymonero.com)")
        print("  - Official Monero GUI (https://www.getmonero.org/downloads/)")
        print("  - Exchanges like Kraken, Binance, etc.")
        
        wallet = input("\nEnter your Monero wallet address (or press Enter to skip): ").strip()
        if wallet:
            CONFIG["wallet_address"] = wallet
            save_config()
            print("✓ Wallet address saved!")
        else:
            print("⚠ Skipping wallet setup. Please edit mining_config.json later.")
            return False
    else:
        print(f"✓ Wallet configured: {CONFIG['wallet_address'][:10]}...{CONFIG['wallet_address'][-10:]}")
    
    return True


def start_mining(xmrig_path):
    """Start the mining process"""
    if CONFIG["wallet_address"] == "YOUR_WALLET_ADDRESS_HERE":
        print("\n❌ Cannot start mining without a valid wallet address!")
        print("Please run setup first or edit mining_config.json")
        return
    
    # Build XMRig command
    pool_url = f"{CONFIG['pool_url']}"
    user = f"{CONFIG['wallet_address']}.{CONFIG['worker_name']}"
    
    cmd = [
        xmrig_path,
        "-o", pool_url,
        "-u", user,
        "-p", "x",
        "-a", CONFIG["algorithm"],
        "--donate-level", "1"
    ]
    
    if CONFIG["tls"]:
        cmd.append("--tls")
    
    if CONFIG["threads"]:
        cmd.extend(["-t", str(CONFIG["threads"])])
    
    print("\n" + "="*60)
    print("Starting Monero Mining")
    print("="*60)
    print(f"Pool: {pool_url}")
    print(f"Wallet: {CONFIG['wallet_address'][:10]}...{CONFIG['wallet_address'][-10:]}")
    print(f"Worker: {CONFIG['worker_name']}")
    print(f"Algorithm: {CONFIG['algorithm']}")
    print("\nPress Ctrl+C to stop mining")
    print("="*60 + "\n")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n✓ Mining stopped by user")
    except Exception as e:
        print(f"\n❌ Error during mining: {e}")


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                    MONERO MINER                          ║
║              Make Money While You Sleep 💰               ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # Load configuration
    load_config()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            setup_wallet()
            save_config()
            return
        elif command == "config":
            print(f"\nCurrent Configuration:")
            print(json.dumps(CONFIG, indent=2))
            return
        elif command == "help":
            print("\nUsage:")
            print("  python mine.py          - Start mining")
            print("  python mine.py setup    - Configure wallet address")
            print("  python mine.py config   - Show current configuration")
            print("  python mine.py help     - Show this help message")
            return
    
    # Check if XMRig is installed
    xmrig_path = check_xmrig_installed()
    
    if not xmrig_path:
        print("\n❌ XMRig miner not found!")
        print_installation_instructions()
        sys.exit(1)
    
    # Check wallet configuration
    if CONFIG["wallet_address"] == "YOUR_WALLET_ADDRESS_HERE":
        print("\n⚠ Wallet not configured. Running setup...")
        if not setup_wallet():
            sys.exit(1)
    
    # Start mining
    start_mining(xmrig_path)


if __name__ == "__main__":
    main()
