"""
api/classifier.py
食品安全風險分級模組（整合官方評核資料）

功能：
1. 分析 Google Places 評論中的食安風險關鍵字（5 大分類）
2. 比對台北市政府餐飲衛生管理分級評核資料（僅限「優」等級）
3. 比對食品稽查結果不合格資料
4. 輸出整合後的風險分級報告

風險等級：
    - 注意：評論中有任何風險關鍵字（症狀/品質缺陷/未煮熟/異物/環境/生食）
    - 無/低風險：無風險關鍵字

獨立標籤：
    - 官方認證優：台北市餐飲衛生評核「優」等級
    - 稽核未通過：食品稽查不合格紀錄

使用方式（CLI）：
    python -m api.classifier

輸入檔案：
    - data/raw/places_with_reviews.json（爬蟲資料）
    - data/external/certified_restaurants.csv（官方評核資料）
    - scraper/food_business_data.json（稽查資料）

輸出檔案：
    - data/processed/safety_classified.json
"""

import json
import csv
import os
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


# ====================
# 常數定義
# ====================
class SafetyLevel(Enum):
    """食安風險等級"""

    CAUTION = "注意"  # 有任何關鍵字提及（症狀/生食）
    LOW_RISK = "無/低風險"
    CERTIFIED = "官方認證優"
    INSPECTION = "稽核未通過"


# 1. 負面症狀、感官異狀與物理危害（吃了出問題 / User 負面體感回饋）
SYMPTOM_KEYWORDS = [
    # 急性病徵
    "發燒", "虛弱", "頭暈", "冒冷汗", "肌肉酸痛", "發冷",
    "嘔吐", "噁心", "胃痙攣", "上吐下瀉",
    "拉肚子", "腹瀉", "肚子痛", "狂拉", "狂瀉", "跑廁所", "腹絞痛",
    "紅疹", "過敏",
    "看醫生", "掛急診", "腸胃炎", "食物中毒",
]

FOOD_QUALITY_DEFECT = [
    # 感官異狀 (嗅覺/味覺)
    "不新鮮", "臭掉", "壞掉", "發霉", "有異味", "臭酸味", "酸臭",
    "藥水味", "漂白水味", "土味", "油耗味", "腐敗", "腥臭", "腥臭味",
    "有塑膠味", "有化學味", "變質", "有怪味",
]

UNDERCOOKED = [
    "沒熟", "沒煮熟", "血水", "生味", "太生",
]

FOREIGN_BODY = [
    "頭髮", "蟑螂", "蟲",
    "碎玻璃", "鋼刷絲", "異物", "塑膠片",
]

ENVIRONMENT = [
    # 環境問題
    "衛生問題", "環境髒亂", "廁所臭", "廁所髒", "霉味",
]

# 2. 高風險料理關鍵字（成品、菜名類）
DISH_KEYWORDS = [
    "生魚片",
    "刺身",
    "握壽司",
    "韃靼牛肉",
    "生牛肉",
    "生雞蛋",
    "蛋液",
    "半熟蛋",
    "太陽蛋",
    "法式吐司",
    "生菜沙拉",
    "生醃",
    "醬蟹",
    "提拉米蘇",
    "美乃滋",
    "越式春捲",
    "生蠔",
]

# 台北市行政區對照
DISTRICT_MAP = {
    "63000010": "松山區",
    "63000020": "信義區",
    "63000030": "大安區",
    "63000040": "中山區",
    "63000050": "中正區",
    "63000060": "大同區",
    "63000070": "萬華區",
    "63000080": "文山區",
    "63000090": "南港區",
    "63000100": "內湖區",
    "63000110": "士林區",
    "63000120": "北投區",
}


# ====================
# 官方評核資料載入
# ====================
def load_certified_restaurants(csv_path: str) -> Dict[str, Dict[str, str]]:
    """
    載入官方餐飲衛生評核資料（僅限評核結果為「優」）

    Args:
        csv_path: CSV 檔案路徑

    Returns:
        以「業者名稱」為 key 的字典
    """
    certified = {}
    total_count = 0
    excellent_count = 0
    good_count = 0

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_count += 1
            name = row.get("業者名稱店名", "").strip()
            rating = row.get("評核結果", "").strip()

            if rating == "良":
                good_count += 1
                continue  # 跳過「良」等級

            if name and rating == "優":
                excellent_count += 1
                district_code = row.get("行政區域代碼", "")
                certified[name] = {
                    "district_code": district_code,
                    "district_name": DISTRICT_MAP.get(district_code, "未知"),
                    "registration_id": row.get("食品業者登錄字號", ""),
                    "address": row.get("地址", ""),
                    "certification_rating": rating,
                }

    print(f"  原始資料: {total_count} 筆")
    print(f"  評核「優」: {excellent_count} 筆（已納入）")
    print(f"  評核「良」: {good_count} 筆（已排除）")

    return certified


def load_inspection_failed(json_path: str) -> Dict[str, Dict[str, str]]:
    """
    載入食品稽查不合格資料

    Args:
        json_path: JSON 檔案路徑

    Returns:
        以「業者名稱」為 key 的字典
    """
    failed = {}

    if not os.path.exists(json_path):
        return failed

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        company_name = item.get("company_name", "").strip()
        if company_name:
            failed[company_name] = {
                "address": item.get("address", ""),
                "registration_number": item.get("registration_number", ""),
            }

    print(f"  稽查不合格: {len(failed)} 筆（已納入）")
    return failed


def fuzzy_match_certification(
    restaurant_name: str,
    restaurant_address: str,
    certified_data: Dict[str, Dict[str, str]],
) -> Optional[Dict[str, str]]:
    """
    模糊比對餐廳是否在官方認證名單中

    比對策略：
    1. 完全名稱比對
    2. 清理後名稱比對
    3. 部分名稱 + 地址交叉驗證

    Args:
        restaurant_name: 餐廳名稱（來自 Google Places）
        restaurant_address: 餐廳地址（來自 Google Places）
        certified_data: 官方認證資料字典

    Returns:
        匹配到的認證資訊，或 None
    """
    if not restaurant_name:
        return None

    # 策略 1：完全比對
    if restaurant_name in certified_data:
        return certified_data[restaurant_name]

    # 清理名稱（移除常見後綴與空白）
    def clean_name(name: str) -> str:
        suffixes = ["餐廳", "店", "門市", "分店", "旗艦店", "本店", "總店"]
        result = name.strip()
        for suffix in suffixes:
            result = result.replace(suffix, "")
        return result.strip()

    clean_restaurant = clean_name(restaurant_name)

    # 策略 2：清理後完全比對
    for cert_name, cert_info in certified_data.items():
        if clean_restaurant == clean_name(cert_name):
            return cert_info

    # 策略 3：部分名稱比對 + 地址驗證
    for cert_name, cert_info in certified_data.items():
        clean_cert = clean_name(cert_name)

        # 檢查名稱是否有包含關係
        name_match = (
            clean_restaurant in clean_cert
            or clean_cert in clean_restaurant
            or clean_restaurant.replace("-", "") in clean_cert.replace("-", "")
        )

        if name_match:
            # 有地址時進行交叉驗證
            if restaurant_address and cert_info["address"]:
                for district in DISTRICT_MAP.values():
                    if (
                        district in restaurant_address
                        and district in cert_info["address"]
                    ):
                        return cert_info
            else:
                # 無地址時，若名稱相似度高則直接匹配
                if len(clean_restaurant) >= 3 and len(clean_cert) >= 3:
                    return cert_info

    return None


# ====================
# 評論分析
# ====================
def classify_review(review_text: str) -> Dict[str, Any]:
    """
    分析單則評論的食安風險

    Args:
        review_text: 評論內文

    Returns:
        {
            "has_symptoms": bool,
            "has_raw_food": bool,
            "matched_keywords": List[str],
        }
    """
    if not review_text:
        return {
            "has_symptoms": False,
            "has_raw_food": False,
            "matched_keywords": [],
        }

    text = review_text.lower()
    matched = []
    has_symptoms = False

    # 檢查急性病徵
    for keyword in SYMPTOM_KEYWORDS:
        if keyword in text:
            has_symptoms = True
            matched.append(f"症狀:{keyword}")

    # 檢查食品品質缺陷
    for keyword in FOOD_QUALITY_DEFECT:
        if keyword in text:
            has_symptoms = True
            matched.append(f"品質缺陷:{keyword}")

    # 檢查未煮熟
    for keyword in UNDERCOOKED:
        if keyword in text:
            has_symptoms = True
            matched.append(f"未煮熟:{keyword}")

    # 檢查異物
    for keyword in FOREIGN_BODY:
        if keyword in text:
            has_symptoms = True
            matched.append(f"異物:{keyword}")

    # 檢查環境問題
    for keyword in ENVIRONMENT:
        if keyword in text:
            has_symptoms = True
            matched.append(f"環境:{keyword}")

    # 檢查生食關鍵字
    has_raw_food = False
    for keyword in DISH_KEYWORDS:
        if keyword in text:
            has_raw_food = True
            matched.append(f"生食:{keyword}")

    return {
        "has_symptoms": has_symptoms,
        "has_raw_food": has_raw_food,
        "matched_keywords": matched,
    }


def classify_restaurant(
    restaurant: Dict[str, Any],
    certified_data: Dict[str, Dict[str, str]],
    inspection_failed_data: Dict[str, Dict[str, str]],
) -> Dict[str, Any]:
    """
    分析單家餐廳的整體食安風險（整合官方認證與稽查資料）

    Args:
        restaurant: 餐廳資料（含評論）
        certified_data: 官方認證資料字典
        inspection_failed_data: 稽查不合格資料字典

    Returns:
        原餐廳資料 + safety_analysis 欄位
    """
    reviews = restaurant.get("reviews", [])
    name = restaurant.get("name", "")
    address = restaurant.get("formatted_address", "")

    # 檢查稽查不合格名單
    inspection_failed = fuzzy_match_certification(name, address, inspection_failed_data)

    # 檢查官方認證
    certification = fuzzy_match_certification(name, address, certified_data)

    # 分析所有評論
    all_matched_keywords = []
    symptom_count = 0
    raw_food_count = 0
    flagged_reviews = []

    for review in reviews:
        text = review.get("text", "")
        result = classify_review(text)

        if result["has_symptoms"]:
            symptom_count += 1
            flagged_reviews.append(
                {
                    "type": "症狀",
                    "author": review.get("author_name", "匿名"),
                    "text_preview": text[:100] + "..." if len(text) > 100 else text,
                    "keywords": [
                        k for k in result["matched_keywords"] if k.startswith("症狀:")
                    ],
                }
            )

        if result["has_raw_food"]:
            raw_food_count += 1

        all_matched_keywords.extend(result["matched_keywords"])

    # 判定風險等級（僅基於評論內容）
    # 優先級：有關鍵字（注意） > 無關鍵字（低風險）
    # 官方認證和稽查不合格作為獨立標籤，不影響風險等級
    if symptom_count > 0 or raw_food_count > 0:
        # 有任何關鍵字提及（症狀、生食等）→ 標示為注意
        level = SafetyLevel.CAUTION
    else:
        level = SafetyLevel.LOW_RISK

    # 組裝分析結果
    safety_analysis = {
        "level": level.value,
        "symptom_mentions": symptom_count,
        "raw_food_mentions": raw_food_count,
        "matched_keywords": list(set(all_matched_keywords)),
        "total_reviews_analyzed": len(reviews),
        "flagged_reviews": flagged_reviews if flagged_reviews else None,
        "official_certification": None,
        "inspection_status": None,
    }

    if inspection_failed:
        safety_analysis["inspection_status"] = {
            "status": "稽查不合格",
            "registration_number": inspection_failed["registration_number"],
            "failed_address": inspection_failed["address"],
        }

    if certification:
        safety_analysis["official_certification"] = {
            "status": "通過評核",
            "rating": certification["certification_rating"],
            "registration_id": certification["registration_id"],
            "certified_address": certification["address"],
            "district": certification["district_name"],
        }

    return {
        **restaurant,
        "safety_analysis": safety_analysis,
    }


# ====================
# 主流程
# ====================
def process_all_restaurants(
    input_path: str,
    output_path: str,
    certification_csv_path: str,
    inspection_json_path: str,
) -> List[Dict[str, Any]]:
    """
    主流程：讀取原始資料 → 載入官方認證與稽查資料 → 分類 → 輸出

    Args:
        input_path: 爬蟲資料 JSON 路徑
        output_path: 輸出 JSON 路徑
        certification_csv_path: 官方評核 CSV 路徑
        inspection_json_path: 稽查不合格 JSON 路徑

    Returns:
        分類後的餐廳清單
    """
    print("=" * 50)
    print("食品安全風險分級系統")
    print("=" * 50)

    # Step 1: 載入官方認證資料
    print("\nStep 1: 載入官方餐飲衛生評核資料...")
    if not os.path.exists(certification_csv_path):
        print(f"  警告：找不到官方評核資料 ({certification_csv_path})")
        print("   將僅依據評論內容進行分類")
        certified_data = {}
    else:
        certified_data = load_certified_restaurants(certification_csv_path)

    # Step 1.5: 載入稽查不合格資料
    print("\nStep 1.5: 載入稽查不合格資料...")
    inspection_failed_data = load_inspection_failed(inspection_json_path)

    # Step 2: 載入爬蟲資料
    print(f"\nStep 2: 載入爬蟲資料...")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"找不到爬蟲資料: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        # 處理兩種資料格式：直接是陣列 或 包在 restaurants key 裡
        if isinstance(data, dict) and "restaurants" in data:
            restaurants = data["restaurants"]
        elif isinstance(data, list):
            restaurants = data
        else:
            raise ValueError("資料格式錯誤：需要陣列或包含 'restaurants' key 的字典")
    print(f"   共 {len(restaurants)} 家餐廳待分類")

    # Step 3: 執行分類
    print(f"\n Step 3: 執行食安風險分類...")
    classified = []
    for i, restaurant in enumerate(restaurants, 1):
        result = classify_restaurant(restaurant, certified_data, inspection_failed_data)
        classified.append(result)

        # 進度顯示
        if i % 10 == 0 or i == len(restaurants):
            print(f"   進度: {i}/{len(restaurants)}")

    # Step 4: 排序
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

    classified.sort(key=sort_key)

    # Step 5: 儲存結果
    print(f"\n Step 4: 儲存分類結果...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(classified, f, ensure_ascii=False, indent=2)

    # Step 6: 輸出摘要
    print("\n" + "=" * 50)
    print("分類結果摘要")
    print("=" * 50)

    # 統計風險等級
    print("\n【風險等級分布】")
    level_emoji = {
        "無/低風險": "🟢",
        "注意": "🟡",
    }

    # 只統計兩個風險等級
    for level_value in [SafetyLevel.LOW_RISK.value, SafetyLevel.CAUTION.value]:
        count = sum(1 for r in classified if r["safety_analysis"]["level"] == level_value)
        emoji = level_emoji.get(level_value, "")
        print(f"   {emoji} {level_value}: {count} 家")

    # 統計官方認證和稽查不合格（獨立標籤）
    print("\n【獨立標籤統計】")
    certified_count = sum(1 for r in classified if r["safety_analysis"].get("official_certification") is not None)
    inspection_failed_count = sum(1 for r in classified if r["safety_analysis"].get("inspection_status") is not None)
    print(f"   ✅ 官方認證優: {certified_count} 家")
    print(f"   ⛔ 稽核未通過: {inspection_failed_count} 家")

    # 稽查不合格餐廳詳情
    inspection_failed = [r for r in classified if r["safety_analysis"].get("inspection_status") is not None]
    if inspection_failed:
        print("\n⛔ 稽查不合格餐廳警示：")
        for r in inspection_failed:
            name = r.get("name", "未知")
            level = r["safety_analysis"]["level"]
            inspection_info = r["safety_analysis"].get("inspection_status", {})
            print(f"   - {name} ({level})")
            if inspection_info:
                print(f"     登錄字號: {inspection_info.get('registration_number', 'N/A')}")

    # 注意等級餐廳詳情
    caution_list = [r for r in classified if r["safety_analysis"]["level"] == "注意"]
    if caution_list:
        print("\n🟡 注意等級餐廳警示：")
        for r in caution_list:
            name = r.get("name", "未知")
            keywords = r["safety_analysis"]["matched_keywords"]

            # 分類顯示各種關鍵字
            all_risk_keywords = []
            for k in keywords:
                if k.startswith("症狀:"):
                    all_risk_keywords.append(k.replace("症狀:", ""))
                elif k.startswith("品質缺陷:"):
                    all_risk_keywords.append(k.replace("品質缺陷:", ""))
                elif k.startswith("未煮熟:"):
                    all_risk_keywords.append(k.replace("未煮熟:", ""))
                elif k.startswith("異物:"):
                    all_risk_keywords.append(k.replace("異物:", ""))
                elif k.startswith("環境:"):
                    all_risk_keywords.append(k.replace("環境:", ""))

            print(f"   - {name}")
            if all_risk_keywords:
                print(f"     關鍵字: {', '.join(all_risk_keywords)}")

    print("\n" + "=" * 50)
    print(f" 完整結果已儲存至: {output_path}")
    print(f"分類時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    return classified


# ====================
# 進入點
# ====================
if __name__ == "__main__":
    # 預設路徑配置
    INPUT_PATH = "data/raw/places_with_reviews.json"
    OUTPUT_PATH = "data/processed/safety_classified.json"
    CERTIFICATION_CSV = "data/external/certified_restaurants.csv"
    INSPECTION_JSON = "scraper/food_business_data.json"

    try:
        process_all_restaurants(
            input_path=INPUT_PATH,
            output_path=OUTPUT_PATH,
            certification_csv_path=CERTIFICATION_CSV,
            inspection_json_path=INSPECTION_JSON,
        )
    except FileNotFoundError as e:
        print(f" 錯誤: {e}")
        print("\n請確認以下檔案存在：")
        print(f"   1. {INPUT_PATH}")
        print(f"   2. {CERTIFICATION_CSV}")
        print(f"   3. {INSPECTION_JSON}")
    except Exception as e:
        print(f" 未預期的錯誤: {e}")
        raise
