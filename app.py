from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from api.places import search_restaurants_by_text, get_place_reviews
from api.classifier import (
    classify_review,
    SafetyLevel,
    classify_restaurant,
    load_certified_restaurants,
    load_inspection_failed,
)

load_dotenv()
app = Flask(__name__)
CORS(app)

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

if not GOOGLE_PLACES_API_KEY:
    raise Exception("GOOGLE_PLACES_API_KEY 環境變數未設定")

# ============================================
# 載入官方認證與稽查資料（應用啟動時執行一次）
# ============================================
print("📂 載入官方認證與稽查資料...")

# 取得當前腳本所在目錄的絕對路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERTIFICATION_CSV = os.path.join(BASE_DIR, "data/external/certified_restaurants.csv")
INSPECTION_JSON = os.path.join(BASE_DIR, "data/external/food_business_data.json")

# 載入台北市餐飲衛生評核資料（僅「優」等級）
if os.path.exists(CERTIFICATION_CSV):
    CERTIFIED_DATA = load_certified_restaurants(CERTIFICATION_CSV)
    print(f"✓ 載入 {len(CERTIFIED_DATA)} 筆官方認證餐廳")
else:
    CERTIFIED_DATA = {}
    print(f"⚠️  找不到官方認證資料: {CERTIFICATION_CSV}")

# 載入食品稽查不合格資料
if os.path.exists(INSPECTION_JSON):
    INSPECTION_FAILED_DATA = load_inspection_failed(INSPECTION_JSON)
    print(f"✓ 載入 {len(INSPECTION_FAILED_DATA)} 筆稽查不合格紀錄")
else:
    INSPECTION_FAILED_DATA = {}
    print(f"⚠️  找不到稽查資料: {INSPECTION_JSON}")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/<path:filename>")
def static_file(filename):
    return send_from_directory("static", filename)


# ============================================
# 路由 1: 前端配置 API（提供 Google Maps API Key）
# ============================================
@app.route("/api/config", methods=["GET"])
def get_config():
    """提供前端需要的配置資訊"""
    return jsonify({"googleMapsApiKey": GOOGLE_PLACES_API_KEY})


# ============================================
# 路由 2: 搜尋 API
# ============================================
@app.route("/api/search", methods=["POST"])
def search_restaurants():
    try:
        data = request.get_json()
        city = data.get("city", "")
        district = data.get("district", "")
        address = data.get("address", "")
        if not city or not address:
            return (
                jsonify({"status": "error", "message": "請提供城市和地址"}),
                400,
            )  # HTTP 400 = 客戶端錯誤
        # 步驟 3: 組合搜尋查詢
        query = f"{city} {district} {address} 餐廳".strip()
        print(f"\n🔍 收到搜尋請求: {query}")

        # TODO: 步驟 4-6 下一階段實作
        # - 呼叫 Google Places API
        # - 風險分析
        # - 儲存檔案

        # 步驟 4: 呼叫 Google Places API
        print("📡 正在搜尋餐廳...")
        places = search_restaurants_by_text(
            api_key=GOOGLE_PLACES_API_KEY,
            query=query,
            min_rating=0.0,  # 修正：改為 min_rating
            max_results=5,
        )
        print(f"✓ 找到 {len(places)} 間餐廳")

        # 步驟 5: 取得每間餐廳的評論並進行風險分析
        print("📝 正在取得評論並分析風險...")
        analyzed_places = []

        for place in places:
            place_id = place["place_id"]
            reviews = get_place_reviews(
                api_key=GOOGLE_PLACES_API_KEY, place_id=place_id, language="zh-TW"
            )
            place["reviews"] = reviews

            # 步驟 6: 使用完整風險分析模組（整合官方資料）
            # classify_restaurant() 會自動比對：
            #   1. 台北市餐飲衛生評核資料（優等級）
            #   2. 食品稽查不合格紀錄
            #   3. 評論中的症狀關鍵字
            #   4. 評論中的生食關鍵字
            analyzed_place = classify_restaurant(
                restaurant=place,
                certified_data=CERTIFIED_DATA,
                inspection_failed_data=INSPECTION_FAILED_DATA,
            )
            analyzed_places.append(analyzed_place)

            # 顯示分析結果
            level = analyzed_place["safety_analysis"]["level"]
            review_count = len(reviews)

            # 顯示額外資訊
            extras = []
            if analyzed_place["safety_analysis"].get("official_certification"):
                extras.append("✅官方認證")
            if analyzed_place["safety_analysis"].get("inspection_status"):
                extras.append("⛔稽查不合格")

            extra_info = f" ({', '.join(extras)})" if extras else ""
            print(f"  - {place['name']}: {review_count} 則評論 → {level}{extra_info}")

        # 步驟 7: 依風險等級排序
        # 排序邏輯：
        # 1. 稽查不合格優先排在最後（警示用）
        # 2. 其次按風險等級：低風險 > 注意
        # 3. 官方認證在同風險等級內優先顯示
        # 4. 同等級內依 Google 評分排序
        def sort_key(restaurant):
            analysis = restaurant["safety_analysis"]
            level = analysis["level"]
            has_certification = analysis.get("official_certification") is not None
            has_inspection_failed = analysis.get("inspection_status") is not None
            rating = restaurant.get("rating", 0)

            # 風險等級排序（數字越小越優先）
            level_order = {
                SafetyLevel.LOW_RISK.value: 0,
                SafetyLevel.CAUTION.value: 1,
            }

            # 排序優先級
            return (
                1 if has_inspection_failed else 0,  # 稽查不合格排最後
                level_order.get(level, 999),         # 風險等級
                0 if has_certification else 1,       # 官方認證優先
                -rating                              # Google 評分高的優先
            )

        analyzed_places.sort(key=sort_key)

        # 步驟 8: 回傳結果
        return jsonify(
            {
                "status": "success",
                "query": query,
                "count": len(analyzed_places),
                "restaurants": analyzed_places,
            }
        )
    except Exception as e:
        return (
            jsonify({"status": "error", "message": f"伺服器錯誤: {str(e)}"}),
            500,
        )  # HTTP 500 = 伺服器錯誤


if __name__ == "__main__":
    print("=" * 60)
    print("🍽️  好食機 (HaoShiJi) 後端伺服器")
    print("=" * 60)
    print(f"📍 前端頁面: http://localhost:5000")
    print(f"📍 API 端點: http://localhost:5000/api/search")
    print(f"📁 靜態檔案: static/")
    print("=" * 60)
    print("💡 按 Ctrl+C 停止伺服器\n")
    app.run(debug=True, port=5000, host="0.0.0.0")
