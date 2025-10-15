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
- 监听 Binance Alpha 新上架代币列表，并可推送到 Telegram

## 🖥️ 支持平台

- ![Windows](https://img.shields.io/badge/-Windows-0078D6?logo=windows&logoColor=white)
- ![macOS](https://img.shields.io/badge/-macOS-000000?logo=apple&logoColor=white)
- ![Linux](https://img.shields.io/badge/-Linux-FCC624?logo=linux&logoColor=black)

## 🔴 Linux/WSL/macOS 用户：

### 1. 克隆仓库/安装依赖（确保你已安装 `git`，如果未安装请参考➡️[安装git教程](./安装git教程.md)）

```bash
# 克隆仓库并进入项目目录
git clone https://github.com/oxmoei/alpha-monitor.git && cd alpha-monitor

# 自动安装缺失的依赖和配置环境
./install.sh
```
### 2. 配置环境变量

编辑 `.env` 文件：

```env
# Aster 监听 RPC（优先使用 WSS）
RPC_WSS=wss://your-wss-endpoint
RPC_HTTP=https://your-http-endpoint

# Binance Alpha API 与轮询间隔（秒）
BN_ALPHA_URL=https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/cex/alpha/all/token/list
POLL_INTERVAL=0.15

# Telegram 推送
bot_token=123456:ABCDEF_your_bot_token
chat_id=123456789
```
说明：
- `RPC_WSS` 存在时优先走 WSS；否则回落到 `RPC_HTTP`
- `POLL_INTERVAL` 用于 `bn_listing_monitor.py` 的轮询间隔
- 命令行参数优先级高于环境变量

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

## 🔴 Windows 用户：

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

同上

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

### ❓ 常见问题

- 无法连接 RPC：
  - 检查 `.env` 中的 `RPC_WSS`/`RPC_HTTP` 是否可用
  - 可用 `--rpc-wss`/`--rpc-http` 参数覆盖
- Telegram 未收到消息：
  - 确认 `bot_token` 与 `chat_id` 正确
  - 确保机器人已加入目标群组，且有发送权限


