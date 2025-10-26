import pandas as pd
import json
from collections import defaultdict

# CSV 읽기
df = pd.read_csv('keywords_20251026.csv', encoding='utf-8-sig')
print(f"Total rows: {len(df)}")
print(f"\n성별: {df['gender'].unique()}")
print(f"연령대 조합: {df['ages'].unique()}")
print(f"카테고리: {df['category'].unique()}")

# 구조화된 JSON 형태로 변환
# 형태: {gender: {ages: {category: [keywords...]}}}
structured = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

for _, row in df.iterrows():
    gender = row['gender']
    ages = row['ages']
    category = row['category']
    
    structured[gender][ages][category].append({
        "rank": row['rank'],
        "keyword": row['keyword']
    })

# 딕셔너리로 변환 (기본 dict로)
result = {}
for gender, ages_dict in structured.items():
    result[gender] = {}
    for ages, category_dict in ages_dict.items():
        result[gender][ages] = {}
        for category, keywords in category_dict.items():
            result[gender][ages][category] = keywords

# JSON 저장
with open('keywords_20251026.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n[OK] 구조화된 JSON 저장 완료!")
print(f"파일 크기: {len(json.dumps(result, ensure_ascii=False)) / 1024:.2f} KB")

# 샘플 출력
print("\n=== 샘플 구조 ===")
print("여성, 10대-20대의 일부:")
sample_gender = list(result.keys())[0]
sample_ages = list(result[sample_gender].keys())[0]
sample_category = list(result[sample_gender][sample_ages].keys())[0]
print(json.dumps({
    sample_gender: {
        sample_ages: {
            sample_category: result[sample_gender][sample_ages][sample_category][:3]
        }
    }
}, ensure_ascii=False, indent=2))

