/**
 * 地圖展示區塊
 * 顯示 Google Maps iframe
 */
export function MapSection() {
  return (
    <div className="px-3 md:px-4 py-3 md:py-4 h-auto md:h-[500px] flex flex-col">
      <h2 className="text-center mb-3 md:mb-4 text-sm md:text-base lg:text-lg text-primary font-semibold">
        餐廳位置地圖
      </h2>
      <MapContainer />
    </div>
  );
}

/**
 * 地圖容器子元件
 */
function MapContainer() {
  return (
    <div className="flex-1 bg-card rounded-xl shadow-md overflow-hidden border border-primary/10 min-h-[300px] md:min-h-auto">
      <MapIframe />
    </div>
  );
}

/**
 * Google Maps iframe 子元件
 */
function MapIframe() {
  return (
    <iframe
      title="Google Maps - 餐廳位置"
      src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3022.215294721433!2d-73.98565042346486!3d40.75797083538802!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89c25855c6480299%3A0x55194ec5a1ae072e!2sTimes%20Square!5e0!3m2!1sen!2sus!4v1703615873927!5m2!1sen!2sus"
      width="100%"
      height="100%"
      style={{ border: 0 }}
      allowFullScreen
      loading="lazy"
      referrerPolicy="no-referrer-when-downgrade"
    />
  );
}
