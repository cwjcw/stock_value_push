import requests

def get_price_from_tx(stock_code: str) -> float:
    # 腾讯接口使用 sh、sz，不用特殊处理
    url = f"https://qt.gtimg.cn/q={stock_code}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    print("返回内容：", response.text)
    try:
        fields = response.text.split("~")
        current_price = float(fields[3])  # 第4个字段是当前价格
        return current_price
    except Exception as e:
        print("解析失败：", e)
        return -1

# 示例：贵州茅台 sh600519
price = get_price_from_tx("sz000981")
print(f"腾讯财经 当前价格：{price}")
