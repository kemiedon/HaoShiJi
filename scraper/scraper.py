from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
import random
import os


class FoodSafetyDataScraper:
    def __init__(self):
        # 設定Chrome選項
        options = webdriver.ChromeOptions()

        # 添加User-Agent來模擬真實瀏覽器
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # 禁用自動化標記
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # 其他選項
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        # 如果不想看到瀏覽器視窗，可以取消註解下面這行
        # options.add_argument('--headless')

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)
        self.all_data = []

    def random_sleep(self, min_sec=1, max_sec=3):
        """隨機延遲，模擬人類行為"""
        time.sleep(random.uniform(min_sec, max_sec))

    def open_page_and_wait(self):
        """開啟網頁並等待使用者手動完成查詢"""
        try:
            print(f"\n{'='*60}")
            print(f"手動查詢模式")
            print(f"{'='*60}")

            # 開啟網頁
            print("  > 正在開啟網頁...")
            self.driver.get("https://imap.health.gov.tw/App_Prog/Analysis3.aspx")
            self.random_sleep(2, 3)
            print("  ✓ 網頁已開啟")

            print("\n" + "=" * 60)
            print("請在瀏覽器中手動完成以下操作：")
            print("  1. 設定起始日期（例如：2025-01-01）")
            print("  2. 設定結束日期（例如：2025-12-29）")
            print("  3. 點擊【查詢】按鈕")
            print("  4. 等待查詢結果顯示出來")
            print("=" * 60)

            input("\n完成後按 Enter 鍵繼續爬蟲...")
            print("\n" + "=" * 60)
            print("開始自動抓取資料")
            print("=" * 60 + "\n")
            return True

        except Exception as e:
            print(f"  ✗ 開啟網頁時發生錯誤: {e}")
            import traceback

            traceback.print_exc()
            return False

    def setup_date_and_search(self, start_date="2025-01-01", end_date="2025-12-29"):
        """設定日期並執行查詢"""
        try:
            print(f"\n{'='*60}")
            print(f"步驟 1: 開啟網頁並設定查詢條件")
            print(f"{'='*60}")

            # 開啟網頁
            print("  > 正在載入網頁...")
            self.driver.get("https://imap.health.gov.tw/App_Prog/Analysis3.aspx")
            self.random_sleep(3, 5)
            print("  ✓ 網頁載入完成")

            # 設定起始日期
            print(f"  > 設定起始日期: {start_date}")
            start_date_input = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        "ContentPlaceHolder1_ContentPlaceHolder2_uccheck_dateS_cxtDateYMD",
                    )
                )
            )
            start_date_input.clear()
            self.random_sleep(0.3, 0.5)
            start_date_input.send_keys(start_date)
            self.random_sleep(0.5, 1)
            print(f"  ✓ 起始日期已設定為 {start_date}")

            # 設定結束日期
            print(f"  > 設定結束日期: {end_date}")
            end_date_input = self.driver.find_element(
                By.ID,
                "ContentPlaceHolder1_ContentPlaceHolder2_uccheck_dateE_cxtDateYMD",
            )
            end_date_input.clear()
            self.random_sleep(0.3, 0.5)
            end_date_input.send_keys(end_date)
            self.random_sleep(0.5, 1)
            print(f"  ✓ 結束日期已設定為 {end_date}")

            # 點擊查詢按鈕
            print("  > 點擊查詢按鈕...")
            search_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "btnSearch"))
            )
            search_btn.click()
            print("  ✓ 查詢按鈕已點擊")

            # 等待查詢結果載入
            print("  > 等待查詢結果載入...")
            self.random_sleep(4, 6)

            # 確認查詢結果已載入
            try:
                self.wait.until(
                    EC.text_to_be_present_in_element((By.ID, "num_1"), "家")
                )
                print("  ✓ 查詢結果載入完成\n")
                print(f"{'='*60}")
                print(f"步驟 2: 開始抓取各業別資料")
                print(f"{'='*60}\n")
                return True
            except TimeoutException:
                print("  ✗ 查詢結果載入逾時")
                return False

        except Exception as e:
            print(f"  ✗ 設定查詢條件時發生錯誤: {e}")
            import traceback

            traceback.print_exc()
            return False

    def click_category(self, category_id):
        """點擊特定業別"""
        try:
            category_link = self.wait.until(
                EC.element_to_be_clickable((By.ID, category_id))
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                category_link,
            )
            self.random_sleep(0.5, 1)
            category_link.click()
            self.random_sleep(2, 3)
            return True
        except Exception as e:
            print(f"  ✗ 點擊業別時發生錯誤: {e}")
            return False

    def set_page_size(self, size=50):
        """設定每頁顯示筆數"""
        try:
            page_size_select_element = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        "ContentPlaceHolder1_ContentPlaceHolder2_ucPageDividerPHPS1_uDdlPageSize",
                    )
                )
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                page_size_select_element,
            )
            self.random_sleep(0.5, 1)

            page_size_select = Select(page_size_select_element)
            page_size_select.select_by_value(str(size))
            self.random_sleep(2, 3)
            print(f"    > 已設定每頁顯示 {size} 筆")
            return True
        except Exception as e:
            print(f"    ! 無法設定頁面大小: {e}")
            return False

    def get_current_page_data(self):
        """獲取當前頁面的資料"""
        data_list = []
        try:
            table = self.wait.until(
                EC.presence_of_element_located(
                    (By.ID, "ContentPlaceHolder1_ContentPlaceHolder2_gvSearchList")
                )
            )

            rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # 跳過表頭

            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 3:
                        company_name = cells[0].text.strip()
                        address = cells[1].text.strip()
                        registration_number = cells[2].text.strip()

                        if company_name and registration_number:
                            data = {
                                "company_name": company_name,
                                "address": address,
                                "registration_number": registration_number,
                            }
                            data_list.append(data)
                except Exception as e:
                    continue

            return data_list

        except Exception as e:
            print(f"    ✗ 獲取頁面資料時發生錯誤: {e}")
            return []

    def has_next_page(self):
        """檢查是否有下一頁"""
        try:
            next_btn_container = self.driver.find_element(
                By.ID,
                "ContentPlaceHolder1_ContentPlaceHolder2_ucPageDividerPHPS1_uLkbNext",
            ).find_element(By.XPATH, "..")

            return "aspNetDisabled" not in next_btn_container.get_attribute("class")
        except:
            return False

    def click_next_page(self):
        """點擊下一頁"""
        try:
            next_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "ContentPlaceHolder1_ContentPlaceHolder2_ucPageDividerPHPS1_uLkbNext",
                    )
                )
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                next_btn,
            )
            self.random_sleep(0.5, 1)
            next_btn.click()
            self.random_sleep(2, 3)
            return True
        except Exception as e:
            return False

    def scrape_category(self, category_id, category_name):
        """抓取特定業別的所有資料"""
        print(f"\n[{category_name}]")
        print(f"  > 點擊業別按鈕...")

        if not self.click_category(category_id):
            print(f"  ✗ 無法點擊業別按鈕")
            return []

        print(f"  ✓ 業別切換成功")

        # 設定每頁顯示50筆
        self.set_page_size(50)

        category_data = []
        page_num = 1

        while True:
            print(f"    > 正在抓取第 {page_num} 頁...")
            page_data = self.get_current_page_data()

            if page_data:
                category_data.extend(page_data)
                print(f"    ✓ 第 {page_num} 頁完成，獲取 {len(page_data)} 筆資料")

                # 如果當前頁資料少於50筆，表示是最後一頁，不需要再翻頁
                if len(page_data) < 50:
                    print(f"    ✓ 當前頁資料少於 50 筆，已到最後一頁")
                    break
            else:
                print(f"    ! 第 {page_num} 頁沒有資料")
                break

            # 檢查是否有下一頁按鈕且可點擊
            if self.has_next_page():
                if self.click_next_page():
                    page_num += 1
                else:
                    print(f"    ! 無法切換到下一頁，停止抓取")
                    break
            else:
                print(f"    ✓ 已經是最後一頁")
                break

        print(f"  ✓ [{category_name}] 完成，共 {len(category_data)} 筆資料")
        return category_data

    def scrape_all_categories(self, manual_mode=False):
        """抓取所有業別的資料"""
        categories = [
            ("A_1", "餐盒食品"),
            ("A_2", "學校及機關附設廚房"),
            ("A_3", "自助餐飲及外燴飲食業"),
            ("A_4", "烘焙業"),
            ("A_5", "早餐速食業"),
            ("A_6", "飲料業"),
            ("A_7", "觀光飯店"),
            ("A_8", "其他"),
        ]

        # 根據模式選擇設定方式
        if manual_mode:
            if not self.open_page_and_wait():
                print("\n✗ 無法開啟網頁，程式終止")
                return
        else:
            if not self.setup_date_and_search():
                print("\n✗ 無法完成查詢設定，程式終止")
                return

        # 開始抓取各業別
        for idx, (category_id, category_name) in enumerate(categories, 1):
            try:
                print(f"\n進度: [{idx}/{len(categories)}]")
                data = self.scrape_category(category_id, category_name)
                self.all_data.extend(data)
                print(f"  累計已抓取: {len(self.all_data)} 筆資料")
                self.random_sleep(1, 2)
            except Exception as e:
                print(f"  ✗ 抓取 {category_name} 時發生錯誤: {e}")
                import traceback

                traceback.print_exc()
                continue

        print(f"\n{'='*60}")
        print(f"所有資料抓取完成！")
        print(f"總共獲取 {len(self.all_data)} 筆資料")
        print(f"{'='*60}\n")

    def save_to_json(self, filename="food_business_data.json"):
        """儲存資料到JSON檔案"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.all_data, f, ensure_ascii=False, indent=2)

            abs_path = os.path.abspath(filename)
            print(f"✓ 資料已儲存至: {abs_path}")
            print(f"  總筆數: {len(self.all_data)}")
            return True
        except Exception as e:
            print(f"✗ 儲存檔案時發生錯誤: {e}")
            return False

    def close(self):
        """關閉瀏覽器"""
        try:
            self.driver.quit()
            print("✓ 瀏覽器已關閉")
        except:
            pass


def main():
    print("\n" + "=" * 60)
    print("食品業者資料爬蟲程式")
    print("=" * 60)

    # 詢問使用者要使用哪種模式
    print("\n請選擇操作模式：")
    print("  1. 自動模式（程式自動設定日期並查詢）")
    print("  2. 手動模式（您手動完成查詢後，程式再開始爬蟲）")

    while True:
        choice = input("\n請輸入 1 或 2: ").strip()
        if choice in ["1", "2"]:
            break
        print("❌ 請輸入 1 或 2")

    manual_mode = choice == "2"

    if not manual_mode:
        print("\n📅 日期範圍: 2025-01-01 ~ 2025-12-29")

    print("=" * 60)

    scraper = None

    try:
        scraper = FoodSafetyDataScraper()

        # 抓取所有業別資料
        scraper.scrape_all_categories(manual_mode=manual_mode)

        # 儲存到JSON檔案
        if scraper.all_data:
            scraper.save_to_json("food_business_data.json")

            # 顯示統計資訊
            print("\n統計資訊:")
            print(f"  總筆數: {len(scraper.all_data)}")

            # 顯示前3筆資料預覽
            if len(scraper.all_data) > 0:
                print(f"\n前3筆資料預覽:")
                for i, item in enumerate(scraper.all_data[:3], 1):
                    print(
                        f"  {i}. {item['company_name']} - {item['registration_number']}"
                    )
        else:
            print("\n⚠ 沒有抓取到任何資料")

    except KeyboardInterrupt:
        print("\n\n⚠ 程式被使用者中斷")
    except Exception as e:
        print(f"\n✗ 執行時發生錯誤: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if scraper:
            scraper.close()
        print("\n程式結束")


if __name__ == "__main__":
    main()
