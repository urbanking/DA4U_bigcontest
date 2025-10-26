"""
네이버 데이터랩 쇼핑 인사이트 크롤러
식품 > 하위 카테고리(농산물/음료/과자·베이커리) Top10 키워드 수집
"""
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time


# 네이버 데이터랩 URL
URL = 'https://datalab.naver.com/shoppingInsight/sCategory.naver'

# XPath 상수
X_FIRST_CLASS_BTN = '//*[@id="content"]/div[2]/div/div[1]/div/div/div[1]/div/div[1]/span'
X_FIRST_CLASS_FOOD_ITEM = '//ul/li/a[contains(text(),"식품")]'
X_SUBCLASS_BTN = '//*[@id="content"]/div[2]/div/div[1]/div/div/div[1]/div/div[2]/span'
X_SUBCLASS_ITEM_FMT = '//ul/li/a[contains(text(), "{name}")]'
X_GENDER_FEMALE = '//*[@id="19_gender_1"]'
X_GENDER_MALE   = '//*[@id="19_gender_2"]'
X_AGE = {
    "10대": '//*[@id="20_age_1"]',
    "20대": '//*[@id="20_age_2"]',
    "30대": '//*[@id="20_age_3"]',
    "40대": '//*[@id="20_age_4"]',
    "50대": '//*[@id="20_age_5"]',
    "60대 이상": '//*[@id="20_age_6"]'
}
X_SUBMIT = '//*[@id="content"]/div[2]/div/div[1]/div/a'
X_TOP_ITEM_FMT = '//*[@id="content"]/div[2]/div/div[2]/div[2]/div/div/div[1]/ul/li[{i}]/a'


class NaverDatalabClient:
    """네이버 데이터랩 쇼핑 인사이트 크롤러"""
    
    def __init__(self, headless: bool = True, implicit_wait: int = 60):
        """
        크롤러 초기화
        
        Args:
            headless: 헤드리스 모드 사용 여부
            implicit_wait: 암묵적 대기 시간(초)
        """
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.browser = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=opts
        )
        self.browser.set_page_load_timeout(120)  # 페이지 로드 타임아웃 120초
        self.browser.get(URL)
        self.browser.implicitly_wait(implicit_wait)

    def _select_food_root(self):
        """최상위 카테고리에서 '식품' 선택"""
        b = self.browser
        b.find_element(By.XPATH, X_FIRST_CLASS_BTN).click()
        time.sleep(0.5)
        b.find_element(By.XPATH, X_FIRST_CLASS_FOOD_ITEM).click()
        time.sleep(0.5)

    def _select_subcategory(self, name: str):
        """
        하위 카테고리 선택
        
        Args:
            name: 카테고리명 (예: "농산물", "음료", "과자/베이커리")
        """
        b = self.browser
        b.find_element(By.XPATH, X_SUBCLASS_BTN).click()
        time.sleep(0.5)
        b.find_element(By.XPATH, X_SUBCLASS_ITEM_FMT.format(name=name)).click()
        time.sleep(0.5)

    def _set_gender(self, gender: str):
        """
        성별 필터 설정
        
        Args:
            gender: "남성", "여성", 또는 "전체"
        """
        b = self.browser
        if gender == "여성":
            b.find_element(By.XPATH, X_GENDER_FEMALE).click()
        elif gender == "남성":
            b.find_element(By.XPATH, X_GENDER_MALE).click()
        else:
            # 전체: 체크박스 미선택 유지
            pass
        time.sleep(0.3)

    def _set_ages(self, ages: List[str]):
        """
        연령 필터 설정
        
        Args:
            ages: 연령대 리스트 (예: ["10대", "20대"])
        """
        b = self.browser
        for a in ages:
            if a in X_AGE:
                b.find_element(By.XPATH, X_AGE[a]).click()
                time.sleep(0.2)

    def _submit(self):
        """조회 버튼 클릭 및 결과 대기"""
        self.browser.find_element(By.XPATH, X_SUBMIT).click()
        time.sleep(2.5)  # 결과 로딩 대기

    def _read_top10(self, category: str) -> List[Dict]:
        """
        Top10 키워드 추출
        
        Args:
            category: 현재 조회 중인 카테고리명
            
        Returns:
            List of {"category": str, "rank": int, "keyword": str}
        """
        out: List[Dict] = []
        for i in range(1, 11):
            try:
                text = self.browser.find_element(
                    By.XPATH, X_TOP_ITEM_FMT.format(i=i)
                ).text
                parts = text.split("\n")
                if len(parts) >= 2:
                    rank = int(parts[0])
                    keyword = parts[1]
                    out.append({
                        "category": category, 
                        "rank": rank, 
                        "keyword": keyword
                    })
            except Exception as e:
                print(f"[WARN] Failed to extract rank {i}: {e}")
                continue
        return out

    def fetch_keywords(
        self, 
        categories: List[str], 
        gender: str, 
        ages: List[str]
    ) -> List[Dict]:
        """
        네이버 데이터랩에서 키워드 수집 (메인 메서드)
        
        Args:
            categories: 조회할 카테고리 리스트 (예: ["농산물", "음료"])
            gender: 성별 필터 ("남성", "여성", "전체")
            ages: 연령 필터 (예: ["10대", "20대"])
            
        Returns:
            전체 키워드 리스트 [{"category": str, "rank": int, "keyword": str}, ...]
        """
        self._select_food_root()
        results: List[Dict] = []
        
        for c in categories:
            try:
                self._select_subcategory(c)
                self._set_gender(gender)
                self._set_ages(ages)
                self._submit()
                keywords = self._read_top10(category=c)
                results.extend(keywords)
                print(f"[OK] {c} 카테고리에서 {len(keywords)}개 키워드 수집")
            except Exception as e:
                print(f"[ERROR] {c} 카테고리 크롤링 실패: {e}")
                continue
        
        return results

    def close(self):
        """브라우저 종료"""
        try:
            self.browser.quit()
        except Exception:
            pass
