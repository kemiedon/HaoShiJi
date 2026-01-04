# 好食機 HaoShiJi 🍜🔍

---

## 📌 專案簡介

**好食機 HaoShiJi** 是一個結合 **Google Places API** 與 **評論關鍵字分析** 的餐廳篩選系統，
目標在於協助使用者於聚餐或外食前，**避開潛在食安風險餐廳**，找到「安心又合適的好食時機」。

本專案聚焦於：

* 即時取得 Google 商家與評論資料
* 從評論文字中辨識常見「負面用餐體驗」與「食安風險線索」
* 提供可延伸的風險判斷基礎，作為後續分析與視覺化的資料來源

---

## 🧠 專案主題

* **諧音概念**：「好時機」
* **核心意涵**：找到好的用餐時機與地點
* **延伸含義**：呼應台灣日常用語「好食」，強調安心、適合聚餐的餐廳選擇

---

## 🎯 專案目標

透過 **縣市 / 行政區、星等（4 星以上）與評論內容分析**，
篩選出 **相對無明顯食安風險** 的聚餐餐廳，
協助使用者在有限時間內做出更安心的用餐決策。

---

## 🚀 功能特色

### 🔍 核心功能

* **餐廳搜尋與篩選**
  依據縣市 / 行政區、關鍵字（如「聚餐 餐廳」）與最低星等（如 4 星以上）搜尋餐廳。

* **Google Places API 串接**
  透過 Text Search / Place Details API 取得：

  * 商家基本資訊（名稱、地址、評分、評論數）
  * 最近評論內容（最多 5 則）

* **評論關鍵字風險分析（Rule‑based Baseline）**
  以關鍵字方式辨識評論中可能出現的風險線索，例如：

  * 吃完不舒服、拉肚子、腹瀉
  * 食材不新鮮、有異味
  * 衛生不佳、環境髒亂

* **結構化資料輸出**
  將處理後的餐廳與評論資料輸出為 JSON，供後續模組分析與前端顯示使用。

---

## 🧩 功能模組與分工

| 模組                | 負責人    | 說明                    |
| ----------------- | ------ | --------------------- |
| Google Places API | Wan    | 餐廳與評論資料抓取、API 錯誤處理    |
| 食安風險分析            | Vickie | 評論關鍵字設計與風險標記          |
| 使用者介面             | Bella  | Streamlit 查詢與結果呈現     |
| 整合與測試             | Kemie  | Code Review、整體流程整合與驗證 |

---

## 🧩 模組概要說明

### 基礎資料取得與 API 介接（Wan）

**功能說明**

* 呼叫 **Google Places API**（Text Search / Place Details）
* 擷取餐廳基本資訊與評論內容
* 將資料整理並儲存為 `JSON` 檔案，供後續分析模組使用

**實作重點**

* API Key 透過環境變數讀取：

  ```python
  os.environ["GOOGLE_PLACES_API_KEY"]
  ```

---

### 例外處理（Error Handling）

系統需妥善處理以下常見情境，以確保資料流程穩定性：

* 查無搜尋結果（No Results）
* 超出 API 配額限制（Quota Exceeded）
* API Key 錯誤或未設定
* 網路或連線失敗（Connection Error）

---

## 📊 輸出資料說明

每筆餐廳資料包含：

* `place_id`
* `name`
* `rating`
* `user_ratings_total`
* `formatted_address`
* `reviews`（最多 5 則）

  * `rating`
  * `text`
  * `author_name`
  * `time`

上述資料可作為後續：

* 食安風險評分
* 中文情緒分析
* 視覺化與統計分析
  的基礎資料來源。

---

## 🛠️ 安裝與使用

### 環境需求

* Python 3.10+
* 已啟用 Google Places API 的 API Key

### 套件安裝

```bash
pip install -r requirements.txt
```

### 環境變數設定

```bash
export GOOGLE_PLACES_API_KEY="YOUR_API_KEY"
```

### 基本使用

```bash
python scripts/run_places.py
```

執行後將於 `data/` 目錄產生餐廳與評論的 JSON 檔案。

---

## 📁 專案結構

```text
HaoShiJi/
├── scripts/
│   └── run_places.py          # 專案執行入口
├── haoshiji/
│   ├── __init__.py
│   └── places_client.py       # Google Places API 封裝
├── data/                       # 輸出資料（JSON / CSV）
├── requirements.txt
├── README.md
└── .env.example
```

---

## 🔧 技術特點

* **Google Places API 整合**：即時取得最新商家與評論資料
* **繁體中文評論處理**：針對台灣常見用語設計關鍵字
* **模組化設計**：API 呼叫、資料處理、分析邏輯清楚分離
* **錯誤處理機制**：包含 API Key、Quota、連線失敗、無結果等情境

---

## 🎯 使用場景

### 🍽️ 一般使用者

* 聚餐前快速篩選相對安心的餐廳
* 避免有多起負面用餐體驗的店家

### 🧑‍💻 專案與學習

* API 串接與資料清洗實作練習
* 中文評論分析入門專案
* Streamlit / NLP 專案的前置資料層

---

## 🔮 未來擴充方向

* 中文情緒分析（NLP / ML）
* 多維度評論分類（餐點 / 服務 / 環境）
* 食安風險量化評分模型
* 視覺化報告與趨勢分析
* Web / Streamlit 即時查詢介面

---

## 📌 專案定位說明

本專案目前以 **關鍵字規則法（Rule‑based）** 作為基礎風險判斷方式，
重點在於建立一個 **穩定、可解釋、可擴充的資料管線**，
而非一次完成完整情緒分析模型。

此設計有助於：

* 降低分析黑箱性
* 提高初期專案可完成度
* 為後續進階分析奠定良好基礎
