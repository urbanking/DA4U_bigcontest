"""
네이버 데이터랩 키워드 크롤링 → CSV 저장

사용법:
    # Jupyter나 일반 Python에서 실행
    python crawl_keywords.py
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import time

from crawler import NaverDatalabClient


def crawl_all_combinations(save_to_csv=True):
    """
    모든 성별/연령 조합으로 크롤링하여 CSV로 저장
    
    Args:
        save_to_csv: CSV로 저장할지 여부
    
    Returns:
        DataFrame with all crawled keywords
    """
    print("="*60)
    print("[크롤링 시작]")
    print("="*60)
    
    # 크롤링할 조합 정의
    categories = ["농산물", "음료", "과자/베이커리"]
    genders = ["남성", "여성", "전체"]
    
    # 연령대 조합
    age_combinations = [
        ["10대"],
        ["20대"],
        ["30대"],
        ["40대"],
        ["50대"],
        ["60대 이상"],
        ["10대", "20대"],
        ["20대", "30대"],
        ["30대", "40대"],
        ["10대", "20대", "30대"],
    ]
    
    print(f"성별: {len(genders)}개")
    print(f"연령 조합: {len(age_combinations)}개")
    print(f"총 조합: {len(genders) * len(age_combinations)}개\n")
    
    # 결과 저장 리스트
    all_results = []
    
    # 크롤러 초기화
    crawler = NaverDatalabClient(headless=True)
    
    total_combinations = len(genders) * len(age_combinations)
    current = 0
    
    try:
        for gender in genders:
            for ages in age_combinations:
                current += 1
                
                ages_str = ', '.join(ages)
                print(f"\n[{current}/{total_combinations}] {gender}, {ages_str}")
                
                try:
                    # 크롤링 실행
                    keywords = crawler.fetch_keywords(
                        categories=categories,
                        gender=gender,
                        ages=ages
                    )
                    
                    # 결과 저장
                    for kw in keywords:
                        all_results.append({
                            'gender': gender,
                            'ages': ages_str,
                            'category': kw['category'],
                            'rank': kw['rank'],
                            'keyword': kw['keyword'],
                            'crawled_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                    
                    print(f"  [OK] {len(keywords)}개 키워드 수집")
                    
                except Exception as e:
                    print(f"  [ERROR] 크롤링 실패: {e}")
                    continue
                
                # 서버 부하 방지를 위한 딜레이
                time.sleep(2)
    
    except KeyboardInterrupt:
        print("\n크롤링 중단됨")
    finally:
        crawler.close()
    
    # DataFrame 생성
    df = pd.DataFrame(all_results)
    
    print("\n" + "="*60)
    print("[크롤링 완료]")
    print(f"총 {len(df)}개 키워드 수집\n")
    print("성별별 통계:")
    print(df.groupby('gender').size())
    print("\n카테고리별 통계:")
    print(df.groupby('category').size())
    
    # CSV 저장
    if save_to_csv and len(df) > 0:
        # 현재 디렉토리에 저장
        output_dir = Path(".")
        
        # 날짜로 저장
        today = datetime.now().strftime("%Y%m%d")
        csv_path = output_dir / f"keywords_{today}.csv"
        
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"\n[OK] CSV 저장 완료: {csv_path}")
        print(f"파일 크기: {csv_path.stat().st_size / 1024:.2f} KB")
    
    return df


def preview_data(df, gender='여성', ages='10대, 20대'):
    """
    특정 조합의 데이터 미리보기
    
    Args:
        df: 크롤링 결과 DataFrame
        gender: 성별
        ages: 연령대 문자열
    """
    print(f"\n{gender}, {ages} Top 10:")
    sample = df[(df['gender'] == gender) & (df['ages'] == ages)].head(10)
    print(sample[['category', 'rank', 'keyword']].to_string(index=False))


if __name__ == "__main__":
    # 크롤링 실행
    df = crawl_all_combinations(save_to_csv=True)
    
    # 미리보기
    print("\n" + "="*60)
    print("[데이터 샘플]")
    preview_data(df, gender='여성', ages='10대, 20대')
    preview_data(df, gender='남성', ages='30대, 40대')

