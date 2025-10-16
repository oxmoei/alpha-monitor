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
    print("正在尝试创建事件过滤器...")
    try:
        if pricefeed:
            pf = Web3.to_checksum_address(pricefeed)
            print(f"创建带 priceFeed 过滤的过滤器: {pf}")
            flt = contract.events.AddToken.create_filter(fromBlock=from_block, argument_filters={"priceFeed": pf})
        else:
            print("创建通用事件过滤器...")
            flt = contract.events.AddToken.create_filter(fromBlock=from_block)
        
        print("过滤器创建成功，正在测试...")
        # 测试过滤器是否可用
        try:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("过滤器测试超时")
            
            # 设置5秒超时
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(5)
            
            try:
                flt.get_new_entries()
                signal.alarm(0)  # 取消超时
                print("过滤器测试成功，将使用过滤器模式")
                return flt
            except TimeoutError:
                print("过滤器测试超时，将使用轮询模式...")
                return None
            finally:
                signal.alarm(0)  # 确保取消超时
                
        except Exception as e:
            if "filter not found" in str(e):
                print("RPC 不支持事件过滤器，将使用轮询模式...")
                return None
            else:
                print(f"过滤器测试失败: {e}")
                print("将使用轮询模式...")
                return None
    except Exception as e:
        print(f"创建过滤器失败: {e}")
        print("将使用轮询模式...")
        return None

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

def poll_events(w3: Web3, contract, from_block: int, pricefeed: str | None = None):
    """轮询模式：手动获取事件日志"""
    try:
        # 获取当前区块号
        current_block = w3.eth.block_number
        
        # 确保起始区块不超过当前区块
        start_block = min(from_block, current_block)
        
        # 如果起始区块等于当前区块，说明没有新区块，直接返回
        if start_block > current_block:
            return current_block
        
        # 限制区块范围，避免一次性获取太多数据
        if current_block - start_block > 50:
            start_block = current_block - 50
        
        # 确保区块范围有效
        if start_block > current_block:
            return current_block
        
        print(f"轮询区块范围: {start_block} -> {current_block} (共 {current_block - start_block + 1} 个区块)")
        
        # 构建过滤器参数
        filter_params = {
            "fromBlock": start_block,
            "toBlock": current_block,
            "address": TREASURY,
            "topics": [TOPIC0]
        }
        
        # 如果指定了 pricefeed，添加额外的 topic 过滤
        if pricefeed:
            pf = Web3.to_checksum_address(pricefeed)
            # priceFeed 是第二个 indexed 参数，在 topics[2] 位置
            filter_params["topics"].append("0x" + "0" * 24 + pf[2:].lower())
        
        print("正在获取事件日志...")
        logs = w3.eth.get_logs(filter_params)
        print(f"找到 {len(logs)} 个事件日志")
        
        # 处理日志
        for log in logs:
            try:
                currency, price_feed, fixed, txh, blk = process_log(contract, log)
                if currency:
                    print(f"\n🟢 block {blk} | tx {txh}")
                    print(f"currency:     {currency}")
                    print(f"priceFeed:    {price_feed}")
                    print(f"fixedPrice:   {fixed}")
                    
                    # 发送 Telegram 消息
                    tg_bot_token = os.getenv("bot_token")
                    tg_chat_id = os.getenv("chat_id")
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
                
        return current_block  # 返回当前区块号，用于下次轮询
    except Exception as e:
        print(f"轮询事件失败: {e}")
        return None


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
    poll_interval = args.poll_interval if args.poll_interval is not None else 3.0
    
    # 调试信息
    print(f"RPC 类型: {'HTTP' if use_http else 'WebSocket'}")
    print(f"轮询间隔: {poll_interval} 秒")

    backoff = 1.0
    backoff_max = 30.0

    # Telegram 配置（来自 .env 或环境变量），键名：bot_token / chat_id
    tg_bot_token = os.getenv("bot_token")
    tg_chat_id = os.getenv("chat_id")

    # 检查是否使用轮询模式
    use_polling = flt is None
    last_block = None
    
    if use_polling:
        print("使用轮询模式（HTTP RPC 不支持事件过滤器）")
        if from_block == "latest":
            last_block = w3.eth.block_number - 1  # 从上一个区块开始
        else:
            last_block = int(from_block) - 1
        print(f"起始区块: {last_block + 1}")
        # 强制使用3秒间隔进行轮询
        poll_interval = 3.0
        print(f"轮询间隔: {poll_interval} 秒")

    try:
        while True:
            try:
                if use_polling:
                    # 轮询模式
                    current_block_num = w3.eth.block_number
                    print(f"正在轮询新事件... (当前区块: {current_block_num})")
                    
                    # 确保起始区块不超过当前区块
                    start_block = last_block + 1 if last_block is not None else current_block_num
                    if start_block > current_block_num:
                        start_block = current_block_num
                    
                    current_block = poll_events(w3, contract, start_block, args.pricefeed)
                    if current_block:
                        last_block = current_block
                        print(f"轮询完成，等待 {poll_interval} 秒...")
                else:
                    # 过滤器模式
                    print("正在检查新事件...")
                    try:
                        import signal
                        
                        def timeout_handler(signum, frame):
                            raise TimeoutError("获取事件超时")
                        
                        # 设置10秒超时
                        signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(10)
                        
                        try:
                            logs = flt.get_new_entries()
                            signal.alarm(0)  # 取消超时
                            print(f"获取到 {len(logs)} 个新事件")
                            
                            for log in logs:
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
                        except TimeoutError:
                            print("获取事件超时，继续等待...")
                        finally:
                            signal.alarm(0)  # 确保取消超时
                    except Exception as e:
                        if "filter not found" in str(e):
                            print("过滤器不可用，切换到轮询模式...")
                            use_polling = True
                            poll_interval = 3.0  # 强制使用3秒间隔
                            print(f"轮询间隔已设置为: {poll_interval} 秒")
                            if from_block == "latest":
                                last_block = w3.eth.block_number - 1
                            else:
                                last_block = int(from_block) - 1
                            continue
                        else:
                            raise e  # 重新抛出其他异常

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
                if not use_polling:
                    try:
                        flt = make_filter()
                        if flt is None:
                            use_polling = True
                            poll_interval = 3.0  # 强制使用3秒间隔
                            print("切换到轮询模式...")
                            print(f"轮询间隔已设置为: {poll_interval} 秒")
                    except Exception:
                        backoff = min(backoff * 2, backoff_max)
                        continue
    except KeyboardInterrupt:
        print("\n已停止。")

if __name__ == "__main__":
    main()
