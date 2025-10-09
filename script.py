import requests
import time

URL = "https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/cex/alpha/all/token/list"

def get_tokens():
    try:
        r = requests.get(URL, timeout=3)
        r.raise_for_status()
        data = r.json().get("data", [])
        # 直接保存完整信息方便后续展示
        return {item["symbol"]: item for item in data}
    except Exception as e:
        print("请求失败:", e)
        return {}

def main():
    print("启动监听中...（Ctrl+C 退出）")
    old_tokens = get_tokens()
    print(f"初始代币数量: {len(old_tokens)}")

    while True:
        time.sleep(0.15)  # 轮询间隔，可调为 2 秒以更低延迟
        new_tokens = get_tokens()
        print(f'找到代币: {len(new_tokens)}个')
        # 找出新代币
        new_listed = set(new_tokens.keys()) - set(old_tokens.keys())
        # new_listed = set(new_tokens.keys())
        # new_listed = set(new_tokens.keys())
        if new_listed:
            # bsc id 56
            if len(new_listed) > 10:
                raise Exception(f"错误 发现大于10个newListing:{new_listed}")
            print("\n🆕 发现新代币上架:")
            for sym in new_listed:
                info = new_tokens[sym]
                addr = info.get('contractAddress')
                print(f"- 符号: {sym}")
                print(f"  名称: {info.get('name', '-')}")
                print(f"  链ID: {info.get('chainId', '-')}")
                print(f"  合约地址: {addr}")
                print("-" * 40)
                if info.get('chainId') == '56' and addr is not None:
                    pass
                    # 推送消息/买入代币

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
