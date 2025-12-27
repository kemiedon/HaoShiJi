# 快速開始指南

## 📁 項目結構

```
src/
├── app/
│   ├── lib/
│   │   ├── constants.ts          # 常數定義（城市、地區、模擬資料）
│   │   └── utils.ts              # 實用工具函數（顏色、篩選、格式化）
│   ├── hooks/
│   │   └── useRestaurantSearch.ts # 搜尋邏輯 Hook（狀態管理、篩選）
│   ├── components/
│   │   ├── Header.tsx            # 應用標題（好食機）
│   │   ├── FilterBar.tsx         # 篩選欄（城市、地區、搜尋）
│   │   ├── DataTable.tsx         # 搜尋結果表格
│   │   ├── MapSection.tsx        # 地圖展示
│   │   ├── ui/                   # UI 組件庫
│   │   └── figma/                # 自訂元件
│   ├── layout.tsx                # 根佈局
│   └── page.tsx                  # 主頁面
└── style/                        # 樣式文件
```

## 🚀 核心功能流程

### 1. 搜尋流程

```
用戶輸入搜尋文字
        ↓
點擊「搜尋」按鈕
        ↓
updateSearchTerm() 更新
        ↓
handleSearch() 觸發搜尋
        ↓
useRestaurantSearch Hook 計算結果
        ↓
展示搜尋結果或空狀態
```

### 2. 篩選流程

```
用戶選擇城市/地區
        ↓
updateCity() / updateArea() 更新
        ↓
Hook 自動重新計算結果（如果已搜尋）
        ↓
表格自動更新
```

## 💡 關鍵概念

### Hook: useRestaurantSearch

管理所有搜尋相關邏輯：

```typescript
const {
  filters,           // 當前篩選條件
  results,          // 搜尋結果
  hasSearched,      // 是否已搜尋
  updateSearchTerm, // 更新搜尋文字
  updateCity,       // 更新城市
  updateArea,       // 更新地區
  handleSearch,     // 觸發搜尋
  clearSearch,      // 清除搜尋
} = useRestaurantSearch();
```

### 工具函數

在 `lib/utils.ts` 中的可複用函數：

- `getLevelColorClass(level)` - 根據等級返回顏色
- `getLevelDescription(level)` - 根據等級返回描述文字
- `filterRestaurants(restaurants, searchTerm, city, area)` - 篩選餐廳

### 常數管理

在 `lib/constants.ts` 中定義：

- `CITIES` - 城市列表
- `AREAS` - 地區列表
- `MOCK_RESTAURANTS` - 模擬餐廳資料
- `LEVEL_DESCRIPTIONS` - 等級描述

## 🔧 如何修改

### 添加新的城市

編輯 `app/lib/constants.ts`：

```typescript
export const CITIES = [
  { value: 'taipei', label: '台北' },
  { value: 'taichung', label: '台中' },
  { value: 'new-city', label: '新城市' }, // 添加這行
];
```

### 添加新的等級顏色

編輯 `app/lib/utils.ts` 的 `getLevelColorClass` 函數：

```typescript
export const getLevelColorClass = (level: number): string => {
  if (level >= 4) {
    return 'bg-red-100 text-red-600';
  }
  // ... 其他邏輯
};
```

### 添加新的篩選條件

1. 在 `app/lib/constants.ts` 中添加新的常數
2. 在 `app/hooks/useRestaurantSearch.ts` 中添加新的狀態和更新函數
3. 在 `app/components/FilterBar.tsx` 中添加新的 UI 元件
4. 在 `app/lib/utils.ts` 的 `filterRestaurants` 中添加篩選邏輯

### 更改搜尋結果樣式

編輯 `app/components/DataTable.tsx` 中的元件：

- `SearchBar` - 搜尋欄樣式
- `RestaurantList` - 結果列表樣式
- `LevelBadge` - 等級標籤樣式

## 📊 數據流

```
┌──────────────────────────┐
│  FilterBar 接收 props    │
│  - filter1/2/searchText  │
│  - onFilter1Change etc   │
└────────────┬─────────────┘
             │ 調用
             ▼
┌──────────────────────────┐
│  page.tsx 狀態管理       │
│  - filter1, filter2      │
│  - searchText            │
└────────────┬─────────────┘
             │ 傳遞給
             ▼
┌──────────────────────────┐
│  DataTable 元件          │
│  - 使用 Hook             │
│  - 管理本地狀態           │
│  - 渲染子元件             │
└──────────────────────────┘
```

## 🎯 性能優化

### useMemo
搜尋結果使用 `useMemo`，避免不必要的重新計算：

```typescript
const results = useMemo(() => {
  if (!hasSearched) return [];
  return filterRestaurants(...);
}, [filters, hasSearched]);
```

### useCallback
事件處理函數使用 `useCallback`，避免重新建立：

```typescript
const updateSearchTerm = useCallback((term) => {
  setFilters(prev => ({ ...prev, searchTerm: term }));
}, []);
```

## 🧪 測試建議

### 搜尋功能
1. 輸入文字後點擊搜尋
2. 檢查結果是否正確
3. 清除搜尋是否重置

### 篩選功能
1. 選擇城市/地區
2. 檢查結果是否更新
3. 組合多個篩選條件

### 響應式設計
1. 測試手機版（< 640px）
2. 測試平板版（641px - 1024px）
3. 測試桌面版（> 1024px）

## 📝 代碼規範

### 命名規則
- 元件：PascalCase（例：DataTable）
- 函數：camelCase（例：getLevelColorClass）
- 常數：UPPER_SNAKE_CASE（例：MOCK_RESTAURANTS）

### 類型定義
- 總是為 Props 定義 interface
- 使用 TypeScript 類型確保類型安全
- JSDoc 註釋重要函數

### 元件結構
- 分解大元件為小子元件
- 每個元件一個職責
- 使用 Props 進行通信

## 🐛 常見問題

**Q: 如何更改搜尋資料？**
A: 編輯 `app/lib/constants.ts` 中的 `MOCK_RESTAURANTS`

**Q: 如何添加新的等級描述？**
A: 更新 `app/lib/constants.ts` 中的 `LEVEL_DESCRIPTIONS`

**Q: 如何修改篩選邏輯？**
A: 編輯 `app/lib/utils.ts` 中的 `filterRestaurants` 函數

**Q: 如何添加新的篩選條件？**
A: 參考「添加新的篩選條件」部分的步驟

## 📚 相關文檔

- [RWD_OPTIMIZATION_GUIDE.md](./RWD_OPTIMIZATION_GUIDE.md) - 響應式設計指南
- [CODE_IMPROVEMENTS.md](./CODE_IMPROVEMENTS.md) - 代碼改進詳解

## 🚀 下一步

1. ✅ 理解項目結構
2. ✅ 熟悉核心流程
3. 📝 根據需求修改常數
4. 🎨 調整 UI 樣式
5. 🧪 添加單元測試
6. 📦 構建並部署
