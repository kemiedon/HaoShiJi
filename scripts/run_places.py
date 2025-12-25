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
    max_results = 5  # MVP 版本：5 筆餐廳資料 

    print(f"\n🚀 開始搜尋任務: [{query}]")
    print("-" * 40)

    # 3. 執行搜尋與排序
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

    # 4. 逐一抓取詳細評論
    # 這裡我們準備一個新的列表，來存放符合計畫書格式的乾淨資料
    cleaned_restaurants = []

    for idx, place in enumerate(places, start=1):
        name = place.get("name")
        place_id = place.get("place_id")
        restaurant_rating = place.get("rating")

        print(f"   串接進度 [{idx}/{len(places)}]: 正在整理『{name}』...")

        try:
            raw_reviews = get_place_reviews(api_key, place_id)
        except Exception as e:
            print(f"   ⚠️ 警告：無法取得 {name} 的評論: {e}")
            raw_reviews = []

        # --- 資料整理：轉換為計畫書要求的格式  ---
        cleaned_reviews = []
        for r in raw_reviews:
            review_item = {
                "author": r.get("author_name"),  # 更名：author_name -> author
                "rating": r.get("rating"),
                "text": r.get("text"),
                "date": r.get("relative_time_description") # 更名：相對時間 -> date
            }
            cleaned_reviews.append(review_item)

        restaurant_item = {
            "name": name,
            "rating": restaurant_rating,
            "reviews": cleaned_reviews
        }
        cleaned_restaurants.append(restaurant_item)

    # 5. 儲存結果
    # 最終輸出的結構：最外層是字典，標籤為 "restaurants" 
    final_output = {
        "restaurants": cleaned_restaurants
    }

    output_dir = "data/raw" 
    output_path = os.path.join(output_dir, "places_with_reviews.json")
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        # 確保儲存格式與計畫書範例一致 
        json.dump(final_output, f, ensure_ascii=False, indent=2)

    print("-" * 40)
    print(f"🎉 任務完成！格式已與計畫書比對一致。")
    print(f"📂 儲存至: {output_path}")

if __name__ == "__main__":
    main()