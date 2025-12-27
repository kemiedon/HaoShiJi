import type { Metadata } from 'next';
import '../style/index.css';

export const metadata: Metadata = {
  title: '好食機 - HaoShiJi',
  description: '快速篩選無食安問題的聚餐餐廳',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=5',
};

function Footer() {
  return (
    <footer className="mt-auto border-t border-primary/10 bg-card/50 backdrop-blur-sm">
      <div className="w-full py-6 px-4 flex items-center justify-center">
        <p className="text-center text-sm text-muted-foreground">
          ©copyright 好食機製作團隊
        </p>
      </div>
    </footer>
  );
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-Hant" suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <meta name="theme-color" content="#D4845F" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
      </head>
      <body className="antialiased">
        <div className="flex flex-col min-h-screen">
          {children}
          <Footer />
        </div>
      </body>
    </html>
  );
}
