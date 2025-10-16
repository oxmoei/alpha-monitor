import os
import time
import argparse
from web3 import Web3
import requests

# 尝试从 .env 加载环境变量（如 RPC_WSS / RPC_HTTP）
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None  # 可选依赖，不存在则忽略


TREASURY = Web3.to_checksum_address("0x128463a60784c4d3f46c23af3f65ed859ba87974")

# event AddToken(address indexed currency, address indexed priceFeed, bool fixedPrice)
EVENT_ABI = [{
    "anonymous": False,
    "inputs": [
        {"indexed": True,  "internalType": "address", "name": "currency",   "type": "address"},
        {"indexed": True,  "internalType": "address", "name": "priceFeed",  "type": "address"},
        {"indexed": False, "internalType": "bool",    "name": "fixedPrice", "type": "bool"},
    ],
    "name": "AddToken",
    "type": "event",
}]

# keccak256("AddToken(address,address,bool)")
TOPIC0 = "0x5e44b8d769cde64991e4725cd0276d385af04c64b64cba70267e0ed4d42350a0"

DEFAULT_HTTP_RPC = "https://bsc-dataseed.binance.org"  # 可替换为 Astar RPC

def get_w3(rpc_wss: str | None = None, rpc_http: str | None = None) -> Web3:
    wss = rpc_wss or os.getenv("RPC_WSS")
    http = rpc_http or os.getenv("RPC_HTTP", DEFAULT_HTTP_RPC)
    if wss:
        return Web3(Web3.WebsocketProvider(wss, websocket_timeout=10))
    return Web3(Web3.HTTPProvider(http, request_kwargs={"timeout": 5}))

def build_filter(w3: Web3, contract, from_block: int | str = "latest", pricefeed: str | None = None):
    # 使用 ABI 级过滤，避免自行编码 topic 地址错误
    if pricefeed:
        pf = Web3.to_checksum_address(pricefeed)
        return contract.events.AddToken.create_filter(fromBlock=from_block, argument_filters={"priceFeed": pf})
    return contract.events.AddToken.create_filter(fromBlock=from_block)

def process_log(contract, log):
    # 用 ABI 解码（拿到 args）
    evt = contract.events.AddToken().process_log(log)
    args = evt["args"]
    currency = Web3.to_checksum_address(args["currency"])
    price_feed = Web3.to_checksum_address(args["priceFeed"])
    fixed = bool(args["fixedPrice"])
    txh = log["transactionHash"].hex()
    blk = log["blockNumber"]
    return currency, price_feed, fixed, txh, blk


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> None:
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=5)
    except Exception as _:
        # 忽略发送失败，避免中断主循环
        pass

def main():
    # 优先从 .env 载入（若安装了 python-dotenv）
    if load_dotenv is not None:
        try:
            # 默认加载当前工作目录下的 .env
            load_dotenv()
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="监听 Aster Treasury 的 AddToken 事件")
    parser.add_argument("--from-block", default="latest", help='默认 latest，或指定区块号')
    parser.add_argument("--pricefeed", help="仅匹配指定的 priceFeed", default=None)
    parser.add_argument("--rpc-http", help="HTTP RPC 覆盖（优先级低于 --rpc-wss）", default=None)
    parser.add_argument("--rpc-wss", help="WebSocket RPC 覆盖（优先）", default=None)
    parser.add_argument("--poll-interval", type=float, default=None, help="轮询间隔秒（HTTP 推荐 1s；WSS 可更小）")
    args = parser.parse_args()

    w3 = get_w3(args.rpc_wss, args.rpc_http)
    if not w3.is_connected():
        raise RuntimeError("RPC 无法连接，请检查 --rpc-wss/--rpc-http 或 RPC_WSS/RPC_HTTP")

    # 解析 from-block
    from_block: int | str
    if args.from_block == "latest":
        from_block = "latest"
    else:
        try:
            from_block = int(args.from_block)
        except ValueError:
            raise SystemExit("--from-block 需为 'latest' 或整数区块号")

    # 预构建合约实例与过滤器
    contract = w3.eth.contract(address=TREASURY, abi=EVENT_ABI)

    def make_filter():
        return build_filter(w3, contract, from_block=from_block, pricefeed=args.pricefeed)

    flt = make_filter()

    print("开始监听 AddToken 事件（Ctrl+C 退出）")
    print(f"- 合约: {TREASURY}")
    print(f"- 过滤: topic0={TOPIC0}")
    if args.pricefeed:
        print(f"- 仅匹配 priceFeed={Web3.to_checksum_address(args.pricefeed)}")

    use_http = isinstance(w3.provider, Web3.HTTPProvider)
    poll_interval = args.poll_interval if args.poll_interval is not None else (1.0 if use_http else 0.05)

    backoff = 1.0
    backoff_max = 30.0

    # Telegram 配置（来自 .env 或环境变量），键名：bot_token / chat_id
    tg_bot_token = os.getenv("bot_token")
    tg_chat_id = os.getenv("chat_id")

    try:
        while True:
            try:
                for log in flt.get_new_entries():
                    try:
                        currency, price_feed, fixed, txh, blk = process_log(contract, log)
                        if currency:
                            print(f"\n🟢 block {blk} | tx {txh}")
                            print(f"currency:     {currency}")
                            print(f"priceFeed:    {price_feed}")
                            print(f"fixedPrice:   {fixed}")
                            # 这里可以加入推送/自动交易逻辑
                            if tg_bot_token and tg_chat_id:
                                message = (
                                    f"Aster AddToken 事件\n"
                                    f"block: {blk}\n"
                                    f"tx: {txh}\n"
                                    f"currency: {currency}\n"
                                    f"priceFeed: {price_feed}\n"
                                    f"fixedPrice: {fixed}"
                                )
                                send_telegram_message(tg_bot_token, tg_chat_id, message)
                    except Exception as e:
                        print("解码失败：", e)

                time.sleep(poll_interval)
                backoff = 1.0  # 成功则重置退避
            except Exception as e:
                print(f"轮询失败，将在 {backoff:.1f}s 后重试：{e}")
                time.sleep(backoff)
                # 尝试重连与重建过滤器
                w3 = get_w3(args.rpc_wss, args.rpc_http)
                if not w3.is_connected():
                    backoff = min(backoff * 2, backoff_max)
                    continue
                contract = w3.eth.contract(address=TREASURY, abi=EVENT_ABI)
                try:
                    flt = make_filter()
                except Exception:
                    backoff = min(backoff * 2, backoff_max)
                    continue
    except KeyboardInterrupt:
        print("\n已停止。")

if __name__ == "__main__":
    main()
