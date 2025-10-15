import os
import time
from datetime import datetime
import requests

# 尝试从 .env 加载环境变量（可选依赖）
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None

URL = os.getenv(
    "BN_ALPHA_URL",
    "https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/cex/alpha/all/token/list",
)
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "0.15"))

def get_tokens():
    try:
        r = requests.get(URL, timeout=5)
        r.raise_for_status()
        data = r.json().get("data", [])
        # 直接保存完整信息方便后续展示
        return {item["symbol"]: item for item in data}
    except Exception as e:
        print("请求失败:", e)
        return {}


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> None:
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass


def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    # 加载 .env（如安装了 python-dotenv）
    if load_dotenv is not None:
        try:
            load_dotenv()
        except Exception:
            pass

    tg_bot_token = os.getenv("bot_token")
    tg_chat_id = os.getenv("chat_id")

    print(f"{ts()} | 启动监听（Ctrl+C 退出）")
    print(f"{ts()} | 目标接口: {URL}")
    old_tokens = get_tokens()
    print(f"{ts()} | 初始代币数量: {len(old_tokens)}")

    last_count = len(old_tokens)
    last_summary_ts = time.time()

    while True:
        time.sleep(POLL_INTERVAL)
        new_tokens = get_tokens()
        current_count = len(new_tokens)

        # 周期性或变更时输出摘要
        if current_count != last_count or (time.time() - last_summary_ts) >= 10:
            print(f"{ts()} | 列表代币数: {current_count}")
            last_count = current_count
            last_summary_ts = time.time()
        # 找出新代币
        new_listed = set(new_tokens.keys()) - set(old_tokens.keys())
        # new_listed = set(new_tokens.keys())
        # new_listed = set(new_tokens.keys())
        if new_listed:
            # bsc id 56
            if len(new_listed) > 10:
                raise Exception(f"错误 发现大于10个newListing:{new_listed}")
            print(f"\n{ts()} | 🆕 发现新代币上架 {len(new_listed)} 个：")
            for sym in new_listed:
                info = new_tokens[sym]
                addr = info.get('contractAddress')
                name = info.get('name', '-')
                chain_id = info.get('chainId', '-')
                print(f"[NEW] {sym} ({name}) | chainId={chain_id} | contract={addr}")
                if info.get('chainId') == '56' and addr is not None:
                    pass
                    # 推送消息/买入代币
                if tg_bot_token and tg_chat_id:
                    message = (
                        f"Binance Alpha 新上架\n"
                        f"symbol: {sym}\n"
                        f"name: {name}\n"
                        f"chainId: {chain_id}\n"
                        f"contract: {addr}"
                    )
                    send_telegram_message(tg_bot_token, tg_chat_id, message)

                    # buy_with_bnb(
                    #     token_address=addr,
                    #     amount_in_bnb=0.2,
                    #     slippage_percent=10,
                    #     deadline_seconds=60,
                    # )
            # 更新缓存
            if len(new_tokens) > 300:
                old_tokens = new_tokens

if __name__ == "__main__":
    main()
