'use client';

import { Header } from './components/Header';
import { FilterBar } from './components/FilterBar';
import { DataTable } from './components/DataTable';
import { MapSection } from './components/MapSection';

/**
 * 主頁面元件
 * 展示整個應用程式的佈局和結構
 */
export default function Page() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      {/* 頁面標題區域 */}
      <PageHeader />

      {/* 主要內容區域 */}
      <PageContent />

      {/* 底部間距 */}
      <PageFooter />
    </main>
  );
}

/**
 * 頁面標題區塊
 */
function PageHeader() {
  return (
    <header className="border-b border-primary/10 bg-card/50 backdrop-blur-sm">
      <Header />
    </header>
  );
}

/**
 * 頁面主要內容區塊
 */
function PageContent() {
  return (
    <div className="w-full max-w-full px-2 md:px-4 lg:px-6 py-4 md:py-6 lg:py-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6 lg:gap-8 auto-rows-max">
        {/* 左側：資料表格 */}
        <ContentSection>
          <DataTable />
        </ContentSection>

        {/* 右側：地圖 */}
        <ContentSection>
          <MapSection />
        </ContentSection>
      </div>
    </div>
  );
}

/**
 * 頁面底部間距
 */
function PageFooter() {
  return <div className="pb-4 md:pb-6 lg:pb-8" />;
}

/**
 * 內容區塊包裝元件
 */
interface ContentSectionProps {
  children: React.ReactNode;
}

function ContentSection({ children }: ContentSectionProps) {
  return <div className="w-full">{children}</div>;
}
