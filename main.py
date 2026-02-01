import csv
import os
from datetime import datetime
from serpapi import GoogleSearch

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

def get_last_stats(filename):
    """讀取最後一次的記錄，用來計算增量"""
    last_data = {}
    if not os.path.exists(filename):
        return last_data
    
    with open(filename, mode='r', encoding='utf-8-sig') as f:
        reader = list(csv.DictReader(f))
        if not reader:
            return last_data
        
        # 取得每一家店最後一筆記錄
        for row in reader:
            last_data[row['店家名稱']] = {
                'reviews': int(row['評論總數']),
                'monthly_sum': int(row.get('本月累計增長', 0))
            }
    return last_data

def fetch_and_log():
    output_file = 'reviews_stats.csv'
    now_dt = datetime.now()
    now_str = now_dt.strftime("%Y-%m-%d %H:%M")
    
    # --- 每月 1 號重置邏輯 ---
    if now_dt.day == 1 and not os.path.exists(f"backup_{now_dt.strftime('%Y%m')}.csv"):
        print("📅 今日為 1 號，重置本月統計資料...")
        if os.path.exists(output_file):
            os.rename(output_file, f"archive_{now_dt.strftime('%Y%m')}_last_month.csv")
    
    last_stats = get_last_stats(output_file)
    all_data = []

    print(f"--- 數據抓取中 ({now_str}) ---")

    for name, p_id in STORES.items():
        params = {
            "engine": "google_maps_reviews",
            "data_id": p_id,
            "api_key": API_KEY
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            print(results)
            place_info = results.get("place_info", {})
            
            rating = place_info.get("rating", 0)
            current_reviews = place_info.get("reviews", 0)

            # 計算「今」與「共」
            last_store_data = last_stats.get(name, {'reviews': current_reviews, 'monthly_sum': 0})
            
            # 今日增加 = 現在總數 - 上次紀錄總數
            today_increase = current_reviews - last_store_data['reviews']
            if today_increase < 0: today_increase = 0 # 防止因 Google 刪評論變成負數
            
            # 本月共計 = 上次的累計 + 今日增加
            total_monthly_increase = last_store_data['monthly_sum'] + today_increase

            # 符合你要求的格式輸出
            # 格式：評分 店名 總數 今X 共X
            print(f"{rating}{name}{current_reviews}今{today_increase}共{total_monthly_increase}")

            all_data.append({
                "時間": now_str,
                "店家名稱": name,
                "平均評分": rating,
                "評論總數": current_reviews,
                "今日增長": today_increase,
                "本月累計增長": total_monthly_increase,
                "Place_ID": p_id
            })

        except Exception as e:
            print(f"錯誤: [{name}] - {e}")

    save_to_file(output_file, all_data)

def save_to_file(filename, data_list):
    if not data_list: return
    file_exists = os.path.isfile(filename)
    keys = data_list[0].keys()
    with open(filename, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        if not file_exists:
            writer.writeheader()
        writer.writerows(data_list)

if __name__ == "__main__":
    fetch_and_log()
