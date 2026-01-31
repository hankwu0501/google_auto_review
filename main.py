from serpapi import GoogleSearch
import json

API_KEY = "5aa038b8b48605c32e03ecfd269f09b358528fa8f9869cbf5e546fa1471bb922"

# 這裡填入你想測試的店家或 ID
params = {
    "engine": "google_maps",
    "q": "ChIJEQEvweADaDQR5aKm7wBtz5Y", # 以台北101為例
    "api_key": API_KEY
}

search = GoogleSearch(params)
results = search.get_dict()

# --- 輸出重點資訊到螢幕 ---
print("--- API 回傳結構檢查 ---")
if "place_results" in results:
    print("找到 place_results 欄位！")
    print(f"店名: {results['place_results'].get('title')}")
    print(f"評論數: {results['place_results'].get('reviews')}")
elif "local_results" in results:
    print("找到 local_results 列表（這通常發生在搜尋結果不只一個時）")
    first_result = results["local_results"][0]
    print(f"第一筆店名: {first_result.get('title')}")
    print(f"第一筆評論數: {first_result.get('reviews')}")
else:
    print("找不到 place_results 或 local_results，請檢查 API 回傳內容")

# --- 將完整 JSON 存檔，方便你打開來看 ---
with open('debug_output.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n--- 完整回傳內容已存至 debug_output.json ---")
