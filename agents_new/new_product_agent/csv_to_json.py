import pandas as pd
import json

# CSV 읽기
df = pd.read_csv('keywords_20251026.csv', encoding='utf-8-sig')

# JSON으로 저장
df.to_json('keywords_20251026.json', orient='records', force_ascii=False, indent=2)

print(f"JSON 변환 완료!")
print(f"총 {len(df)}개 레코드")

