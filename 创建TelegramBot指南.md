## 创建 Telegram Bot 指南

本指南帮助你从零创建一个 Telegram Bot，并取得在代码中可用的 Token。

### 1. 安装与准备
- 下载并安装 Telegram 客户端（桌面或移动端均可）。
- 登录你的 Telegram 账号，确保可以搜索并与其他用户对话。

### 2. 通过 BotFather 创建 Bot
- 在 Telegram 搜索 `@BotFather` 并开始对话。
- 发送 `/newbot`，按提示输入 Bot 的显示名称和唯一用户名（必须以 `bot` 结尾，如 `my_price_bot`）。
- BotFather 会返回一段以 `:AA...` 结尾的 HTTP API Token。请妥善保存，该 Token 之后用于程序访问。

### 3. 设置 Bot 基础信息（可选）
- `/setdescription` 设置简介；`/setabouttext` 设置 About 文本。
- `/setuserpic` 上传头像，`/setcommands` 配置常用命令列表。

### 4. 选择接收消息方式
- **长轮询（Long Polling）**：适合本地或不固定公网地址的环境，直接用 Telegram HTTP API 轮询获取更新。
- **Webhook**：需要一条可被 Telegram 访问的 HTTPS 地址（域名 + 443 端口 + 有效证书）。可用反向代理或隧道（如 Cloudflare Tunnel、ngrok）暴露本地服务。

### 5. 在代码中使用 Token 示例（Python 轮询）
```python
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "替换为你的_BotFather_令牌"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot 已上线！")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()  # Ctrl+C 结束
```

### 6. Webhook 设置示例（如需）
- 启动你的 HTTPS 服务，并确保外网可达，路径如 `https://your-domain.com/telegram-webhook`.
- 调用 Telegram API 注册 Webhook（将 `<TOKEN>` 与 URL 替换为实际值）：
```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://your-domain.com/telegram-webhook
```
- 如果要改回轮询，先删除 Webhook：
```
https://api.telegram.org/bot<TOKEN>/deleteWebhook
```

### 7. 安全与运营建议
- 不要泄露 Token；可放入环境变量或 `.env` 文件，避免硬编码在仓库。
- 为 Bot 命令添加权限控制或白名单，避免滥用。
- 监控 Bot 报错日志；若使用 Webhook，确保证书未过期。
- 若 Bot 面向公开用户，请在简介中写清用途与联系信息。

完成以上步骤后，即可在本地或服务器上运行你的 Telegram Bot 并开始收发消息。祝开发顺利！
