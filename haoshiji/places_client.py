"""
places_client.py

功能：
- 使用 Google Places Text Search API 搜尋餐廳
- 以「行政區 + 餐廳」為主搜尋策略
- 在程式端進行 rating 篩選
- 使用 Place Details API 取得評論（reviews）
"""

from typing import List, Dict, Any
import os
import requests
from dotenv import load_dotenv

# ====================
# Environment
# ====================
load_dotenv()

# ====================
# API Endpoints
# ====================
PLACES_TEXT_SEARCH_URL = (
    "https://maps.googleapis.com/maps/api/place/textsearch/json"
)

PLACES_DETAILS_URL = (
    "https://maps.googleapis.com/maps/api/place/details/json"
)

# ====================
# Exceptions
# ====================
class PlacesClientError(Exception):
    """Base exception for Places client errors."""


# ====================
# Utilities
# ====================
def _get_api_key() -> str:
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")

    if not api_key:
        raise PlacesClientError(
            "GOOGLE_PLACES_API_KEY not found in environment variables."
        )
    return api_key


# ====================
# Text Search
# ====================
def search_restaurants_by_text(
    query: str,
    min_rating: float = 0.0,
    max_results: int = 20,
) -> List[Dict[str, Any]]:
    """
    使用 Text Search 搜尋餐廳

    Args:
        query: 搜尋文字，例如「台北市 大安區 餐廳」
        min_rating: 最低星等
        max_results: 最多回傳筆數

    Returns:
        List[dict]: 餐廳資料清單
    """
    api_key = _get_api_key()

    params = {
        "query": query,
        "language": "zh-TW",
        "key": api_key,
    }

    response = requests.get(
        PLACES_TEXT_SEARCH_URL,
        params=params,
        timeout=10,
    )

    if response.status_code != 200:
        raise PlacesClientError(
            f"Places API error HTTP {response.status_code}: {response.text}"
        )

    data = response.json()
    places = data.get("results", [])

    print(f"Text Search returned {len(places)} places (raw)")

    results: List[Dict[str, Any]] = []

    for p in places:
        rating = p.get("rating", 0)
        if rating < min_rating:
            continue

        results.append(
            {
                "place_id": p.get("place_id"),
                "name": p.get("name"),
                "rating": rating,
                "user_ratings_total": p.get("user_ratings_total"),
                "formatted_address": p.get("formatted_address"),
            }
        )

        if len(results) >= max_results:
            break

    return results


# ====================
# Place Details (Reviews)
# ====================
def get_place_reviews(
    place_id: str,
    language: str = "zh-TW",
    max_reviews: int = 5,
) -> List[Dict[str, Any]]:
    """
    使用 Place Details API 取得餐廳評論

    Args:
        place_id: Google place_id
        language: 評論語言
        max_reviews: 最多回傳幾則評論（Google 上限通常 5）

    Returns:
        List[dict]: 評論清單
    """
    api_key = _get_api_key()

    params = {
        "place_id": place_id,
        "fields": "reviews",
        "language": language,
        "key": api_key,
    }

    response = requests.get(
        PLACES_DETAILS_URL,
        params=params,
        timeout=10,
    )

    if response.status_code != 200:
        raise PlacesClientError(
            f"Place Details API error HTTP {response.status_code}: {response.text}"
        )

    data = response.json()
    result = data.get("result", {})
    reviews = result.get("reviews", [])

    parsed_reviews: List[Dict[str, Any]] = []

    for r in reviews[:max_reviews]:
        parsed_reviews.append(
            {
                "author_name": r.get("author_name"),
                "rating": r.get("rating"),
                "text": r.get("text"),
                "time": r.get("time"),
            }
        )

    return parsed_reviews