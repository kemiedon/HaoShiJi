import { useEffect, useRef, useState } from 'react';

declare global {
  interface Window {
    google: any;
  }
}

/**
 * 地圖展示區塊
 * 顯示 Google Maps 並根據搜尋地址更新位置
 */
export function MapSection({ searchAddress }: { searchAddress?: string }) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const geocoderRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const [mapLoaded, setMapLoaded] = useState(false);

  // 初始化地圖
  useEffect(() => {
    if (!mapRef.current || mapLoaded) return;

    const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
    if (!apiKey) {
      console.error('Google Maps API key is missing');
      return;
    }

    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`;
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
      // Initialize the map
      if (mapRef.current && window.google) {
        mapInstanceRef.current = new window.google.maps.Map(mapRef.current, {
          center: { lat: 25.033964, lng: 121.564468 }, // Taipei 101 coordinates
          zoom: 12,
        });
        
        // Initialize geocoder
        geocoderRef.current = new window.google.maps.Geocoder();
        setMapLoaded(true);
      }
    };

    document.head.appendChild(script);

    return () => {
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, [mapLoaded]);

  // 當搜尋地址改變時，更新地圖位置
  useEffect(() => {
    if (!mapLoaded || !searchAddress || !geocoderRef.current || !mapInstanceRef.current) return;

    // 清除之前的標記
    markersRef.current.forEach((marker) => {
      marker.setMap(null);
    });
    markersRef.current = [];

    geocoderRef.current.geocode({ address: searchAddress }, (results: any, status: any) => {
      if (status === 'OK' && results.length > 0) {
        const location = results[0].geometry.location;
        mapInstanceRef.current.setCenter(location);
        mapInstanceRef.current.setZoom(15);

        // 在地圖上添加標記
        const marker = new window.google.maps.Marker({
          position: location,
          map: mapInstanceRef.current,
          title: searchAddress,
        });
        markersRef.current.push(marker);
      } else {
        console.error('Geocode was not successful for the following reason: ' + status);
      }
    });
  }, [searchAddress, mapLoaded]);

  return (
    <div className="px-3 md:px-4 py-3 md:py-4 h-auto md:h-[500px] flex flex-col">
      <h2 className="text-center mb-3 md:mb-4 text-sm md:text-base lg:text-lg text-primary font-semibold">
        餐廳位置地圖
      </h2>
      <div ref={mapRef} style={{ width: '100%', height: '400px' }} />
    </div>
  );
}
