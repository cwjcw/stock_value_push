# monitor.py

import time
import requests
import schedule
from datetime import datetime
from stock import STOCKS
from project import SEND_KEY, CHECK_INTERVAL_MINUTES

# 保存已提醒记录（如 'sh600519_buy'）
notified_today = set()
last_reset_date = datetime.now().date()

def reset_daily_notifications():
    global notified_today, last_reset_date
    today = datetime.now().date()
    if today != last_reset_date:
        notified_today.clear()
        last_reset_date = today
        print(f"[重置] 清空提醒记录：{today}")

def get_stock_price(stock_code: str) -> float:
    url = f"http://hq.sinajs.cn/list={stock_code}"
    response = requests.get(url)
    response.encoding = 'gbk'
    data = response.text
    try:
        fields = data.split(",")
        price = float(fields[3])  # 当前价是第4项
        return price
    except Exception as e:
        print(f"[错误] 获取 {stock_code} 价格失败: {e}")
        return -1

def send_wechat_notification(title: str, content: str):
    url = f"https://sctapi.ftqq.com/{SEND_KEY}.send"
    data = {"title": title, "desp": content}
    try:
        requests.post(url, data=data)
        print(f"[通知] {title}")
    except Exception as e:
        print(f"[错误] 推送失败: {e}")

def check_all_prices():
    reset_daily_notifications()  # 每次都检查是否需要清空记录

    for code, limits in STOCKS.items():
        current_price = get_stock_price(code)
        if current_price <= 0:
            continue

        print(f"[检查] {code} 当前价格：{current_price}（买入 ≤ {limits['buy_below']}，卖出 ≥ {limits['sell_above']}）")

        # 买入提醒
        if current_price <= limits['buy_below']:
            key = f"{code}_buy"
            if key not in notified_today:
                send_wechat_notification(
                    "📉 买入提醒",
                    f"🔻 {code} 当前价格：{current_price} 元，已低于买入价 {limits['buy_below']} 元，可考虑买入。"
                )
                notified_today.add(key)

        # 卖出提醒
        elif current_price >= limits['sell_above']:
            key = f"{code}_sell"
            if key not in notified_today:
                send_wechat_notification(
                    "📈 卖出提醒",
                    f"🔺 {code} 当前价格：{current_price} 元，已高于卖出价 {limits['sell_above']} 元，可考虑卖出。"
                )
                notified_today.add(key)

# 定时执行
schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_all_prices)

print(f"[启动] 开始监控...每 {CHECK_INTERVAL_MINUTES} 分钟检查一次")
while True:
    schedule.run_pending()
    time.sleep(1)
