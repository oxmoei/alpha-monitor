## Alpha Monitor
```
       _   _       _                                _ _             
      /_\ | |_ __ | |__   __ _    /\/\   ___  _ __ (_) |_ ___  _ __ 
     //_\\| | '_ \| '_ \ / _` |  /    \ / _ \| '_ \| | __/ _ \| '__|
    /  _  \ | |_) | | | | (_| | / /\/\ \ (_) | | | | | || (_) | |   
    \_/ \_/_| .__/|_| |_|\__,_| \/    \/\___/|_| |_|_|\__\___/|_|   
            |_|          
```

English | [中文](README.md)

Lightweight listing monitoring toolset:
- Monitors `AddToken` events from Astar Treasury contract, with Telegram push support
- Monitors Binance Alpha new token listings, with Telegram push support       ➡️[Telegram Bot Setup Guide](./创建TelegramBot指南.md)

---

## 📚 Table of Contents
- [🖥️ Supported Platforms](#️-supported-platforms)
- [🚀 Quick Start](#-quick-start)
  - [Linux / WSL / macOS](#1-clone-repository-and-install-dependencies-ensure-you-have-git-installed-if-not-please-refer-to-the-git-installation-tutorial)
  - [Windows](#1-clone-repository-and-install-dependencies-ensure-you-have-git-installed-if-not-please-refer-to-the-git-installation-tutorial-1)
- [⚙️ Feature Overview](#️-feature-overview)
- [❓ FAQ](#-faq)

---

## 🖥️ Supported Platforms

- ![Windows](https://img.shields.io/badge/-Windows-0078D6?logo=windows&logoColor=white)
- ![macOS](https://img.shields.io/badge/-macOS-000000?logo=apple&logoColor=white)
- ![Linux](https://img.shields.io/badge/-Linux-FCC624?logo=linux&logoColor=black)
- ![WSL](https://img.shields.io/badge/-WSL-0078D6?logo=windows&logoColor=white) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;➡️[How to Install WSL2 on Windows](https://medium.com/@cryptoguy_/在-windows-上安装-wsl2-和-ubuntu-a857dab92c3e)

---

## 🚀 Quick Start
🔴 Linux / WSL / macOS Users:

### 1. Clone Repository/Install Dependencies (Ensure you have `git` installed. If not, please refer to ➡️[Git Installation Tutorial](./安装git教程.md))

```bash
# Clone repository and enter project directory
git clone https://github.com/oxmoei/alpha-monitor.git && cd alpha-monitor

# Automatically install missing dependencies and configure environment
./install.sh
```

### 2. Configure Environment Variables

```bash
# Copy example environment file and edit settings
cp .env.example .env && nano .env # Press Ctrl+O to save after editing, Ctrl+X to exit
```

### 3. Usage

Run with Poetry (Recommended):
```bash
# Monitor Aster listings
poetry run python aster_listing_monitor.py
# Or run in background to prevent interruption when closing terminal
nohup poetry run python aster_listing_monitor.py > monitor.log 2>&1 &

# Monitor Binance listings
poetry run python bn_listing_monitor.py
# Or run in background to prevent interruption when closing terminal
nohup poetry run python bn_listing_monitor.py > monitor.log 2>&1 &
```

---

🔴 Windows Users:

### 1. Clone Repository/Install Dependencies (Ensure you have `git` installed. If not, please refer to ➡️[Git Installation Tutorial](./安装git教程.md))

Launch PowerShell as Administrator
```powershell
# Clone repository and enter project directory
git clone https://github.com/oxmoei/alpha-monitor.git
cd alpha-monitor

# Set execution policy for current user and enable TLS 1.2
Set-ExecutionPolicy Bypass -Scope CurrentUser -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072;

# Automatically install missing dependencies and configure environment
.\install_for_wins.ps1
```

### 2. Configure Environment Variables
```powershell
# Copy example environment file
Copy-Item .env.example .env

# Edit settings
notepad .env  # Save and close after editing
```

### 3. Usage

Run with Poetry (Recommended):
```powershell
# Monitor Aster listings
poetry run python aster_listing_monitor.py
# Or run in background to prevent interruption when closing terminal
Start-Process powershell -WindowStyle Hidden -ArgumentList "poetry run python aster_listing_monitor.py"

# Monitor Binance listings
poetry run python bn_listing_monitor.py
# Or run in background to prevent interruption when closing terminal
Start-Process powershell -WindowStyle Hidden -ArgumentList "poetry run python bn_listing_monitor.py"
```

---

### ⚙️ Feature Overview

- `aster_listing_monitor.py`
  - Monitors `AddToken(address,address,bool)` events from Aster Treasury
  - Supported parameters: `--from-block`, `--rpc-wss`, `--rpc-http`, `--poll-interval`, `--pricefeed`
  - Automatically reads `RPC_WSS` / `RPC_HTTP`, Telegram configuration from `.env`
  - Prints and pushes to Telegram (if configured) upon event capture

- `bn_listing_monitor.py`
  - Polls Binance Alpha new token listing API
  - Reads `BN_ALPHA_URL`, `POLL_INTERVAL`, Telegram configuration from `.env`
  - Prints and pushes to Telegram (if configured) when new tokens are detected

---

### ❓ FAQ
- How to configure Telegram push?
  - ➡️[Telegram Bot Setup Guide](./创建TelegramBot指南.md)
- Cannot connect to RPC:
  - Check if `RPC_WSS`/`RPC_HTTP` in `.env` is available
  - Can override with `--rpc-wss`/`--rpc-http` parameters
- Telegram messages not received:
  - Verify `bot_token` and `chat_id` are correct
  - Ensure the bot has joined the target group and has send permissions
