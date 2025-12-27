/**
 * 應用程式標題和介紹區塊
 */
export function Header() {
  return (
    <header className="px-4 py-6 md:px-8 md:py-8 mb-4 md:mb-6 text-center">
      <div className="mb-2 md:mb-3 flex flex-col md:flex-row items-center justify-center gap-2 md:gap-3">
        <h1 className="text-2xl md:text-4xl lg:text-5xl text-primary font-bold">
          好食機
        </h1>
        <span className="md:ml-3 text-xs md:text-base lg:text-lg text-muted-foreground opacity-70 align-baseline font-medium">
          HaoShiJi
        </span>
      </div>
      <p className="text-xs md:text-sm lg:text-base text-muted-foreground px-2">
        快速篩選無食安問題的聚餐餐廳
      </p>
    </header>
  );
}
