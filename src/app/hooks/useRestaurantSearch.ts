/**
 * 餐廳搜尋和篩選的自訂 Hook
 */

import { useState, useCallback, useMemo } from 'react';
import { filterRestaurants } from '../lib/utils';
import { MOCK_RESTAURANTS } from '../lib/constants';

export interface SearchFilters {
  searchTerm: string;
  city: string;
  area: string;
}

export function useRestaurantSearch(initialFilters: SearchFilters = { searchTerm: '', city: '', area: '' }) {
  const [filters, setFilters] = useState(initialFilters);
  const [hasSearched, setHasSearched] = useState(false);

  // 使用 useMemo 避免不必要的重新篩選
  const results = useMemo(() => {
    if (!hasSearched) return [];
    return filterRestaurants(
      MOCK_RESTAURANTS,
      filters.searchTerm,
      filters.city,
      filters.area
    );
  }, [filters, hasSearched]);

  const updateSearchTerm = useCallback((term: string) => {
    setFilters((prev) => ({ ...prev, searchTerm: term }));
  }, []);

  const updateCity = useCallback((city: string) => {
    setFilters((prev) => ({ ...prev, city }));
  }, []);

  const updateArea = useCallback((area: string) => {
    setFilters((prev) => ({ ...prev, area }));
  }, []);

  const handleSearch = useCallback(() => {
    setHasSearched(true);
  }, []);

  const clearSearch = useCallback(() => {
    setFilters({ searchTerm: '', city: '', area: '' });
    setHasSearched(false);
  }, []);

  return {
    filters,
    results,
    hasSearched,
    updateSearchTerm,
    updateCity,
    updateArea,
    handleSearch,
    clearSearch,
  };
}
