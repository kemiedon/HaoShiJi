from typing import List, Dict, Any
import requests

# ====================
# API Endpoints
# ====================
PLACES_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

class PlacesClientError(Exception):
    """自定義錯誤類別，方便除錯"""
    pass

# ====================
# Text Search
# ====================
def search_restaurants_by_text(
    api_key: str,
    query: str,
    min_rating: float = 0.0,
    max_results: int = 20,
) -> List[Dict[str, Any]]:
    """
    搜尋餐廳並依星等排序
    """
    params = {
        "query": query,
        "type": "restaurant", # 強制指定搜尋餐廳
        "language": "zh-TW",
        "key": api_key,
    }

    response = requests.get(PLACES_TEXT_SEARCH_URL, params=params, timeout=10)
    
    if response.status_code != 200:
        raise PlacesClientError(f"API 連線失敗: {response.status_code}")

    data = response.json()
    raw_places = data.get("results", [])

    # --- Python 排序邏輯 ---
    # 1. 根據 rating 從高到低排序 (reverse=True)
    sorted_places = sorted(
        raw_places, 
        key=lambda x: x.get("rating", 0), 
        reverse=True
    )

    # 2. 篩選星等並限制回傳筆數
    results = []
    for p in sorted_places:
        rating = p.get("rating", 0)
        if rating >= min_rating:
            results.append({
                "place_id": p.get("place_id"),
                "name": p.get("name"),
                "rating": rating,
                "user_ratings_total": p.get("user_ratings_total"),
                "formatted_address": p.get("formatted_address"),
            })
        
        # 達到目標筆數就收工
        if len(results) >= max_results:
            break

    return results


# ====================
# Place Details (Reviews)
# ====================
def get_place_reviews(
    api_key: str,
    place_id: str,
    language: str = "zh-TW",
) -> List[Dict[str, Any]]:
    """
    取得餐廳的完整評論，供後續食安分析
    """
    params = {
        "place_id": place_id,
        "fields": "reviews", # 只要評論，節省流量
        "language": language,
        "key": api_key,
    }

    response = requests.get(PLACES_DETAILS_URL, params=params, timeout=10)
    
    if response.status_code != 200:
        return [] # 出錯時回傳空清單，不讓主程式斷掉

    data = response.json()
    result = data.get("result", {})
    # 這裡直接回傳完整 reviews 清單，包含完整 text
    return result.get("reviews", [])