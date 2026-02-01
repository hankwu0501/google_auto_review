import csv
import os
from datetime import datetime
from serpapi import GoogleSearch

# 1. 設定你的 SerpApi 金鑰
API_KEY = "5aa038b8b48605c32e03ecfd269f09b358528fa8f9869cbf5e546fa1471bb922"

# 2. 直接在此定義你的店家清單
# 建議使用字典格式：{"顯示名稱": "Place ID"}
STORES = {
    "板橋": "0x346803e0c12f0111:0x96cf6d00efa6a2e5",
    "民生": "0x3442a937f8b48629:0x489a0788378a066c",
    "新莊": "0x3442a79b5ba0b8df:0x433ad9a3c91cd37",
    "三峽": "0x34681d49492982e9:0xd99c4a0f911f5d0d",
    "蘆洲": "0x3442a92bc792af15:0xf10e6065b0462d19",
    "中和": "0x3442a9d756d4d789:0xd2ab824c3a1a8122",
    "梅花湖": "0x3467e77197a62b11:0xf852610c779dc99d",
}

def fetch_and_log():
    output_file = 'reviews_stats.csv'
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    all_data = []

    print(f"--- 開始抓取數據 ({now}) ---")

    for name, p_id in STORES.items():
        params = {
            "engine": "google_maps_reviews",
            "data_id": p_id,
            "api_key": API_KEY
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # 從結果中提取評分與評論數
            place_info = results.get("place_info", {})
            rating = place_info.get("rating", 0)
            reviews = place_info.get("reviews", 0)

            print(f"成功: [{name}] - {reviews} 則評論 ({rating}⭐)")

            all_data.append({
                "時間": now,
                "店家名稱": name,
                "評論總數": reviews,
                "平均評分": rating,
                "Place_ID": p_id
            })

        except Exception as e:
            print(f"錯誤: [{name}] 抓取失敗 - {e}")

    # 儲存結果
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
    
    print(f"\n--- 任務完成，數據已存入 {filename} ---")

if __name__ == "__main__":
    fetch_and_log()
