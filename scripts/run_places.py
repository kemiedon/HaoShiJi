import os
import json
from dotenv import load_dotenv
from haoshiji.places_client import (
    search_restaurants_by_text,
    get_place_reviews,
)

def main() -> None:
    # 1. 初始化環境與檢查鑰匙
    load_dotenv()
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    
    if not api_key:
        print("❌ 錯誤：找不到 API Key，請檢查 .env 檔案")
        return

    # 2. 設定搜尋參數
    query = "台北市 大安區 餐廳"
    min_rating = 4.0
    max_results = 5  # DEMO 建議先設定 5-10 筆，速度較快且免費額度夠用

    print(f"\n🚀 開始搜尋任務: [{query}]")
    print(f"🎯 目標：星等 > {min_rating}，預計抓取前 {max_results} 名")
    print("-" * 40)

    # 3. 執行搜尋與排序 (Step 1)
    # 現在這裡會收到已經由 Python 根據星等排好序的餐廳清單
    try:
        places = search_restaurants_by_text(
            api_key=api_key,
            query=query,
            min_rating=min_rating,
            max_results=max_results,
        )
    except Exception as e:
        print(f"❌ 搜尋過程發生錯誤: {e}")
        return

    if not places:
        print("查無符合條件的餐廳。")
        return

    print(f"✅ 成功找到 {len(places)} 家高品質餐廳（已完成高分排序）")

    # 4. 逐一抓取詳細評論 (Step 2)
    for idx, place in enumerate(places, start=1):
        name = place.get("name")
        place_id = place.get("place_id")
        rating = place.get("rating")

        print(f"   串接進度 [{idx}/{len(places)}]: 正在獲取『{name}』({rating}星) 的完整評論...")

        try:
            # 傳入 api_key 並獲取所有評論文字
            reviews = get_place_reviews(api_key, place_id)
            place["reviews"] = reviews
        except Exception as e:
            print(f"   ⚠️ 警告：無法取得 {name} 的評論: {e}")
            place["reviews"] = []

    # 5. 儲存結果 (Step 3)
    output_dir = "data/raw"
    output_path = os.path.join(output_dir, "places_with_reviews.json")
    
    # 自動建立資料夾
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(places, f, ensure_ascii=False, indent=2)

    print("-" * 40)
    print(f"🎉 任務完成！")
    print(f"📂 原始資料已儲存至: {output_path}")
    print(f"💡 提示：負責食安過濾的夥伴可以開始讀取這份檔案了。")
    
if __name__ == "__main__":
    main()