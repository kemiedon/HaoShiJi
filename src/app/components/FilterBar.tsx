'use client';

import { useEffect, useRef, useState } from 'react';
import { Input } from './ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { TAIWAN_LOCATIONS_DATABASE } from '../lib/constants';

/**
 * 篩選條件物件型別
 */
interface FilterBarProps {
  searchText: string;
  onSearchChange: (value: string) => void;
}

/**
 * 篩選欄元件
 * 提供縣市、鄉鎮市區、郵遞區號和搜尋功能
 */
export function FilterBar({
  searchText,
  onSearchChange,
}: FilterBarProps) {
  const [county, setCounty] = useState('');
  const [district, setDistrict] = useState('');
  const [zipcode, setZipcode] = useState('');
  
  const countyBoxRef = useRef<HTMLSelectElement>(null);
  const districtBoxRef = useRef<HTMLSelectElement>(null);
  const zipcodeBoxRef = useRef<HTMLInputElement>(null);

  // 獲取縣市列表
  const counties = Object.getOwnPropertyNames(TAIWAN_LOCATIONS_DATABASE);
  
  // 獲取當前縣市的鄉鎮市區
  const districts = county 
    ? Object.getOwnPropertyNames(TAIWAN_LOCATIONS_DATABASE[county as keyof typeof TAIWAN_LOCATIONS_DATABASE] || {})
    : [];

  // 當縣市變化時
  const handleCountyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedCounty = e.target.value;
    setCounty(selectedCounty);
    setDistrict('');
    setZipcode('');
  };

  // 當鄉鎮市區變化時
  const handleDistrictChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedDistrict = e.target.value;
    setDistrict(selectedDistrict);
    
    // 自動填充郵遞區號
    if (selectedDistrict && county) {
      const zipcodeValue = TAIWAN_LOCATIONS_DATABASE[county as keyof typeof TAIWAN_LOCATIONS_DATABASE]?.[selectedDistrict as never];
      setZipcode(zipcodeValue || '');
    } else {
      setZipcode('');
    }
  };

  return (
    <nav className="sticky top-0 z-40 bg-background border-b border-primary/10 shadow-sm">
      <div className="px-3 md:px-4 py-3 md:py-4">
        {/* 搜尋輸入框 */}
        <div className="flex flex-col gap-2 md:gap-4 md:flex-row md:items-center mb-3 md:mb-0">
          <SearchInput value={searchText} onChange={onSearchChange} />
        </div>

        {/* 縣市、鄉鎮市區、郵遞區號選擇器 */}
        <div className="flex flex-col gap-2 md:gap-4 md:flex-row md:items-center pt-3 md:pt-0 border-t md:border-t-0 border-primary/10">
          <div className="dropdown flex flex-col gap-2 md:gap-4 md:flex-row w-full md:w-auto">
            {/* 縣市選擇器 */}
            <select
              ref={countyBoxRef}
              id="county_box"
              name="county"
              value={county}
              onChange={handleCountyChange}
              className="w-full md:w-48 px-4 py-2 border border-primary/30 bg-card shadow-sm rounded-xl hover:border-primary/50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">選擇縣市</option>
              {counties.map((countyName) => (
                <option key={countyName} value={countyName}>
                  {countyName}
                </option>
              ))}
            </select>

            {/* 鄉鎮市區選擇器 */}
            <select
              ref={districtBoxRef}
              id="district_box"
              name="district"
              value={district}
              onChange={handleDistrictChange}
              disabled={!county}
              className={`w-full md:w-48 px-4 py-2 border border-primary/30 bg-card shadow-sm rounded-xl hover:border-primary/50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary ${
                !county ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <option value="">選擇鄉鎮市區</option>
              {districts.map((districtName) => (
                <option key={districtName} value={districtName}>
                  {districtName}
                </option>
              ))}
            </select>

            {/* 郵遞區號輸入框 */}
            <input
              ref={zipcodeBoxRef}
              type="text"
              id="zipcode_box"
              placeholder="郵遞區號"
              value={zipcode}
              onChange={(e) => setZipcode(e.target.value)}
              maxLength={5}
              className="w-full md:w-32 px-4 py-2 border border-primary/30 bg-card shadow-sm rounded-xl hover:border-primary/50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>
      </div>
    </nav>
  );
}

/**
 * 搜尋輸入框子元件
 */
interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
}

function SearchInput({ value, onChange }: SearchInputProps) {
  return (
    <Input
      type="text"
      placeholder="輸入地址或關鍵字..."
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full md:flex-1 border border-primary/30 bg-card shadow-sm rounded-xl hover:border-primary/50 transition-colors focus:border-primary"
    />
  );
}
