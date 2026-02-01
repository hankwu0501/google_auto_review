import csv
import os
from datetime import datetime, timedelta
from serpapi import GoogleSearch
import requests

CHANNEL_ACCESS_TOKEN = "SzutDgGTkjHmHxDCwLAeud/8lNDsbKwpD8bWl37ZN8QWBGkWX5QCEK9oZ8eW02CwfH1+dKUI4Qv04ZOkdU3VAmEMA/vxTuWGn9zhHpp7Nj2vTjTagSGlgi4Ccy8DIxW5RonqO739QBVphoRXwq4lhAdB04t89/1O/w1cDnyilFU="
USER_ID = "U8fe13fbdbb8573206a4dd7a4ce2675a8"

def lineNotifyMessage(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "to": USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("訊息發送成功！")
    else:
        print("發送失敗，錯誤碼：", response.status_code)
        print("回應內容：", response.text)

API_KEY = "5aa038b8b48605c32e03ecfd269f09b358528fa8f9869cbf5e546fa1471bb922"

STORES = {
    "板橋": "0x346803e0c12f0111:0x96cf6d00efa6a2e5",
    "民生": "0x3442a937f8b48629:0x489a0788378a066c",
    "新莊": "0x3442a79b5ba0b8df:0x433ad9a3c91cd37",
    "三峽": "0x34681d49492982e9:0xd99c4a0f911f5d0d",
    "蘆洲": "0x3442a92bc792af15:0xf10e6065b0462d19",
    "中和": "0x3442a9d756d4d789:0xd2ab824c3a1a8122",
    "梅花湖": "0x3467e77197a62b11:0xf852610c779dc99d",
}

def get_last_stats_from_files():
    """自動尋找當月或上個月的檔案來讀取最後一筆紀錄"""
    now = datetime.now()
    current_file = f"reviews_{now.strftime('%Y_%m')}.csv"
    
    # 優先找當月的檔案
    if os.path.exists(current_file):
        return read_csv_last_row(current_file), False
    
    # 如果當月還沒產生檔案 (例如 1 號第一次執行)，找上個月的檔案
    last_month = now.replace(day=1) - timedelta(days=1)
    prev_file = f"reviews_{last_month.strftime('%Y_%m')}.csv"
    
    if os.path.exists(prev_file):
        return read_csv_last_row(prev_file), True # True 代表這是跨月了
    
    return {}, False

def read_csv_last_row(filename):
    data = {}
    try:
        with open(filename, mode='r', encoding='utf-8-sig') as f:
            reader = list(csv.DictReader(f))
            if not reader: return data
            # 取得各店最後一筆數據
            for row in reader:
                data[row['店家名稱']] = {
                    'reviews': int(row['評論總數']),
                    'monthly_sum': int(row.get('本月累計增長', 0))
                }
    except Exception as e:
        print(f"讀取 {filename} 失敗: {e}")
    return data

def fetch_and_log():
    now_dt = datetime.now()
    current_filename = f"reviews_{now_dt.strftime('%Y_%m')}.csv"
    
    # 讀取最後一次紀錄 (會自動判斷要讀哪個月的檔案)
    last_stats, is_new_month = get_last_stats_from_files()

    all_data = []
    report_lines = [f"{now_dt.month}/{now_dt.day}"]

    for name, p_id in STORES.items():
        params = {
            "engine": "google_maps_reviews",
            "data_id": p_id,
            "api_key": API_KEY
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            place_info = results.get("place_info", {})
            
            rating = place_info.get("rating", 0)
            current_reviews = place_info.get("reviews", 0)

            # 取得參考數據
            prev = last_stats.get(name, {'reviews': current_reviews, 'monthly_sum': 0})
            
            # 1. 計算「今」：永遠跟最後一次紀錄比 (不論是否跨月)
            today_inc = current_reviews - prev['reviews']
            if today_inc < 0: today_inc = 0
            
            # 2. 計算「共」：如果是新月份的第一筆，重置為今日增量
            if is_new_month:
                monthly_total = today_inc
            else:
                monthly_total = prev['monthly_sum'] + today_inc

            line = f"{rating}{name}{current_reviews}今{today_inc}共{monthly_total}"
            report_lines.append(line)

            all_data.append({
                "時間": now_dt.strftime("%Y-%m-%d %H:%M"),
                "店家名稱": name,
                "平均評分": rating,
                "評論總數": current_reviews,
                "今日增長": today_inc,
                "本月累計增長": monthly_total,
                "Place_ID": p_id
            })

        except Exception as e:
            report_lines.append(f"錯誤: {name} 抓取失敗")

    # 輸出最終字串
    final_report = "\n".join(report_lines)
    print("\n" + final_report + "\n")
    lineNotifyMessage(final_report)

    # 存入當月的 CSV
    save_to_file(current_filename, all_data)

def save_to_file(filename, data_list):
    if not data_list: return
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=data_list[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(data_list)

if __name__ == "__main__":
    fetch_and_log()
