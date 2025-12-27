/**
 * 實用工具函數集
 */

/**
 * 根據等級返回對應的顏色樣式類
 */
export const getLevelColorClass = (level: number): string => {
  if (level >= 4) {
    return 'bg-red-100 text-red-600';
  }
  if (level === 3) {
    return 'bg-yellow-100 text-yellow-600';
  }
  return 'bg-green-100 text-green-600';
};

/**
 * 根據等級返回風險描述
 */
export const getLevelDescription = (level: number): string => {
  const descriptions: Record<number, string> = {
    1: '安全',
    2: '較安全',
    3: '需注意',
    4: '有風險',
    5: '高風險',
  };
  return descriptions[level] || '未知';
};

/**
 * 搜尋過濾函數
 */
export const filterRestaurants = (
  restaurants: any[],
  searchTerm: string,
  cityFilter: string,
  areaFilter: string
): any[] => {
  return restaurants.filter((restaurant) => {
    const matchesSearch =
      !searchTerm ||
      restaurant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      restaurant.keywords.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesCity = !cityFilter || restaurant.city === cityFilter;
    const matchesArea = !areaFilter || restaurant.area === areaFilter;

    return matchesSearch && matchesCity && matchesArea;
  });
};

/**
 * 格式化關鍵字
 */
export const formatKeywords = (keywords: string): string[] => {
  return keywords.split(',').map((k) => k.trim());
};
