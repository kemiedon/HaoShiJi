# 代碼改進文檔

## 概述
本文檔描述了對整個應用程式代碼結構的優化，使其更流暢、邏輯更清楚。

## 核心改進

### 1. **模組化架構**

#### 新增結構
```
src/app/
├── lib/
│   ├── constants.ts      # 常數定義
│   └── utils.ts          # 實用工具函數
├── hooks/
│   └── useRestaurantSearch.ts  # 自訂 Hook
├── components/
│   ├── Header.tsx
│   ├── FilterBar.tsx
│   ├── DataTable.tsx
│   └── MapSection.tsx
├── layout.tsx
└── page.tsx
```

### 2. **改進詳解**

#### **lib/constants.ts** - 集中管理常數
✅ 統一管理所有常數資料
✅ 易於維護和更新資料
✅ 減少硬編碼值

```typescript
export const CITIES = [
  { value: 'taipei', label: '台北' },
  { value: 'taichung', label: '台中' },
  // ...
];

export const MOCK_RESTAURANTS = [
  { id: 1, name: '美味漢堡店', level: 1, ... },
  // ...
];
```

#### **lib/utils.ts** - 可複用工具函數
✅ 提取邏輯，避免重複
✅ 職責單一，易於測試
✅ 提高代碼可讀性

```typescript
export const getLevelColorClass = (level: number): string => { ... };
export const getLevelDescription = (level: number): string => { ... };
export const filterRestaurants = (...): any[] => { ... };
```

#### **hooks/useRestaurantSearch.ts** - 自訂 Hook
✅ 封裝搜尋邏輯
✅ 管理相關狀態
✅ 可複用於多個元件

```typescript
export const useRestaurantSearch = (initialFilters) => {
  // 管理搜尋狀態
  // 提供搜尋、篩選、清除操作
  // 自動計算搜尋結果
  return { filters, results, hasSearched, ... };
};
```

### 3. **元件改進**

#### **DataTable.tsx** - 職責清晰的元件組織

**之前**:
- 單一大元件
- 混合業務邏輯和 UI
- 難以維護和測試

**之後**:
- 分解為 6 個子元件
- 每個元件一個職責
- 邏輯清晰易於追蹤

```tsx
export function DataTable()          // 主元件
├─ SearchBar()                       // 搜尋欄
├─ EmptyState()                      // 空狀態
└─ RestaurantList()                  // 列表
   └─ RestaurantRow()                // 單行
      └─ LevelBadge()                // 等級標籤
```

**優勢**:
- 易於測試各個子元件
- 代碼複用性高
- 維護成本低

#### **FilterBar.tsx** - 結構化的篩選器

**改進**:
- 分解為 3 個子元件 (CitySelector, AreaSelector, SearchInput)
- 使用 constants 中的資料
- 邏輯清晰，職責明確

#### **page.tsx** - 簡化的主頁面

**之前**:
- 混合狀態管理
- 直接使用狀態值
- 結構不清楚

**之後**:
```tsx
export default function Page()
├─ PageHeader()      // 標題區域
├─ PageContent()     // 主要內容
│  ├─ ContentSection
│  │  └─ DataTable
│  └─ ContentSection
│     └─ MapSection
└─ PageFooter()      // 底部
```

### 4. **數據流改進**

#### **狀態管理邏輯**

```
┌─────────────────────────────────────────┐
│         useRestaurantSearch Hook        │
├─────────────────────────────────────────┤
│ • filters (searchTerm, city, area)      │
│ • results (已篩選的結果)                  │
│ • hasSearched (搜尋狀態)                 │
│ • updateSearchTerm(term)                │
│ • updateCity(city)                      │
│ • updateArea(area)                      │
│ • handleSearch()                        │
│ • clearSearch()                         │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│          DataTable Component            │
├─────────────────────────────────────────┤
│ • 接收 Hook 返回的所有操作                │
│ • 管理本地搜尋輸入狀態                    │
│ • 遞迴傳遞數據給子元件                    │
└─────────────────────────────────────────┘
```

### 5. **性能優化**

#### **useMemo 優化搜尋結果**
```typescript
const results = useMemo(() => {
  if (!hasSearched) return [];
  return filterRestaurants(
    MOCK_RESTAURANTS,
    filters.searchTerm,
    filters.city,
    filters.area
  );
}, [filters, hasSearched]);
```

✅ 避免不必要的重新篩選
✅ 只在依賴變化時重新計算

#### **useCallback 優化事件處理**
```typescript
const updateSearchTerm = useCallback((term: string) => {
  setFilters((prev) => ({ ...prev, searchTerm: term }));
}, []);
```

✅ 避免不必要的函數重新建立
✅ 提升子元件性能

### 6. **代碼可讀性改進**

#### **類型安全**
```typescript
interface SearchFilters {
  searchTerm: string;
  city: string;
  area: string;
}

interface Restaurant {
  id: number;
  name: string;
  level: number;
  keywords: string;
  city: string;
  area: string;
}
```

#### **清晰的註釋**
```typescript
/**
 * 餐廳搜尋和篩選的自訂 Hook
 * @param initialFilters - 初始篩選條件
 * @returns 搜尋狀態和操作方法
 */
export function useRestaurantSearch(...) { }
```

#### **函數職責單一**
- 每個函數做一件事
- 函數名稱清楚表達意圖
- 易於理解和維護

## 邏輯流程

### 搜尋流程
```
用戶輸入文字
    ↓
點擊搜尋按鈕
    ↓
updateSearchTerm() 更新本地狀態
    ↓
handleSearch() 設置 hasSearched 為 true
    ↓
useMemo 自動觸發
    ↓
filterRestaurants() 篩選結果
    ↓
DisplaySearchResults
    ├─ 有結果 → RestaurantList
    └─ 無結果 → EmptyState
```

### 篩選流程
```
用戶選擇城市/地區
    ↓
updateCity() / updateArea()
    ↓
filters 更新
    ↓
useMemo 依賴變化
    ↓
自動重新篩選（如果已搜尋）
```

## 最佳實踐應用

### 1. 單一責任原則 (SRP)
- 每個元件只負責一個職責
- 每個函數只做一件事

### 2. 乾淨代碼 (DRY)
- 提取重複邏輯到工具函數
- 使用常數避免硬編碼

### 3. 關注點分離 (SoC)
- 業務邏輯在 Hook 中
- UI 邏輯在元件中
- 資料和常數在專用文件

### 4. 組件化設計
- 大元件分解為小元件
- 易於測試和複用

## 維護優勢

### 🔧 易於修改
- 需要更改篩選邏輯？編輯 `useRestaurantSearch`
- 需要新增城市？編輯 `constants.ts`
- 需要修改樣式？編輯單個元件

### 🧪 易於測試
- 工具函數易於單元測試
- Hook 可以單獨測試
- 子元件可以獨立測試

### 📈 易於擴展
- 新增功能不需要修改現有代碼
- 易於添加新的篩選條件
- 易於添加新的資訊展示

## 性能指標

✅ 減少不必要的重新渲染（useMemo、useCallback）
✅ 模組化減少包大小
✅ 清晰的邏輯流程提升初始化速度
✅ 緩存搜尋結果避免重複計算

## 總結

通過模組化、職責分離和優化的邏輯流程，代碼變得：
- **更流暢**：數據流清晰，狀態管理有序
- **邏輯更清楚**：結構明確，易於理解
- **更易維護**：修改成本低，測試容易
- **更可擴展**：新功能集成簡單
