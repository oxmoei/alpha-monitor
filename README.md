## Alpha Monitor
```
       _   _       _                                _ _             
      /_\ | |_ __ | |__   __ _    /\/\   ___  _ __ (_) |_ ___  _ __ 
     //_\\| | '_ \| '_ \ / _` |  /    \ / _ \| '_ \| | __/ _ \| '__|
    /  _  \ | |_) | | | | (_| | / /\/\ \ (_) | | | | | || (_) | |   
    \_/ \_/_| .__/|_| |_|\__,_| \/    \/\___/|_| |_|_|\__\___/|_|   
            |_|          
```
轻量级上新监听工具集：
- 监听 Astar Treasury 合约的 AddToken 事件，并可推送到 Telegram
- 监听 Binance Alpha 新上架代币列表，并可推送到 Telegram       ➡️[创建TelegramBot指南](./创建TelegramBot指南.md)

---

## 📚 目录
- [🖥️ 支持平台](#️-支持平台)
- [🚀 快速开始](#-快速开始)
  - [Linux / WSL / macOS](#1-克隆仓库安装依赖确保你已安装-git如果未安装请参考安装git教程)
  - [Windows](#1-克隆仓库安装依赖确保你已安装-git如果未安装请参考安装git教程-1)
- [⚙️ 功能概述](#️-功能概述)
- [❓ 常见问题](#-常见问题)

---

## 🖥️ 支持平台

- ![Windows](https://img.shields.io/badge/-Windows-0078D6?logo=windows&logoColor=white)
- ![macOS](https://img.shields.io/badge/-macOS-000000?logo=apple&logoColor=white)
- ![Linux](https://img.shields.io/badge/-Linux-FCC624?logo=linux&logoColor=black)
- ![WSL](https://img.shields.io/badge/-WSL-0078D6?logo=windows&logoColor=white) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;➡️[如何在 Windows 上安装 WSL2](https://medium.com/@cryptoguy_/在-windows-上安装-wsl2-和-ubuntu-a857dab92c3e)

---

## 🚀 快速开始
🔴 Linux /WSL /macOS 用户：

### 1. 克隆仓库/安装依赖（确保你已安装 `git`，如果未安装请参考➡️[安装git教程](./安装git教程.md)）

```bash
# 克隆仓库并进入项目目录
git clone https://github.com/oxmoei/alpha-monitor.git && cd alpha-monitor

# 自动安装缺失的依赖和配置环境
./install.sh
```

### 2. 配置环境变量

```bash
# 复制示例环境文件并编辑设置
cp .env.example .env && nano .env # 编辑完成按 Ctrl+O 保存，Ctrl+X 退出
```

### 3. 使用方法

使用 Poetry 运行（推荐）：
```bash
# 监听Aster上新
poetry run python aster_listing_monitor.py
# 或者后台运行，防止因关闭终端而中断任务
nohup poetry run python aster_listing_monitor.py > monitor.log 2>&1 &

# 监听币安上新
poetry run python bn_listing_monitor.py
# 或者后台运行，防止因关闭终端而中断任务
nohup poetry run python bn_listing_monitor.py > monitor.log 2>&1 &
```

---

🔴 Windows 用户：

### 1. 克隆仓库/安装依赖（确保你已安装 `git`，如果未安装请参考➡️[安装git教程](./安装git教程.md)）

以管理员身份启动 PowerShell
```powershell
# 克隆仓库并进入项目目录
git clone https://github.com/oxmoei/alpha-monitor.git
cd alpha-monitor

# 设置允许当前用户运行脚本和启用 TLS 1.2
Set-ExecutionPolicy Bypass -Scope CurrentUser -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072;

# 自动安装缺失的依赖和配置环境
.\install_for_wins.ps1
```

### 2. 配置环境变量
```powershell
# 复制示例环境文件
Copy-Item .env.example .env

# 编辑设置
notepad .env  # 编辑完成保存、关闭
```

### 3. 使用方法

使用 Poetry 运行（推荐）：
```powershell
# 监听Aster上新
poetry run python aster_listing_monitor.py
# 或者后台运行，防止因关闭终端而中断任务
Start-Process powershell -WindowStyle Hidden -ArgumentList "poetry run python aster_listing_monitor.py"

# 监听币安上新
poetry run python bn_listing_monitor.py
# 或者后台运行，防止因关闭终端而中断任务
Start-Process powershell -WindowStyle Hidden -ArgumentList "poetry run python bn_listing_monitor.py"
```

---

### ⚙️ 功能概述

- `aster_listing_monitor.py`
  - 监听 Aster Treasury 的 `AddToken(address,address,bool)` 事件
  - 支持参数：`--from-block`、`--rpc-wss`、`--rpc-http`、`--poll-interval`、`--pricefeed`
  - 自动从 `.env` 读取 `RPC_WSS` / `RPC_HTTP`、Telegram 配置
  - 捕获事件后打印并推送 Telegram（如配置）

- `bn_listing_monitor.py`
  - 轮询 Binance Alpha 新上架代币列表
  - 从 `.env` 读取 `BN_ALPHA_URL`、`POLL_INTERVAL`、Telegram 配置
  - 发现新代币时打印并推送 Telegram（如配置）

---

### ❓ 常见问题
- 如何配置 Telegram 推送？
  - ➡️[创建TelegramBot指南](./创建TelegramBot指南.md)
- 无法连接 RPC：
  - 检查 `.env` 中的 `RPC_WSS`/`RPC_HTTP` 是否可用
  - 可用 `--rpc-wss`/`--rpc-http` 参数覆盖
- Telegram 未收到消息：
  - 确认 `bot_token` 与 `chat_id` 正确
  - 确保机器人已加入目标群组，且有发送权限


