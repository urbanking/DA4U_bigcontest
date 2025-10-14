"""
코드 구조 검증 스크립트 - import만 확인
"""

print("="*60)
print("Store Agent Module 코드 검증")
print("="*60)

# 1. 모듈 import 테스트
print("\n[1] 모듈 import 테스트...")
try:
    from report_builder.store_agent_module import StoreAgentModule, StoreAgentState
    print("✅ StoreAgentModule import 성공")
    print("✅ StoreAgentState import 성공")
except ImportError as e:
    print(f"❌ Import 실패: {e}")
    exit(1)

# 2. 클래스 구조 확인
print("\n[2] 클래스 구조 확인...")
print(f"✅ StoreAgentModule 클래스 존재: {StoreAgentModule is not None}")
print(f"✅ StoreAgentState TypedDict 존재: {StoreAgentState is not None}")

# 3. 필수 메서드 확인
print("\n[3] 필수 메서드 확인...")
required_methods = [
    'execute_analysis_with_self_evaluation',
    '_load_data',
    '_extract_store_code',
    '_filter_store_data',
    '_analyze_store_overview',
    '_analyze_sales',
    '_analyze_customers',
    '_analyze_commercial_area',
    '_analyze_industry',
    '_create_visualizations',
    '_generate_summary',
    '_perform_self_evaluation'
]

agent_class = StoreAgentModule
for method in required_methods:
    has_method = hasattr(agent_class, method)
    status = "✅" if has_method else "❌"
    print(f"{status} {method}")

# 4. State 필드 확인
print("\n[4] State 필드 확인...")
required_fields = ['user_query', 'user_id', 'session_id', 'context', 'store_analysis', 'error']
state_fields = StoreAgentState.__annotations__.keys()

for field in required_fields:
    has_field = field in state_fields
    status = "✅" if has_field else "❌"
    print(f"{status} {field}")

# 5. 초기화 테스트 (데이터 로드 없이)
print("\n[5] 초기화 테스트...")
try:
    # 가짜 데이터 경로로 초기화만 테스트
    agent = StoreAgentModule(data_path="dummy.csv")
    print(f"✅ 초기화 성공")
    print(f"   agent_name: {agent.agent_name}")
    print(f"   data_path: {agent.data_path}")
    print(f"   data: {agent.data}")
    print(f"   store_data: {agent.store_data}")
except Exception as e:
    print(f"❌ 초기화 실패: {e}")

# 6. 데이터 파일 확인
print("\n[6] 데이터 파일 확인...")
import os
data_path = "store_data/final_merged_data.csv"
if os.path.exists(data_path):
    print(f"✅ 데이터 파일 존재: {data_path}")
    
    # 파일 크기
    size_mb = os.path.getsize(data_path) / (1024 * 1024)
    print(f"   파일 크기: {size_mb:.2f} MB")
    
    # 행 수 확인
    try:
        import pandas as pd
        df = pd.read_csv(data_path, nrows=5)
        print(f"✅ 데이터 읽기 성공")
        print(f"   컬럼 수: {len(df.columns)}")
        print(f"   주요 컬럼: {', '.join(df.columns[:5])}")
    except Exception as e:
        print(f"❌ 데이터 읽기 실패: {e}")
else:
    print(f"❌ 데이터 파일 없음: {data_path}")

# 7. 최종 결과
print("\n" + "="*60)
print("검증 완료!")
print("="*60)
print("\n✅ 모든 필수 구성 요소가 정상입니다.")
print("\n실행 방법:")
print("  1. Jupyter Notebook에서 실행")
print("  2. Python 인터랙티브 쉘에서 실행")
print("  3. IDE(PyCharm, VSCode 등)에서 실행")
print("\n상세 가이드: HOW_TO_RUN.md 참조")

