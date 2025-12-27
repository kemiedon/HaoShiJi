'use client';

import { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';
import { useRestaurantSearch } from '../hooks/useRestaurantSearch';
import { getLevelColorClass, getLevelDescription } from '../lib/utils';

/**
 * 餐廳資料表格元件
 * 展示搜尋結果和餐廳詳細資訊
 */
export function DataTable() {
  const {
    filters,
    results,
    hasSearched,
    updateSearchTerm,
    handleSearch,
    clearSearch,
  } = useRestaurantSearch();

  const [searchInput, setSearchInput] = useState('');

  // 處理搜尋按鈕點擊
  const onSearchClick = () => {
    updateSearchTerm(searchInput);
    handleSearch();
  };

  // 處理清除搜尋
  const onClearSearch = () => {
    setSearchInput('');
    clearSearch();
  };

  // 根據搜尋狀態決定要顯示的內容
  const isEmpty = hasSearched && results.length === 0;

  return (
    <div className="w-full space-y-4 md:space-y-6">
      {/* 搜尋控制區域 */}
      <SearchBar
        value={searchInput}
        onChange={setSearchInput}
        onSearch={onSearchClick}
        onClear={onClearSearch}
        hasSearched={hasSearched}
      />

      {/* 搜尋結果或空狀態 */}
      {hasSearched && (
        <>
          {isEmpty ? (
            <EmptyState onReset={onClearSearch} />
          ) : (
            <RestaurantList restaurants={results} />
          )}
        </>
      )}
    </div>
  );
}

/**
 * 搜尋欄位子元件
 */
interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
  onClear: () => void;
  hasSearched: boolean;
}

function SearchBar({
  value,
  onChange,
  onSearch,
  onClear,
  hasSearched,
}: SearchBarProps) {
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  return (
    <div className="flex flex-col md:flex-row gap-3 md:gap-4 items-stretch md:items-center p-4 bg-muted/30 rounded-lg">
      <input
        type="text"
        placeholder="輸入城市或地點..."
        className="flex-1 px-4 py-2 border border-primary/30 bg-card rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary transition-all"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyPress={handleKeyPress}
      />
      <div className="flex gap-2">
        <button
          onClick={onSearch}
          className="flex-1 md:flex-none px-6 py-2 bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors font-medium"
        >
          搜尋
        </button>
        {hasSearched && (
          <button
            onClick={onClear}
            className="flex-1 md:flex-none px-6 py-2 bg-muted text-foreground rounded-lg shadow hover:bg-muted/80 transition-colors font-medium"
          >
            清除
          </button>
        )}
      </div>
    </div>
  );
}

/**
 * 空狀態提示
 */
interface EmptyStateProps {
  onReset: () => void;
}

function EmptyState({ onReset }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 bg-muted/20 rounded-xl border border-primary/10">
      <p className="text-lg text-muted-foreground mb-4">找不到符合條件的餐廳</p>
      <button
        onClick={onReset}
        className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
      >
        返回重新搜尋
      </button>
    </div>
  );
}

/**
 * 餐廳列表元件
 */
interface RestaurantListProps {
  restaurants: any[];
}

function RestaurantList({ restaurants }: RestaurantListProps) {
  return (
    <div className="bg-card rounded-xl shadow-md border border-primary/10 overflow-hidden">
      {/* 表頭 */}
      <div className="p-4 border-b bg-muted/50">
        <h3 className="font-semibold text-lg text-primary">
          搜尋結果 ({restaurants.length})
        </h3>
      </div>

      {/* 表格 */}
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/30">
              <TableHead className="text-xs md:text-sm">名稱</TableHead>
              <TableHead className="text-xs md:text-sm w-[100px]">食安等級</TableHead>
              <TableHead className="text-xs md:text-sm">關鍵字</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {restaurants.map((restaurant) => (
              <RestaurantRow key={restaurant.id} restaurant={restaurant} />
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

/**
 * 單個餐廳列表項目
 */
interface RestaurantRowProps {
  restaurant: any;
}

function RestaurantRow({ restaurant }: RestaurantRowProps) {
  const levelColor = getLevelColorClass(restaurant.level);
  const levelDesc = getLevelDescription(restaurant.level);

  return (
    <TableRow className="hover:bg-muted/50 transition-colors">
      <TableCell className="font-medium text-xs md:text-sm">
        {restaurant.name}
      </TableCell>
      <TableCell>
        <LevelBadge level={restaurant.level} description={levelDesc} colorClass={levelColor} />
      </TableCell>
      <TableCell className="text-xs md:text-sm text-muted-foreground">
        {restaurant.keywords}
      </TableCell>
    </TableRow>
  );
}

/**
 * 等級標籤子元件
 */
interface LevelBadgeProps {
  level: number;
  description: string;
  colorClass: string;
}

function LevelBadge({ level, description, colorClass }: LevelBadgeProps) {
  return (
    <div
      className={`inline-flex flex-col items-center justify-center w-10 h-10 rounded-full text-xs md:text-sm font-bold ${colorClass}`}
      title={description}
    >
      <span>{level}</span>
      <span className="text-xs">{description}</span>
    </div>
  );
}
