from dotenv import load_dotenv
load_dotenv()

import os
import json
from haoshiji.places_client import (
    search_restaurants_by_text,
    get_place_reviews,
)


def main() -> None:
    # =====================
    # Environment check
    # =====================
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_PLACES_API_KEY is not loaded.")

    # =====================
    # Query parameters
    # =====================
    query = "台北市 大安區 餐廳"
    min_rating = 4.0
    max_results = 20

    print(f"Searching restaurants by text: {query}")

    # =====================
    # Step 1: Text Search
    # =====================
    places = search_restaurants_by_text(
        query=query,
        min_rating=min_rating,
        max_results=max_results,
    )

    print(f"Found {len(places)} places.")

    # =====================
    # Step 2: Fetch reviews
    # =====================
    for idx, place in enumerate(places, start=1):
        name = place.get("name")
        place_id = place.get("place_id")

        print(f"[{idx}/{len(places)}] Fetching reviews: {name}")

        try:
            reviews = get_place_reviews(place_id)
        except Exception as e:
            print(f"  Failed to get reviews for {name}: {e}")
            reviews = []

        place["reviews"] = reviews

    # =====================
    # Step 3: Save output
    # =====================
    output_path = "data/raw/places_with_reviews.json"
    os.makedirs("data/raw", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(places, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(places)} places to {output_path}")


if __name__ == "__main__":
    main()
