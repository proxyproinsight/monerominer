#!/usr/bin/env python3
"""
Mining Dashboard Server
Displays real-time Monero mining stats via web interface on port 3001
"""
import os
import json
import subprocess
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime
import threading

class MiningDashboard(BaseHTTPRequestHandler):
    def get_mining_stats(self):
        """Get current mining statistics"""
        try:
            monerod = subprocess.run(['pgrep', '-f', 'monerod'], capture_output=True).returncode == 0
            p2pool = subprocess.run(['pgrep', '-f', 'p2pool'], capture_output=True).returncode == 0
            xmrig = subprocess.run(['pgrep', '-f', 'xmrig'], capture_output=True).returncode == 0
            
            sync_percent = 0
            try:
                result = subprocess.run(['screen', '-r', 'monerod', '-X', 'hardcopy', '/tmp/sync.log'], 
                                      capture_output=True, timeout=2)
                with open('/tmp/sync.log', 'r') as f:
                    content = f.read()
                    if 'Synced' in content:
                        import re
                        match = re.search(r'Synced (\d+)', content)
                        if match:
                            current = int(match.group(1))
                            total = 3536707
                            sync_percent = round(current * 100 / total, 1)
            except:
                pass
            
            return {
                'monerod': monerod,
                'p2pool': p2pool,
                'xmrig': xmrig,
                'sync_percent': sync_percent,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_html().encode())
        
        elif self.path == '/api/stats':
            stats = self.get_mining_stats()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_html(self):
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⛏️ Monero Mining Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Rajdhani', 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }
        
        /* Animated background */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 20% 50%, rgba(255, 140, 0, 0.03) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(0, 200, 255, 0.03) 0%, transparent 50%);
            pointer-events: none;
            z-index: 1;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            position: relative;
            z-index: 2;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: rgba(10, 14, 39, 0.8);
            border: 1px solid rgba(255, 140, 0, 0.3);
            border-radius: 10px;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 30px rgba(255, 140, 0, 0.1);
        }
        
        h1 {
            font-size: 3em;
            background: linear-gradient(45deg, #ff8c00, #ffd700, #00c8ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
            text-shadow: 0 0 30px rgba(255, 140, 0, 0.2);
        }
        
        .subtitle {
            font-size: 0.9em;
            color: #888;
            font-weight: 300;
        }
        
        .back-link {
            display: inline-block;
            margin-top: 15px;
            padding: 10px 20px;
            background: rgba(255, 140, 0, 0.1);
            border: 1px solid rgba(255, 140, 0, 0.3);
            color: #ff8c00;
            text-decoration: none;
            border-radius: 5px;
            transition: all 0.3s;
        }
        
        .back-link:hover {
            background: rgba(255, 140, 0, 0.2);
            border-color: #ff8c00;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, rgba(255, 140, 0, 0.1) 0%, rgba(0, 200, 255, 0.05) 100%);
            border: 1px solid rgba(255, 140, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 20px rgba(255, 140, 0, 0.1);
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, transparent 0%, rgba(255, 140, 0, 0.1) 50%, transparent 100%);
            opacity: 0;
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0%, 100% { opacity: 0; transform: translateX(-100%); }
            50% { opacity: 1; transform: translateX(100%); }
        }
        
        .stat-card:hover {
            background: linear-gradient(135deg, rgba(255, 140, 0, 0.15) 0%, rgba(0, 200, 255, 0.1) 100%);
            border-color: #ff8c00;
            box-shadow: 0 0 30px rgba(255, 140, 0, 0.2);
            transform: translateY(-5px);
        }
        
        .stat-icon {
            font-size: 2.5em;
            margin-bottom: 15px;
            color: #ff8c00;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #888;
            font-weight: 300;
            margin-bottom: 10px;
        }
        
        .stat-value {
            font-size: 2.2em;
            font-weight: 700;
            background: linear-gradient(45deg, #00c8ff, #ff8c00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 15px;
            background: rgba(0, 200, 100, 0.1);
            border: 1px solid rgba(0, 200, 100, 0.3);
            border-radius: 20px;
            font-size: 0.9em;
            margin: 10px 5px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
            animation: pulse 2s infinite;
        }
        
        .status-dot.online {
            background-color: #00c864;
            box-shadow: 0 0 10px #00c864;
        }
        
        .status-dot.offline {
            background-color: #ff3b30;
            box-shadow: 0 0 10px #ff3b30;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .sync-bar {
            background: rgba(0, 200, 255, 0.1);
            border: 1px solid rgba(0, 200, 255, 0.3);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .sync-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 0.95em;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid rgba(0, 200, 255, 0.2);
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00c8ff, #ff8c00);
            transition: width 1s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8em;
            font-weight: 600;
            color: #000;
        }
        
        .controls {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            background: rgba(10, 14, 39, 0.8);
            border: 1px solid rgba(255, 140, 0, 0.3);
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        button {
            padding: 12px 25px;
            margin: 5px;
            background: rgba(255, 140, 0, 0.2);
            border: 1px solid rgba(255, 140, 0, 0.5);
            color: #ff8c00;
            border-radius: 5px;
            cursor: pointer;
            font-family: 'Rajdhani', monospace;
            font-weight: 600;
            transition: all 0.3s;
            font-size: 0.95em;
        }
        
        button:hover {
            background: rgba(255, 140, 0, 0.3);
            border-color: #ff8c00;
            box-shadow: 0 0 15px rgba(255, 140, 0, 0.3);
        }
        
        .timestamp {
            color: #888;
            font-size: 0.9em;
            margin-top: 10px;
        }
        
        .loading {
            color: #00c8ff;
            animation: pulse 1s infinite;
        }
        
        @media (max-width: 768px) {
            h1 { font-size: 2em; }
            .stats-grid { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
            .stat-card { padding: 15px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⛏️ MONERO MINING</h1>
            <div class="subtitle">Real-Time Mining Dashboard</div>
            <a href="http://localhost:8080" class="back-link">← Back to Omega9</a>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Monerod Status</div>
                <div class="stat-icon">🖥️</div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="status-dot" id="monerod-dot"></span>
                    <span id="monerod-status">Checking...</span>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">P2Pool Status</div>
                <div class="stat-icon">🌊</div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="status-dot" id="p2pool-dot"></span>
                    <span id="p2pool-status">Checking...</span>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">XMRig Miner</div>
                <div class="stat-icon">⚡</div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="status-dot" id="xmrig-dot"></span>
                    <span id="xmrig-status">Checking...</span>
                </div>
            </div>
        </div>
        
        <div class="sync-bar">
            <div class="sync-label">
                <span>Blockchain Synchronization</span>
                <span id="sync-percent">0%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="sync-fill" style="width: 0%;">
                    <span id="sync-text">0%</span>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <p style="margin-bottom: 15px; color: #888;">Last updated: <span id="timestamp">--:--:--</span></p>
            <button onclick="updateStats()">🔄 Refresh Now</button>
            <button onclick="openTelegram()">📱 Open Telegram Bot</button>
        </div>
    </div>
    
    <script>
        async function updateStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                // Update status indicators
                const statuses = {
                    'monerod': stats.monerod,
                    'p2pool': stats.p2pool,
                    'xmrig': stats.xmrig
                };
                
                for (const [key, status] of Object.entries(statuses)) {
                    const dot = document.getElementById(key + '-dot');
                    const text = document.getElementById(key + '-status');
                    dot.className = 'status-dot ' + (status ? 'online' : 'offline');
                    text.textContent = status ? '✅ ONLINE' : '❌ OFFLINE';
                }
                
                // Update sync progress
                const syncPercent = stats.sync_percent || 0;
                document.getElementById('sync-percent').textContent = syncPercent + '%';
                document.getElementById('sync-fill').style.width = syncPercent + '%';
                document.getElementById('sync-text').textContent = syncPercent + '%';
                
                // Update timestamp
                const time = new Date().toLocaleTimeString();
                document.getElementById('timestamp').textContent = time;
                
            } catch (error) {
                console.error('Error updating stats:', error);
            }
        }
        
        function openTelegram() {
            window.open('https://t.me/Moneroominerbot', '_blank');
        }
        
        // Update every 3 seconds
        updateStats();
        setInterval(updateStats, 3000);
    </script>
</body>
</html>'''
    
    def log_message(self, format, *args):
        pass  # Suppress logs

if __name__ == '__main__':
    PORT = 3001
    server = HTTPServer(('0.0.0.0', PORT), MiningDashboard)
    print(f"⛏️  Mining Dashboard listening on port {PORT}")
    print(f"🌐 Access at: http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()
