import os
import time
import argparse
from web3 import Web3


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

def get_w3():
    wss = os.getenv("RPC_WSS")
    http = os.getenv("RPC_HTTP", "https://bsc-dataseed.binance.org")  # 你也可以换成 Astar 的 RPC
    if wss:
        return Web3(Web3.WebsocketProvider(wss, websocket_timeout=10))
    return Web3(Web3.HTTPProvider(http, request_kwargs={"timeout": 5}))

def build_filter(w3: Web3, from_block: int | str = "latest", pricefeed: str | None = None):
    topics = [TOPIC0]
    if pricefeed:
        topics = [TOPIC0, None, Web3.to_checksum_address(pricefeed).lower()]
    flt = w3.eth.filter({
        "address": TREASURY,
        "fromBlock": from_block,
        "topics": topics
    })
    return flt

def process_log(w3: Web3, log):
    # 用 ABI 解码（拿到 args）
    contract = w3.eth.contract(address=TREASURY, abi=EVENT_ABI)
    evt = contract.events.AddToken().process_log(log)
    args = evt["args"]
    currency = Web3.to_checksum_address(args["currency"])
    price_feed = Web3.to_checksum_address(args["priceFeed"])
    fixed = bool(args["fixedPrice"])
    txh = log["transactionHash"].hex()
    blk = log["blockNumber"]
    return currency, price_feed, fixed, txh, blk

def main():
    parser = argparse.ArgumentParser(description="监听 Aster Treasury 的 AddToken 事件")
    parser.add_argument("--from-block", default="latest",
                        help='默认 latest')
    parser.add_argument("--pricefeed", help="仅匹配指定的 priceFeed", default=None)
    args = parser.parse_args()

    w3 = get_w3()
    if not w3.is_connected():
        raise RuntimeError("RPC 无法连接，请检查 RPC_WSS / RPC_HTTP")

    # from-block 解析
    from_block = args.from_block
    if from_block != "latest":
        from_block = int(from_block)

    # 构建过滤器
    flt = build_filter(w3, from_block=from_block, pricefeed=args.pricefeed)

    print("开始监听 AddToken 事件（Ctrl+C 退出）")
    print(f"- 合约: {TREASURY}")
    print(f"- 过滤: topic0={TOPIC0}")
    if args.pricefeed:
        print(f"- 仅匹配 priceFeed={Web3.to_checksum_address(args.pricefeed)}")


    try:
        while True:
            for log in flt.get_new_entries():
                try:
                    currency, price_feed, fixed, txh, blk = process_log(w3, log)
                    if currency:
                        print(f"\n🟢 block {blk} | tx {txh}")
                        print(f"currency:     {currency}")
                        print(f"priceFeed:    {price_feed}")
                        # 推送消息/买入代币

                        # buy_with_bnb(
                        #     token_address=currency,
                        #     amount_in_bnb=0.1,
                        #     slippage_percent=10,
                        #     deadline_seconds=60,
                        # )
                except Exception as e:
                    print("解码失败：", e)

            time.sleep(1 if isinstance(w3.provider, Web3.HTTPProvider) else 0.05)
    except KeyboardInterrupt:
        print("\n已停止。")

if __name__ == "__main__":
    main()
