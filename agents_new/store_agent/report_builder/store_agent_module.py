"""
Store Agent Module
매장 분석 전문 에이전트 모듈 - 개별 리포트 생성
"""

from typing import Dict, Any, Optional, List, Tuple, TypedDict
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import re
from io import BytesIO
import base64
import json
import os
from pathlib import Path
import platform

# matplotlib import 및 설정
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 설정
system = platform.system()
if system == "Windows":
    plt.rcParams['font.family'] = 'Malgun Gothic'
elif system == "Darwin":
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'NanumGothic'
matplotlib.rcParams['axes.unicode_minus'] = False

print("[OK] Matplotlib loaded in store_agent_module")

logger = logging.getLogger(__name__)

class StoreAgentState(TypedDict):
    """Store Agent State 정의"""
    user_query: str
    user_id: str
    session_id: str
    context: Dict[str, Any]
    store_analysis: Optional[Dict[str, Any]]
    error: Optional[str]

class StoreAgentModule:
    """매장 분석 모듈"""
    
    def __init__(self, data_path: Optional[str] = None):
        self.agent_name = "StoreAgent"
        self.data_path = data_path or self._get_default_data_path()
        self.data = None
        self.store_data = None
        logger.info(f"매장 분석 에이전트 모듈 초기화 완료 - 데이터 경로: {self.data_path}")
    
    def _get_default_data_path(self) -> str:
        """기본 데이터 경로 반환"""
        # report_builder에서 상위 디렉토리(store_agent)로 이동 후 store_data 접근
        current_dir = Path(__file__).parent.parent
        data_path = current_dir / "store_data" / "final_merged_data.csv"
        return str(data_path)
    
    async def execute_analysis_with_self_evaluation(self, state: StoreAgentState) -> StoreAgentState:
        """매장 분석 실행"""
        user_query = state["user_query"]
        user_id = state["user_id"]
        session_id = state["session_id"]
        context = state.get("context", {})
        
        logger.info(f"매장 분석 시작 - 사용자: {user_id}, 쿼리: {user_query}")
        
        try:
            # JSON 파일 처리 확인
            json_input = self._check_json_input(user_query, context)
            
            if json_input:
                # JSON 파일에서 매장 코드 추출
                store_code = self._extract_store_code_from_json(json_input)
                if not store_code:
                    return {**state, "error": "JSON 파일에서 매장 코드를 찾을 수 없습니다."}
            else:
                # 사용자 쿼리에서 매장 코드 추출
                store_code = self._extract_store_code(user_query)
                if not store_code:
                    return {**state, "error": "매장 코드를 찾을 수 없습니다. 쿼리에 매장 코드를 포함하거나 JSON 파일을 제공해주세요."}
            
            # 데이터 로드
            await self._load_data()
            
            # 특정 매장 데이터 필터링
            self.store_data = self._filter_store_data(store_code)
            if self.store_data.empty:
                return {**state, "error": f"매장 코드 {store_code}에 대한 데이터를 찾을 수 없습니다."}
            
            # 분석 수행 (memory_insights 제거)
            analysis_result = await self._perform_store_analysis(user_query, user_id, context)
            evaluation_result = await self._perform_self_evaluation(analysis_result, user_query)
            
            # JSON 형태로 결과 출력
            json_output = self._format_json_output(analysis_result, evaluation_result, store_code)
            
            # JSON 파일로 저장
            output_file_path = await self._save_json_report(json_output, store_code, session_id)
            
            logger.info(f"매장 분석 완료 - 품질점수: {evaluation_result['quality_score']}")
            logger.info(f"JSON 리포트 저장: {output_file_path}")
            
            # State 업데이트
            return {
                **state,
                "store_analysis": {
                    "analysis_result": analysis_result,
                    "evaluation": evaluation_result,
                    "json_output": json_output,
                    "output_file_path": output_file_path,
                    "store_code": store_code
                },
                "error": None
            }
            
        except Exception as e:
            logger.error(f"매장 분석 에러: {e}")
            return {**state, "error": str(e)}
    
    async def _load_data(self):
        """데이터 로드"""
        try:
            if self.data is None:
                self.data = pd.read_csv(self.data_path)
                logger.info(f"데이터 로드 완료: {len(self.data)} 행 - 경로: {self.data_path}")
        except Exception as e:
            logger.error(f"데이터 로드 실패: {e}")
            raise
    
    def _extract_store_code(self, user_query: str) -> Optional[str]:
        """사용자 쿼리에서 매장 코드 추출"""
        # 매장 코드 패턴 (예: 000F03E44A)
        code_pattern = r'\b[A-Z0-9]{10}\b'
        match = re.search(code_pattern, user_query)
        return match.group(0) if match else None
    
    def _filter_store_data(self, store_code: str) -> pd.DataFrame:
        """특정 매장의 데이터 필터링"""
        return self.data[self.data['코드'] == store_code].copy()
    
    def _check_json_input(self, user_query: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """JSON 입력 확인 및 파싱"""
        # context에서 JSON 파일 경로 확인
        if context.get('json_file_path'):
            try:
                with open(context['json_file_path'], 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"JSON 파일 읽기 실패: {e}")
                return None
        
        # user_query에서 JSON 파일 경로 패턴 확인
        json_pattern = r'json[_\s]*file[_\s]*path[:\s]*["\']?([^"\'\s]+)["\']?'
        match = re.search(json_pattern, user_query, re.IGNORECASE)
        if match:
            file_path = match.group(1)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"JSON 파일 읽기 실패: {e}")
                return None
        
        # user_query에서 직접 JSON 문자열 확인
        json_pattern = r'\{.*\}'
        match = re.search(json_pattern, user_query, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception as e:
                logger.error(f"JSON 문자열 파싱 실패: {e}")
                return None
        
        return None
    
    def _extract_store_code_from_json(self, json_data: Dict[str, Any]) -> Optional[str]:
        """JSON 데이터에서 매장 코드 추출"""
        # 다양한 필드명으로 매장 코드 찾기
        possible_fields = ['store_code', 'storeCode', 'code', '매장코드', 'store_id', 'storeId']
        
        for field in possible_fields:
            if field in json_data and json_data[field]:
                return str(json_data[field])
        
        # 중첩된 객체에서 찾기
        if 'store' in json_data:
            store_info = json_data['store']
            for field in possible_fields:
                if field in store_info and store_info[field]:
                    return str(store_info[field])
        
        # 분석 요청 정보에서 찾기
        if 'analysis_request' in json_data:
            req_info = json_data['analysis_request']
            for field in possible_fields:
                if field in req_info and req_info[field]:
                    return str(req_info[field])
        
        return None
    
    def _format_json_output(self, analysis_result: Dict[str, Any], evaluation_result: Dict[str, Any], store_code: str) -> Dict[str, Any]:
        """분석 결과를 JSON 형태로 포맷팅"""
        store_overview = analysis_result['store_overview']
        sales_analysis = analysis_result['sales_analysis']
        customer_analysis = analysis_result['customer_analysis']
        commercial_analysis = analysis_result['commercial_area_analysis']
        industry_analysis = analysis_result['industry_analysis']
        summary = analysis_result['summary']
        
        # Base64 이미지를 파일 경로로 변환
        visualizations = {}
        current_dir = Path(__file__).parent.parent
        chart_dir = current_dir / "outputs" / "charts"
        chart_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 차트 파일 저장
        chart_files = {}
        for chart_name, base64_data in analysis_result['visualizations'].items():
            if base64_data:
                chart_filename = f"{store_code}_{chart_name}_{timestamp}.png"
                chart_path = chart_dir / chart_filename
                
                try:
                    with open(chart_path, 'wb') as f:
                        f.write(base64.b64decode(base64_data))
                    chart_files[chart_name] = str(chart_path)
                except Exception as e:
                    logger.error(f"차트 저장 실패 {chart_name}: {e}")
                    chart_files[chart_name] = None
        
        json_output = {
            "report_metadata": {
                "store_code": store_code,
                "analysis_date": summary['analysis_date'],
                "agent_name": self.agent_name,
                "report_version": "1.0",
                "quality_score": evaluation_result['quality_score']
            },
            "store_overview": {
                "code": store_overview['code'],
                "name": store_overview['name'],
                "address": store_overview['address'],
                "industry": store_overview['industry'],
                "brand": store_overview['brand'],
                "commercial_area": store_overview['commercial_area'],
                "record_months": store_overview['record_months'],
                "operating_months": round(store_overview['operating_months'], 1),
                "store_age": store_overview['store_age']
            },
            "sales_analysis": {
                "trends": {
                    "sales_amount": {
                        "trend": sales_analysis['sales_analysis']['sales_amount']['trend'],
                        "stability": sales_analysis['sales_analysis']['sales_amount']['stability'],
                        "data_points": len(sales_analysis['sales_analysis']['sales_amount']['data'])
                    },
                    "sales_count": {
                        "trend": sales_analysis['sales_analysis']['sales_count']['trend'],
                        "stability": sales_analysis['sales_analysis']['sales_count']['stability'],
                        "data_points": len(sales_analysis['sales_analysis']['sales_count']['data'])
                    },
                    "unique_customers": {
                        "trend": sales_analysis['sales_analysis']['unique_customers']['trend'],
                        "stability": sales_analysis['sales_analysis']['unique_customers']['stability'],
                        "data_points": len(sales_analysis['sales_analysis']['unique_customers']['data'])
                    },
                    "avg_transaction": {
                        "trend": sales_analysis['sales_analysis']['avg_transaction']['trend'],
                        "stability": sales_analysis['sales_analysis']['avg_transaction']['stability'],
                        "data_points": len(sales_analysis['sales_analysis']['avg_transaction']['data'])
                    }
                },
                "industry_comparison": {
                    "same_industry_sales_amount": {
                        "trend": sales_analysis['industry_comparison']['same_industry_sales_amount']['trend'],
                        "average": round(sales_analysis['industry_comparison']['same_industry_sales_amount']['average'], 1)
                    },
                    "same_industry_sales_count": {
                        "trend": sales_analysis['industry_comparison']['same_industry_sales_count']['trend'],
                        "average": round(sales_analysis['industry_comparison']['same_industry_sales_count']['average'], 1)
                    }
                },
                "rankings": {
                    "industry_rank": {
                        "trend": sales_analysis['ranking_analysis']['industry_rank']['trend'],
                        "average": round(sales_analysis['ranking_analysis']['industry_rank']['average'], 1)
                    },
                    "commercial_rank": {
                        "trend": sales_analysis['ranking_analysis']['commercial_rank']['trend'],
                        "average": round(sales_analysis['ranking_analysis']['commercial_rank']['average'], 1)
                    }
                },
                "cancellation_analysis": {
                    "average_grade": round(sales_analysis['cancellation_analysis']['average_grade'], 1) if pd.notna(sales_analysis['cancellation_analysis']['average_grade']) else None,
                    "grade_distribution": sales_analysis['cancellation_analysis']['grade_distribution'],
                    "recommendation": sales_analysis['cancellation_analysis']['recommendation']
                },
                "delivery_analysis": {
                    "trend": sales_analysis['delivery_analysis']['trend'],
                    "average": round(sales_analysis['delivery_analysis']['average'], 1) if sales_analysis['delivery_analysis']['average'] is not None else None
                }
            },
            "customer_analysis": {
                "gender_distribution": {
                    "male_ratio": round(customer_analysis['gender_analysis']['male_ratio'], 1),
                    "female_ratio": round(customer_analysis['gender_analysis']['female_ratio'], 1)
                },
                "age_group_distribution": {
                    age_group: round(ratio, 1) 
                    for age_group, ratio in customer_analysis['age_group_analysis'].items()
                },
                "detailed_customer_ratios": {
                    category: round(ratio, 1) 
                    for category, ratio in list(customer_analysis['detailed_ratios'].items())[:10]  # 상위 10개만
                },
                "customer_type_analysis": {
                    "new_customers": {
                        "ratio": round(customer_analysis['customer_type_analysis']['new_customers']['ratio'], 1),
                        "trend": customer_analysis['customer_type_analysis']['new_customers']['trend']
                    },
                    "returning_customers": {
                        "ratio": round(customer_analysis['customer_type_analysis']['returning_customers']['ratio'], 1),
                        "trend": customer_analysis['customer_type_analysis']['returning_customers']['trend']
                    },
                    "customer_distribution": {
                        "residential": round(customer_analysis['customer_type_analysis']['customer_distribution']['residential'], 1),
                        "workplace": round(customer_analysis['customer_type_analysis']['customer_distribution']['workplace'], 1),
                        "floating": round(customer_analysis['customer_type_analysis']['customer_distribution']['floating'], 1)
                    }
                }
            },
            "commercial_area_analysis": {
                "commercial_area": commercial_analysis.get('commercial_area', 'N/A'),
                "analysis_available": commercial_analysis.get('analysis_available', False),
                "total_stores_in_area": commercial_analysis.get('total_stores_in_area', 0),
                "average_sales_analysis": commercial_analysis.get('average_sales_analysis', {}),
                "termination_analysis": commercial_analysis.get('termination_analysis', {}),
                "average_customer_segments": commercial_analysis.get('average_customer_segments', {})
            },
            "industry_analysis": {
                "industry": industry_analysis.get('industry', 'N/A'),
                "analysis_available": industry_analysis.get('analysis_available', False),
                "total_stores_in_industry": industry_analysis.get('total_stores_in_industry', 0),
                "average_sales_analysis": industry_analysis.get('average_sales_analysis', {}),
                "termination_analysis": industry_analysis.get('termination_analysis', {}),
                "delivery_analysis": industry_analysis.get('delivery_analysis', {}),
                "average_customer_segments": industry_analysis.get('average_customer_segments', {})
            },
            "summary": {
                "key_insights": summary['key_insights'],
                "main_problems": summary['main_problems'],
                "recommendations": summary['recommendations']
            },
            "visualizations": {
                "chart_files": chart_files,
                "available_charts": list(chart_files.keys())
            },
            "evaluation": {
                "quality_score": round(evaluation_result['quality_score'], 2),
                "completeness": round(evaluation_result['completeness'], 2),
                "accuracy": round(evaluation_result['accuracy'], 2),
                "relevance": round(evaluation_result['relevance'], 2),
                "actionability": round(evaluation_result['actionability'], 2),
                "feedback": evaluation_result['feedback']
            }
        }
        
        return json_output
    
    async def _save_json_report(self, json_output: Dict[str, Any], store_code: str, session_id: str) -> str:
        """JSON 리포트를 파일로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"store_analysis_report_{store_code}_{timestamp}.json"
        
        # 리포트 디렉토리 생성
        current_dir = Path(__file__).parent.parent
        report_dir = current_dir / "outputs" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = report_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_output, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON 리포트 저장 완료: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"JSON 리포트 저장 실패: {e}")
            raise
    
    async def _perform_store_analysis(self, user_query: str, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """매장 분석 수행"""
        logger.info("매장 분석 시작")
        
        analysis_result = {
            "store_overview": await self._analyze_store_overview(),
            "sales_analysis": await self._analyze_sales(),
            "customer_analysis": await self._analyze_customers(),
            "commercial_area_analysis": await self._analyze_commercial_area(),
            "industry_analysis": await self._analyze_industry(),
            "visualizations": await self._create_visualizations(),
            "summary": await self._generate_summary()
        }
        
        return analysis_result
    
    async def _analyze_store_overview(self) -> Dict[str, Any]:
        """1. 점포 개요 분석"""
        store_info = self.store_data.iloc[0]
        
        # 주소 처리
        address = store_info['기준면적']
        if address.startswith('서울'):
            formatted_address = address.replace('서울특별시', '서울')
        else:
            formatted_address = address
        
        # 업종 처리
        industry_sub = store_info['업종_소분류']
        industry_mid = store_info['업종_중분류']
        
        # 소분류가 100개 이상인지 확인
        sub_count = len(self.data[self.data['업종_소분류'] == industry_sub])
        if sub_count >= 100:
            industry_category = industry_sub
        else:
            industry_category = industry_mid
        
        # 브랜드 처리
        brand_code = store_info['브랜드코드']
        if pd.isna(brand_code) or brand_code == '':
            brand_name = "브랜드 없음"
        else:
            # 숫자 제거하여 브랜드명 추출
            brand_name = re.sub(r'\d+$', '', str(brand_code))
        
        # 상권 처리
        commercial_code = store_info['상권코드']
        commercial_area = "중심상권 아님" if commercial_code == '미표기' else commercial_code
        
        # 기록개월수
        record_months = len(self.store_data)
        
        # 점포 운영개월수 (평균) - NaN 처리
        operating_months = self.store_data['운영개월수'].mean()
        if pd.isna(operating_months):
            operating_months = 0
        
        # 점포 연령 분류
        if operating_months < 12:
            store_age = "신생 매장"
        elif operating_months > 60:
            store_age = "기존 매장"
        else:
            store_age = "성숙 매장"
        
        return {
            "code": store_info['코드'],
            "name": store_info['가맹점명'],
            "address": formatted_address,
            "industry": industry_category,
            "brand": brand_name,
            "commercial_area": commercial_area,
            "record_months": record_months,
            "operating_months": operating_months,
            "store_age": store_age
        }
    
    async def _analyze_sales(self) -> Dict[str, Any]:
        """2. 가게 매출 분석"""
        # 매출 데이터 정렬 (시간순)
        sales_data = self.store_data.sort_values('기준년월')
        
        # 매출 분석
        sales_analysis = {
            "sales_amount": {
                "data": sales_data['매출금액'].tolist(),
                "months": sales_data['기준년월'].tolist(),
                "trend": self._calculate_trend(sales_data['매출금액']),
                "stability": self._calculate_stability(sales_data['매출금액'])
            },
            "sales_count": {
                "data": sales_data['매출건수'].tolist(),
                "months": sales_data['기준년월'].tolist(),
                "trend": self._calculate_trend(sales_data['매출건수']),
                "stability": self._calculate_stability(sales_data['매출건수'])
            },
            "unique_customers": {
                "data": sales_data['유니크고객수'].tolist(),
                "months": sales_data['기준년월'].tolist(),
                "trend": self._calculate_trend(sales_data['유니크고객수']),
                "stability": self._calculate_stability(sales_data['유니크고객수'])
            },
            "avg_transaction": {
                "data": sales_data['객단가'].tolist(),
                "months": sales_data['기준년월'].tolist(),
                "trend": self._calculate_trend(sales_data['객단가']),
                "stability": self._calculate_stability(sales_data['객단가'])
            }
        }
        
        # 동일 업종 대비 매출
        industry_comparison = {
            "same_industry_sales_amount": {
                "data": sales_data['동종매출금액%'].tolist(),
                "months": sales_data['기준년월'].tolist(),
                "trend": self._calculate_trend(sales_data['동종매출금액%']),
                "average": sales_data['동종매출금액%'].mean() if not sales_data['동종매출금액%'].isna().all() else 0
            },
            "same_industry_sales_count": {
                "data": sales_data['동종매출건수%'].tolist(),
                "months": sales_data['기준년월'].tolist(),
                "trend": self._calculate_trend(sales_data['동종매출건수%']),
                "average": sales_data['동종매출건수%'].mean() if not sales_data['동종매출건수%'].isna().all() else 0
            }
        }
        
        # 매출 순위
        ranking_analysis = {
            "industry_rank": {
                "data": sales_data['동종매출순위%'].tolist(),
                "months": sales_data['기준년월'].tolist(),
                "trend": self._calculate_rank_trend(sales_data['동종매출순위%']),
                "average": sales_data['동종매출순위%'].mean() if not sales_data['동종매출순위%'].isna().all() else 0
            },
            "commercial_rank": {
                "data": sales_data['동일상권매출순위%'].tolist(),
                "months": sales_data['기준년월'].tolist(),
                "trend": self._calculate_rank_trend(sales_data['동일상권매출순위%']),
                "average": sales_data['동일상권매출순위%'].mean() if not sales_data['동일상권매출순위%'].isna().all() else 0
            }
        }
        
        # 취소율 분석
        cancellation_data = sales_data['취소율'].dropna()
        cancellation_analysis = {
            "data": cancellation_data.tolist(),
            "months": sales_data.loc[cancellation_data.index, '기준년월'].tolist(),
            "grade_distribution": cancellation_data.value_counts().to_dict(),
            "average_grade": cancellation_data.mean() if len(cancellation_data) > 0 else 0,
            "recommendation": self._get_cancellation_recommendation(cancellation_data)
        }
        
        # 배달매출비율
        delivery_data = sales_data['배달매출비율'].dropna()
        delivery_analysis = {
            "data": delivery_data.tolist(),
            "months": sales_data.loc[delivery_data.index, '기준년월'].tolist(),
            "trend": self._calculate_trend(delivery_data) if len(delivery_data) > 1 else "데이터 부족",
            "average": delivery_data.mean() if len(delivery_data) > 0 else 0
        }
        
        return {
            "sales_analysis": sales_analysis,
            "industry_comparison": industry_comparison,
            "ranking_analysis": ranking_analysis,
            "cancellation_analysis": cancellation_analysis,
            "delivery_analysis": delivery_analysis
        }
    
    async def _analyze_customers(self) -> Dict[str, Any]:
        """3. 고객층 분석"""
        # 최신 데이터 사용
        latest_data = self.store_data.iloc[-1]
        
        # 남녀 비율 계산
        male_columns = ['남20대이하', '남30대', '남40대', '남50대', '남60대이상']
        female_columns = ['여20대이하', '여30대', '여40대', '여50대', '여60대이상']
        
        male_ratio = sum([latest_data[col] for col in male_columns if pd.notna(latest_data[col])])
        female_ratio = sum([latest_data[col] for col in female_columns if pd.notna(latest_data[col])])
        
        gender_analysis = {
            "male_ratio": male_ratio,
            "female_ratio": female_ratio,
            "distribution": {
                "남성": male_ratio,
                "여성": female_ratio
            }
        }
        
        # 연령대 비율 계산
        age_groups = {
            "20대 이하": latest_data['남20대이하'] + latest_data['여20대이하'],
            "30대": latest_data['남30대'] + latest_data['여30대'],
            "40대": latest_data['남40대'] + latest_data['여40대'],
            "50대": latest_data['남50대'] + latest_data['여50대'],
            "60대 이상": latest_data['남60대이상'] + latest_data['여60대이상']
        }
        
        # 세부 비율 (개별 카테고리)
        detailed_ratios = {}
        for col in male_columns + female_columns:
            if pd.notna(latest_data[col]):
                detailed_ratios[col] = latest_data[col]
        
        # 비율 순으로 정렬
        detailed_ratios = dict(sorted(detailed_ratios.items(), key=lambda x: x[1], reverse=True))
        
        # 고객 유형 분석 (최신 데이터)
        customer_type_analysis = {
            "new_customers": {
                "ratio": latest_data['신규고객'] if pd.notna(latest_data['신규고객']) else 0,
                "trend": self._analyze_customer_trend('신규고객')
            },
            "returning_customers": {
                "ratio": latest_data['재방문고객'] if pd.notna(latest_data['재방문고객']) else 0,
                "trend": self._analyze_customer_trend('재방문고객')
            },
            "customer_distribution": {
                "residential": latest_data['거주이용고객'] if pd.notna(latest_data['거주이용고객']) else 0,
                "workplace": latest_data['직장이용고객'] if pd.notna(latest_data['직장이용고객']) else 0,
                "floating": latest_data['유동인구이용고객'] if pd.notna(latest_data['유동인구이용고객']) else 0
            }
        }
        
        return {
            "gender_analysis": gender_analysis,
            "age_group_analysis": age_groups,
            "detailed_ratios": detailed_ratios,
            "customer_type_analysis": customer_type_analysis
        }
    
    async def _analyze_commercial_area(self) -> Dict[str, Any]:
        """4. 상권 분석"""
        store_info = self.store_data.iloc[0]
        commercial_code = store_info['상권코드']
        
        if commercial_code == '미표기':
            return {
                "commercial_area": "중심상권 아님",
                "analysis_available": False,
                "reason": "상권코드가 미표기로 상권 분석 불가"
            }
        
        # 동일 상권 내 매장들 필터링
        commercial_stores = self.data[self.data['상권코드'] == commercial_code]
        
        if len(commercial_stores) == 0:
            return {
                "commercial_area": commercial_code,
                "analysis_available": False,
                "reason": "상권 내 다른 매장 데이터 없음"
            }
        
        # 상권 평균 매출 분석
        commercial_avg_sales = commercial_stores.groupby('기준년월').agg({
            '매출금액': 'mean',
            '매출건수': 'mean',
            '유니크고객수': 'mean',
            '객단가': 'mean'
        }).reset_index()
        
        # 상권 해지가맹점 비중
        termination_ratio = commercial_stores['동일상권해지가맹점비중'].mean()
        if pd.isna(termination_ratio):
            termination_ratio = 0
        
        # 상권 고객층 분석 (평균)
        customer_columns = ['남20대이하', '남30대', '남40대', '남50대', '남60대이상',
                          '여20대이하', '여30대', '여40대', '여50대', '여60대이상']
        
        commercial_customer_avg = {}
        for col in customer_columns:
            commercial_customer_avg[col] = commercial_stores[col].mean()
            if pd.isna(commercial_customer_avg[col]):
                commercial_customer_avg[col] = 0
        
        # 상권 분석 결과
        commercial_analysis = {
            "commercial_area": commercial_code,
            "analysis_available": True,
            "total_stores_in_area": len(commercial_stores['코드'].unique()),
            "average_sales_analysis": {
                "sales_amount_trend": self._calculate_trend(commercial_avg_sales['매출금액']),
                "sales_count_trend": self._calculate_trend(commercial_avg_sales['매출건수']),
                "unique_customers_trend": self._calculate_trend(commercial_avg_sales['유니크고객수']),
                "avg_transaction_trend": self._calculate_trend(commercial_avg_sales['객단가'])
            },
            "termination_analysis": {
                "termination_ratio": round(termination_ratio, 2) if pd.notna(termination_ratio) else None,
                "area_health": "건전한 상권" if termination_ratio < 10 else "위험한 상권" if termination_ratio > 20 else "보통 상권"
            },
            "average_customer_segments": {
                col: round(ratio, 1) for col, ratio in commercial_customer_avg.items() if pd.notna(ratio)
            }
        }
        
        return commercial_analysis
    
    async def _analyze_industry(self) -> Dict[str, Any]:
        """5. 업종 분석"""
        store_info = self.store_data.iloc[0]
        industry_sub = store_info['업종_소분류']
        industry_mid = store_info['업종_중분류']
        
        # 소분류가 100개 이상인지 확인하여 업종 선택
        sub_count = len(self.data[self.data['업종_소분류'] == industry_sub])
        if sub_count >= 100:
            industry_category = industry_sub
            industry_stores = self.data[self.data['업종_소분류'] == industry_sub]
        else:
            industry_category = industry_mid
            industry_stores = self.data[self.data['업종_중분류'] == industry_mid]
        
        if len(industry_stores) == 0:
            return {
                "industry": industry_category,
                "analysis_available": False,
                "reason": "업종 내 다른 매장 데이터 없음"
            }
        
        # 업종 평균 매출 분석
        industry_avg_sales = industry_stores.groupby('기준년월').agg({
            '매출금액': 'mean',
            '매출건수': 'mean',
            '유니크고객수': 'mean',
            '객단가': 'mean'
        }).reset_index()
        
        # 업종 해지가맹점 비중
        termination_ratio = industry_stores['동종해지가맹점%'].mean()
        
        # 업종 평균 배달 분석
        delivery_ratio = industry_stores['배달매출비율'].mean()
        
        # 업종 고객층 분석 (평균)
        customer_columns = ['남20대이하', '남30대', '남40대', '남50대', '남60대이상',
                          '여20대이하', '여30대', '여40대', '여50대', '여60대이상']
        
        industry_customer_avg = {}
        for col in customer_columns:
            industry_customer_avg[col] = industry_stores[col].mean()
        
        # 업종 분석 결과
        industry_analysis = {
            "industry": industry_category,
            "analysis_available": True,
            "total_stores_in_industry": len(industry_stores['코드'].unique()),
            "average_sales_analysis": {
                "sales_amount_trend": self._calculate_trend(industry_avg_sales['매출금액']),
                "sales_count_trend": self._calculate_trend(industry_avg_sales['매출건수']),
                "unique_customers_trend": self._calculate_trend(industry_avg_sales['유니크고객수']),
                "avg_transaction_trend": self._calculate_trend(industry_avg_sales['객단가'])
            },
            "termination_analysis": {
                "termination_ratio": round(termination_ratio, 2) if pd.notna(termination_ratio) else None,
                "industry_health": "건전한 업종" if termination_ratio < 10 else "위험한 업종" if termination_ratio > 20 else "보통 업종"
            },
            "delivery_analysis": {
                "average_delivery_ratio": round(delivery_ratio, 2) if pd.notna(delivery_ratio) else None,
                "delivery_trend": self._calculate_trend(industry_stores['배달매출비율'].dropna()) if len(industry_stores['배달매출비율'].dropna()) > 1 else "데이터 부족"
            },
            "average_customer_segments": {
                col: round(ratio, 1) for col, ratio in industry_customer_avg.items() if pd.notna(ratio)
            }
        }
        
        return industry_analysis
    
    async def _create_visualizations(self) -> Dict[str, str]:
        """시각화 생성"""
        visualizations = {}
        
        # 매출 시계열 그래프 (추세선 포함)
        visualizations['sales_trend'] = self._create_sales_trend_chart()
        
        # 고객층 파이차트
        visualizations['gender_pie'] = self._create_gender_pie_chart()
        visualizations['age_pie'] = self._create_age_pie_chart()
        visualizations['detailed_pie'] = self._create_detailed_pie_chart()
        
        # 순위 시계열 그래프 (추세선 포함)
        visualizations['ranking_trend'] = self._create_ranking_trend_chart()
        
        # 고객층별 시계열 트렌드 차트 (추세선 포함)
        visualizations['customer_trends'] = self._create_customer_trends_chart()
        visualizations['new_returning_trends'] = self._create_new_returning_trends_chart()
        
        return visualizations
    
    def _create_sales_trend_chart(self) -> str:
        """매출 트렌드 차트 생성 (추세선 포함)"""
            
        # 매출 데이터 정렬
        sales_data = self.store_data.sort_values('기준년월')
        
        # 4개 지표를 하나의 차트에 표시
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Store Sales Analysis with Trend Lines', fontsize=16)
        
        # 매출금액 (역스케일 + 추세선)
        self._plot_with_trend(axes[0,0], sales_data['기준년월'], sales_data['매출금액'], 
                             'Sales Amount Trend (Inverted Scale)', 'Sales Amount', 'red', invert=True)
        
        # 매출건수 (역스케일 + 추세선)
        self._plot_with_trend(axes[0,1], sales_data['기준년월'], sales_data['매출건수'], 
                             'Sales Count Trend (Inverted Scale)', 'Sales Count', 'blue', invert=True)
        
        # 유니크고객수 (역스케일 + 추세선)
        self._plot_with_trend(axes[1,0], sales_data['기준년월'], sales_data['유니크고객수'], 
                             'Unique Customers Trend (Inverted Scale)', 'Unique Customers', 'green', invert=True)
        
        # 객단가 (역스케일 + 추세선)
        self._plot_with_trend(axes[1,1], sales_data['기준년월'], sales_data['객단가'], 
                             'Average Transaction Value Trend (Inverted Scale)', 'Avg Transaction Value', 'orange', invert=True)
        
        plt.tight_layout()
        
        # Base64 인코딩
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def _plot_with_trend(self, ax, x_data, y_data, title, ylabel, color, invert=False):
        """추세선이 포함된 플롯 생성"""
        # NaN 처리: 유효한 데이터만 필터링
        valid_mask = pd.notna(y_data) & (y_data != np.inf) & (y_data != -np.inf)
        x_data_clean = x_data[valid_mask]
        y_data_clean = y_data[valid_mask]
        
        if len(y_data_clean) == 0:
            # 데이터가 없으면 빈 차트
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title)
            return
        
        # 데이터 플롯
        ax.plot(x_data_clean, y_data_clean, marker='o', color=color, linewidth=2, markersize=4, label='Data')
        
        # 추세선 계산 및 그리기
        if len(y_data_clean) > 1:
            try:
                x_numeric = np.arange(len(y_data_clean))
                z = np.polyfit(x_numeric, y_data_clean, 1)
                p = np.poly1d(z)
                trend_line = p(x_numeric)
                ax.plot(x_data_clean, trend_line, '--', color=color, alpha=0.7, linewidth=2, label='Trend')
            except (np.linalg.LinAlgError, ValueError) as e:
                # 추세선 계산 실패 시 무시
                print(f"[WARN] Trend line calculation failed: {e}")
        
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        
        # y축 스케일을 0-100으로 고정 (유효한 데이터가 있을 때만)
        ax.set_ylim(0, 100)
        
        if invert:
            ax.invert_yaxis()
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _create_customer_trends_chart(self) -> str:
        """고객층별 시계열 트렌드 차트 생성"""
        sales_data = self.store_data.sort_values('기준년월')
        
        # 고객층 데이터 추출
        customer_columns = {
            '남20대이하': '남20대이하',
            '남30대': '남30대', 
            '남40대': '남40대',
            '남50대': '남50대',
            '남60대이상': '남60대이상',
            '여20대이하': '여20대이하',
            '여30대': '여30대',
            '여40대': '여40대',
            '여50대': '여50대',
            '여60대이상': '여60대이상'
        }
        
        # 상위 5개 고객층만 선택 (최신 데이터 기준)
        latest_data = self.store_data.iloc[-1]
        customer_ratios = {}
        for col, display_name in customer_columns.items():
            if pd.notna(latest_data[col]):
                customer_ratios[display_name] = latest_data[col]
        
        # 비율 순으로 정렬하여 상위 5개 선택
        top_customers = dict(sorted(customer_ratios.items(), key=lambda x: x[1], reverse=True)[:5])
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Customer Segment Trends (Top 5 Segments)', fontsize=16)
        
        colors = ['red', 'blue', 'green', 'orange', 'purple']
        
        for i, (customer_type, ratio) in enumerate(top_customers.items()):
            if i < 5:  # 최대 5개만 표시
                row = i // 3
                col = i % 3
                
                if row < 2 and col < 3:
                    customer_data = sales_data[customer_columns[customer_type]].dropna()
                    if len(customer_data) > 0:
                        self._plot_with_trend(axes[row, col], 
                                            sales_data.loc[customer_data.index, '기준년월'], 
                                            customer_data,
                                            f'{customer_type} Trend', 
                                            'Ratio (%)', 
                                            colors[i])
        
        # 빈 subplot 숨기기
        if len(top_customers) < 6:
            axes[1, 2].set_visible(False)
        
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def _create_new_returning_trends_chart(self) -> str:
        """신규/재방문 고객 트렌드 차트 생성"""
        sales_data = self.store_data.sort_values('기준년월')
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('New vs Returning Customer Trends', fontsize=16)
        
        # 신규고객 트렌드
        new_customer_data = sales_data['신규고객'].dropna()
        if len(new_customer_data) > 0:
            self._plot_with_trend(axes[0], 
                                sales_data.loc[new_customer_data.index, '기준년월'], 
                                new_customer_data,
                                'New Customers Trend', 
                                'Ratio (%)', 
                                'blue')
        else:
            axes[0].text(0.5, 0.5, 'No New Customer Data', ha='center', va='center', transform=axes[0].transAxes)
            axes[0].set_title('New Customers Trend (No Data)')
        
        # 재방문고객 트렌드
        returning_customer_data = sales_data['재방문고객'].dropna()
        if len(returning_customer_data) > 0:
            self._plot_with_trend(axes[1], 
                                sales_data.loc[returning_customer_data.index, '기준년월'], 
                                returning_customer_data,
                                'Returning Customers Trend', 
                                'Ratio (%)', 
                                'green')
        else:
            axes[1].text(0.5, 0.5, 'No Returning Customer Data', ha='center', va='center', transform=axes[1].transAxes)
            axes[1].set_title('Returning Customers Trend (No Data)')
        
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def _create_gender_pie_chart(self) -> str:
        """성별 파이차트 생성"""
            
        plt.figure(figsize=(8, 8))
        
        latest_data = self.store_data.iloc[-1]
        
        # NaN 처리: 컬럼이 있고 값이 유효한 경우만 합산
        male_cols = ['남20대이하', '남30대', '남40대', '남50대', '남60대이상']
        female_cols = ['여20대이하', '여30대', '여40대', '여50대', '여60대이상']
        
        male_ratio = sum([float(latest_data.get(col, 0) or 0) for col in male_cols if pd.notna(latest_data.get(col, 0))])
        female_ratio = sum([float(latest_data.get(col, 0) or 0) for col in female_cols if pd.notna(latest_data.get(col, 0))])
        
        # 0이면 데이터 없음 처리
        if male_ratio == 0 and female_ratio == 0:
            plt.text(0.5, 0.5, 'No Gender Data Available', ha='center', va='center')
            plt.axis('off')
        else:
            labels = ['Male', 'Female']
            sizes = [male_ratio, female_ratio]
            colors = ['lightblue', 'lightpink']
            
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title('Gender Distribution')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def _create_age_pie_chart(self) -> str:
        """연령대 파이차트 생성"""
            
        plt.figure(figsize=(8, 8))
        
        latest_data = self.store_data.iloc[-1]
        
        # NaN 처리: fillna(0)로 0으로 변환
        age_groups = {
            "20s and below": (latest_data.get('남20대이하', 0) or 0) + (latest_data.get('여20대이하', 0) or 0),
            "30s": (latest_data.get('남30대', 0) or 0) + (latest_data.get('여30대', 0) or 0),
            "40s": (latest_data.get('남40대', 0) or 0) + (latest_data.get('여40대', 0) or 0),
            "50s": (latest_data.get('남50대', 0) or 0) + (latest_data.get('여50대', 0) or 0),
            "60s and above": (latest_data.get('남60대이상', 0) or 0) + (latest_data.get('여60대이상', 0) or 0)
        }
        
        # NaN을 0으로 변환
        age_groups = {k: float(v) if pd.notna(v) else 0.0 for k, v in age_groups.items()}
        
        # 0이 아닌 값만 필터링
        age_groups = {k: v for k, v in age_groups.items() if v > 0}
        
        if not age_groups:
            # 데이터가 없으면 빈 차트
            plt.text(0.5, 0.5, 'No Age Data Available', ha='center', va='center')
            plt.axis('off')
        else:
            labels = list(age_groups.keys())
            sizes = list(age_groups.values())
            colors = ['lightcoral', 'lightskyblue', 'lightgreen', 'gold', 'lightgray']
            
            plt.pie(sizes, labels=labels, colors=colors[:len(labels)], autopct='%1.1f%%', startangle=90)
            plt.title('Age Group Distribution')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def _create_detailed_pie_chart(self) -> str:
        """세부 비율 파이차트 생성"""
            
        plt.figure(figsize=(10, 10))
        
        latest_data = self.store_data.iloc[-1]
        detailed_ratios = {}
        
        for col in ['남20대이하', '남30대', '남40대', '남50대', '남60대이상', 
                   '여20대이하', '여30대', '여40대', '여50대', '여60대이상']:
            if col in latest_data.index and pd.notna(latest_data[col]):
                val = float(latest_data[col])
                if val > 0:  # 0보다 큰 값만 추가
                    detailed_ratios[col] = val
        
        if not detailed_ratios:
            # 데이터가 없으면 빈 차트
            plt.text(0.5, 0.5, 'No Detailed Data Available', ha='center', va='center')
            plt.axis('off')
        else:
            # 비율 순으로 정렬
            detailed_ratios = dict(sorted(detailed_ratios.items(), key=lambda x: x[1], reverse=True))
            
            labels = list(detailed_ratios.keys())
            sizes = list(detailed_ratios.values())
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
            
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title('Detailed Customer Distribution (Top to Bottom)')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def _create_ranking_trend_chart(self) -> str:
        """순위 트렌드 차트 생성 (추세선 포함)"""
            
        fig, ax = plt.subplots(figsize=(12, 6))
        
        sales_data = self.store_data.sort_values('기준년월')
        
        # 업종 내 순위 (추세선 포함)
        self._plot_with_trend(ax, sales_data['기준년월'], sales_data['동종매출순위%'], 
                             'Sales Ranking Trends (Inverted Scale)', 'Rank (%)', 'blue', invert=True)
        
        # 상권 내 순위 (추세선 포함)
        ax.plot(sales_data['기준년월'], sales_data['동일상권매출순위%'], marker='s', color='red', 
                linewidth=2, markersize=4, label='Commercial Area Rank')
        
        # 상권 내 순위 추세선
        if len(sales_data) > 1:
            x_numeric = np.arange(len(sales_data))
            z = np.polyfit(x_numeric, sales_data['동일상권매출순위%'], 1)
            p = np.poly1d(z)
            trend_line = p(x_numeric)
            ax.plot(sales_data['기준년월'], trend_line, '--', color='red', alpha=0.7, linewidth=2, 
                   label='Commercial Area Trend')
        
        ax.set_xlabel('Month')
        ax.legend()
        ax.invert_yaxis()  # 순위는 낮을수록 좋으므로 역스케일
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def _calculate_trend(self, data: pd.Series) -> str:
        """트렌드 계산"""
        if len(data) < 2:
            return "데이터 부족"
        
        # 선형 회귀로 트렌드 계산
        x = np.arange(len(data))
        y = data.values
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.1:
            return "상승 추세"
        elif slope < -0.1:
            return "하락 추세"
        else:
            return "안정 추세"
    
    def _calculate_stability(self, data: pd.Series) -> str:
        """안정성 계산"""
        if len(data) < 2:
            return "데이터 부족"
        
        cv = data.std() / data.mean() if data.mean() != 0 else float('inf')
        
        if cv < 0.1:
            return "매우 안정적"
        elif cv < 0.2:
            return "안정적"
        elif cv < 0.3:
            return "보통"
        else:
            return "불안정"
    
    def _calculate_rank_trend(self, data: pd.Series) -> str:
        """순위 트렌드 계산 (낮을수록 좋음)"""
        if len(data) < 2:
            return "데이터 부족"
        
        x = np.arange(len(data))
        y = data.values
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.1:
            return "순위 하락 (악화)"
        elif slope < -0.1:
            return "순위 상승 (개선)"
        else:
            return "순위 안정"
    
    def _get_cancellation_recommendation(self, cancellation_data: pd.Series) -> str:
        """취소율 개선 권고사항"""
        if cancellation_data.mean() > 3:
            return "취소율이 높습니다. 주문 확인 프로세스 개선, 배달 시간 단축, 고객 서비스 강화를 권장합니다."
        elif cancellation_data.mean() > 2:
            return "취소율이 보통 수준입니다. 지속적인 모니터링과 개선이 필요합니다."
        else:
            return "취소율이 양호합니다. 현재 수준을 유지하세요."
    
    def _analyze_customer_trend(self, column: str) -> str:
        """고객 트렌드 분석"""
        if column not in self.store_data.columns:
            return "데이터 없음"
        
        trend_data = self.store_data[column].dropna()
        if len(trend_data) < 2:
            return "데이터 부족"
        
        return self._calculate_trend(trend_data)
    
    async def _generate_summary(self) -> Dict[str, Any]:
        """분석 결과 종합 요약"""
        store_overview = await self._analyze_store_overview()
        sales_analysis = await self._analyze_sales()
        customer_analysis = await self._analyze_customers()
        commercial_analysis = await self._analyze_commercial_area()
        industry_analysis = await self._analyze_industry()
        
        # 핵심 인사이트 추출
        key_insights = []
        
        # 매출 트렌드
        sales_trend = sales_analysis['sales_analysis']['sales_amount']['trend']
        key_insights.append(f"매출 트렌드: {sales_trend}")
        
        # 순위 분석
        industry_rank_trend = sales_analysis['ranking_analysis']['industry_rank']['trend']
        key_insights.append(f"업종 내 순위: {industry_rank_trend}")
        
        # 고객층 특성
        gender_ratio = customer_analysis['gender_analysis']
        dominant_gender = "남성" if gender_ratio['male_ratio'] > gender_ratio['female_ratio'] else "여성"
        key_insights.append(f"주 고객층: {dominant_gender} 고객 중심")
        
        # 상권/업종 건강도
        if commercial_analysis.get('analysis_available'):
            area_health = commercial_analysis['termination_analysis']['area_health']
            key_insights.append(f"상권 건강도: {area_health}")
        
        if industry_analysis.get('analysis_available'):
            industry_health = industry_analysis['termination_analysis']['industry_health']
            key_insights.append(f"업종 건강도: {industry_health}")
        
        # 주요 문제점
        problems = []
        if sales_analysis['cancellation_analysis']['average_grade'] > 3:
            problems.append("높은 취소율")
        
        if sales_analysis['ranking_analysis']['industry_rank']['average'] > 70:
            problems.append("업종 내 낮은 순위")
        
        if commercial_analysis.get('analysis_available') and commercial_analysis['termination_analysis']['termination_ratio'] > 20:
            problems.append("상권 위험 상황")
        
        if industry_analysis.get('analysis_available') and industry_analysis['termination_analysis']['termination_ratio'] > 20:
            problems.append("업종 위험 상황")
        
        # 구체적인 개선 권고사항 생성
        recommendations = self._generate_detailed_recommendations(
            store_overview, sales_analysis, customer_analysis, 
            commercial_analysis, industry_analysis
        )
        
        return {
            "store_summary": store_overview,
            "key_insights": key_insights,
            "main_problems": problems,
            "recommendations": recommendations,
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _generate_detailed_recommendations(self, store_overview, sales_analysis, customer_analysis, 
                                         commercial_analysis, industry_analysis) -> List[Dict[str, Any]]:
        """구체적이고 실행 가능한 권고사항 생성"""
        recommendations = []
        
        # 1. 매출 개선 권고사항
        if sales_analysis['sales_analysis']['sales_amount']['trend'] == "하락 추세":
            # 주 고객층 기반 구체적 마케팅 전략
            dominant_customers = self._get_dominant_customer_segments(customer_analysis)
            
            for customer_type, ratio in list(dominant_customers.items())[:2]:  # 상위 2개 고객층
                if "남20대이하" in customer_type:
                    recommendations.append({
                        "category": "마케팅 전략",
                        "priority": "높음",
                        "target": customer_type,
                        "action": "SNS 마케팅 강화",
                        "specific_actions": [
                            "인스타그램/틱톡 이벤트 진행",
                            "20대 인플루언서 협업",
                            "점심시간 할인 프로모션 (11:30-14:00)"
                        ],
                        "expected_impact": "주 고객층 유지 및 신규 고객 확보"
                    })
                elif "남30대" in customer_type:
                    recommendations.append({
                        "category": "마케팅 전략",
                        "priority": "높음",
                        "target": customer_type,
                        "action": "직장인 타겟 마케팅",
                        "specific_actions": [
                            "점심 배달 서비스 강화",
                            "회식 메뉴 패키지 출시",
                            "카카오톡 채널 운영"
                        ],
                        "expected_impact": "직장인 고객층 확대"
                    })
                elif "여성" in customer_type:
                    recommendations.append({
                        "category": "마케팅 전략",
                        "priority": "중간",
                        "target": customer_type,
                        "action": "여성 고객 확대 전략",
                        "specific_actions": [
                            "건강한 메뉴 라인 추가",
                            "디저트 메뉴 개발",
                            "인테리어 개선 (인스타 감성)"
                        ],
                        "expected_impact": "여성 고객 비율 증가"
                    })
        
        # 2. 취소율 개선 권고사항
        if sales_analysis['cancellation_analysis']['average_grade'] > 2:
            recommendations.append({
                "category": "운영 개선",
                "priority": "높음",
                "target": "전체 고객",
                "action": "취소율 감소 프로그램",
                "specific_actions": [
                    "주문 확인 시스템 개선 (2단계 확인)",
                    "예상 대기시간 정확한 안내",
                    "취소 시 포인트 적립 혜택 제공",
                    "배달 시간 단축 (30분 이내 목표)"
                ],
                "expected_impact": f"취소율 {sales_analysis['cancellation_analysis']['average_grade']:.1f} → 2.0 이하"
            })
        
        # 3. 순위 개선 권고사항
        if sales_analysis['ranking_analysis']['industry_rank']['average'] > 50:
            recommendations.append({
                "category": "경쟁력 강화",
                "priority": "높음",
                "target": "업종 내 경쟁력",
                "action": "차별화 전략 수립",
                "specific_actions": [
                    "시그니처 메뉴 개발",
                    "고객 리뷰 관리 시스템 구축",
                    "로열티 프로그램 도입",
                    "경쟁사 대비 가격 경쟁력 분석"
                ],
                "expected_impact": f"업종 내 순위 {sales_analysis['ranking_analysis']['industry_rank']['average']:.1f}% → 30% 이하"
            })
        
        # 4. 상권 대응 권고사항
        if commercial_analysis.get('analysis_available'):
            if commercial_analysis['termination_analysis']['area_health'] == "위험한 상권":
                recommendations.append({
                    "category": "상권 대응",
                    "priority": "높음",
                    "target": "상권 변화 대응",
                    "action": "상권 위험 대응 전략",
                    "specific_actions": [
                        "배달 서비스 비중 확대",
                        "온라인 마케팅 집중 투자",
                        "이전 후보지 사전 조사",
                        "고객 데이터베이스 구축"
                    ],
                    "expected_impact": "상권 변화에 대한 대응력 강화"
                })
        
        # 5. 업종 대응 권고사항
        if industry_analysis.get('analysis_available'):
            if industry_analysis['termination_analysis']['industry_health'] == "위험한 업종":
                recommendations.append({
                    "category": "업종 대응",
                    "priority": "높음",
                    "target": "업종 변화 대응",
                    "action": "업종 위험 대응 전략",
                    "specific_actions": [
                        "다양한 메뉴 라인 확장",
                        "다른 업종 진출 검토",
                        "고객층 다변화 전략",
                        "신규 사업 모델 개발"
                    ],
                    "expected_impact": "업종 변화에 대한 대응력 강화"
                })
        
        # 6. 배달 서비스 권고사항
        if industry_analysis.get('analysis_available') and industry_analysis['delivery_analysis']['average_delivery_ratio']:
            delivery_ratio = industry_analysis['delivery_analysis']['average_delivery_ratio']
            if delivery_ratio < 30:  # 업종 평균 대비 낮은 경우
                recommendations.append({
                    "category": "배달 서비스",
                    "priority": "중간",
                    "target": "배달 매출 확대",
                    "action": "배달 서비스 강화",
                    "specific_actions": [
                        "배달 전용 메뉴 개발",
                        "배달 앱 최적화",
                        "배달 포장재 개선",
                        "배달료 할인 이벤트"
                    ],
                    "expected_impact": f"배달 매출 비율 {delivery_ratio:.1f}% → 40% 이상"
                })
        
        return recommendations
    
    def _get_dominant_customer_segments(self, customer_analysis) -> Dict[str, float]:
        """주요 고객층 세그먼트 추출"""
        detailed_ratios = customer_analysis['detailed_ratios']
        return dict(sorted(detailed_ratios.items(), key=lambda x: x[1], reverse=True))
    
    async def _perform_self_evaluation(self, analysis_result: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """자가 평가 수행"""
        # 분석 완성도 평가
        completeness_score = 0.0
        total_sections = 5  # 점포개요, 매출분석, 고객분석, 시각화, 요약
        
        if analysis_result.get('store_overview'):
            completeness_score += 0.2
        if analysis_result.get('sales_analysis'):
            completeness_score += 0.2
        if analysis_result.get('customer_analysis'):
            completeness_score += 0.2
        if analysis_result.get('visualizations'):
            completeness_score += 0.2
        if analysis_result.get('summary'):
            completeness_score += 0.2
        
        # 정확성 평가 (데이터 활용도)
        accuracy_score = 0.9 if self.store_data is not None and len(self.store_data) > 0 else 0.5
        
        # 관련성 평가
        relevance_score = 0.9 if "매장" in user_query or "점포" in user_query else 0.7
        
        # 실행가능성 평가
        actionability_score = 0.8 if analysis_result.get('summary', {}).get('recommendations') else 0.6
        
        # 종합 품질 점수
        quality_score = (completeness_score * 0.3 + accuracy_score * 0.3 + 
                        relevance_score * 0.2 + actionability_score * 0.2)
        
        feedback = f"매장 분석이 완료되었습니다. 완성도: {completeness_score:.1f}, 정확성: {accuracy_score:.1f}, 관련성: {relevance_score:.1f}, 실행가능성: {actionability_score:.1f}"
        
        return {
            "quality_score": quality_score,
            "feedback": feedback,
            "completeness": completeness_score,
            "accuracy": accuracy_score,
            "relevance": relevance_score,
            "actionability": actionability_score
        }
    
