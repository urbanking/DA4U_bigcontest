"""
Integrated Analysis Pipeline - Store Agent → Marketing Agent Direct Connection
Implemented as regular Python functions, not Agent format
"""
import asyncio
import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent

# Add paths
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "agents_new"))

# Global environment detection
def is_cloud_environment() -> bool:
    """클라우드 환경 감지 (Streamlit Cloud, etc.)"""
    return (
        os.path.exists('/mount/src') or 
        os.path.exists('/home/appuser') or
        os.getenv('STREAMLIT_SHARING_MODE') is not None or
        os.getenv('HOME') == '/home/appuser' or
        'streamlit' in sys.executable.lower() or
        os.path.exists('/app')  # Heroku, Cloud Run 등
    )

IS_CLOUD = is_cloud_environment()
if IS_CLOUD:
    print("[INFO] 클라우드 환경 감지됨 - 일부 Agent 비활성화됨")
else:
    print("[INFO] 로컬 환경에서 실행 중")

# Add remaining paths
sys.path.insert(0, str(project_root / "agents_new" / "store_agent" / "report_builder"))
sys.path.insert(0, str(project_root / "agents_new" / "panorama_img_anal"))
sys.path.insert(0, str(project_root / "agents_new" / "new_product_agent"))
sys.path.insert(0, str(project_root / "open_sdk"))  # For spatial_matcher module

# Langfuse tracing 추가 (올바른 방식)
try:
    from langfuse import observe
    from langfuse.openai import openai as langfuse_openai
    LANGFUSE_AVAILABLE = True
    print("[OK] Langfuse initialized in run_analysis")
except ImportError:
    print("[WARN] Langfuse not available in run_analysis - tracing disabled")
    LANGFUSE_AVAILABLE = False
    langfuse_openai = None

# matplotlib 활성화 및 폰트 경고 완전 억제
import warnings
import logging

# 환경변수로 matplotlib 설정
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'
os.environ['MPLBACKEND'] = 'Agg'

# 모든 경고 완전 차단
warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.ERROR)
logging.getLogger().setLevel(logging.ERROR)

import matplotlib
matplotlib.use('Agg')  # GUI 백엔드 비활성화

# matplotlib 로거 완전 차단
for logger_name in ['matplotlib', 'matplotlib.font_manager', 'matplotlib.pyplot', 'PIL']:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    logging.getLogger(logger_name).propagate = False

import matplotlib.pyplot as plt
import platform

# 한글 폰트 설정 (경고 없이)
system = platform.system()
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        if system == "Windows":
            plt.rcParams['font.family'] = 'Malgun Gothic'
        elif system == "Darwin":
            plt.rcParams['font.family'] = 'AppleGothic'
        else:
            # Linux - DejaVu Sans 사용 (NanumGothic 검색 안 함)
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
        
        matplotlib.rcParams['axes.unicode_minus'] = False
except:
    pass

print("[OK] Matplotlib loaded in run_analysis")


async def run_store_analysis(store_code: str) -> Dict[str, Any]:
    """Step 1: Execute Store Agent Analysis"""
    print("\n" + "="*60)
    print("[Step 1] Store Agent Analysis")
    print("="*60)
    
    try:
        # Import module directly
        import importlib.util
        module_path = project_root / "agents_new" / "store_agent" / "report_builder" / "store_agent_module.py"
        
        spec = importlib.util.spec_from_file_location("store_agent_module", module_path)
        store_module = importlib.util.module_from_spec(spec)
        sys.modules["store_agent_module"] = store_module
        spec.loader.exec_module(store_module)
        
        StoreAgentModule = store_module.StoreAgentModule
        StoreAgentState = store_module.StoreAgentState
        
        # Initialize Store Agent
        agent = StoreAgentModule()
        
        # Prepare state - Create as dict (TypedDict is compatible)
        state = {
            "user_query": f"{store_code} store analysis",
            "user_id": "pipeline_user",
            "session_id": f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "context": {},
            "store_analysis": None,
            "error": None
        }
        
        # Execute analysis
        print(f"Starting analysis: {store_code}")
        result = await agent.execute_analysis_with_self_evaluation(state)
        
        if result["error"]:
            print(f"[ERROR] Store Agent failed: {result['error']}")
            return None
        
        analysis = result["store_analysis"]
        print(f"[OK] Store Agent completed - Quality: {analysis['evaluation']['quality_score']:.2%}")
        print(f"   Report: {analysis['output_file_path']}")
        print(f"   Charts: {len(analysis['json_output']['visualizations']['chart_files'])} generated")
        
        # Extract address
        address = analysis['json_output']['store_overview']['address']
        analysis['address'] = address
        print(f"   Address: {address}")
        
        return analysis
        
    except Exception as e:
        print(f"[ERROR] Store Agent error: {e}")
        import traceback
        traceback.print_exc()
        return None


def _get_address_from_store_code(store_code: str) -> str:
    """Extract address from store code"""
    try:
        import pandas as pd
        csv_path = project_root / "agents_new" / "store_agent" / "store_data" / "final_merged_data.csv"
        
        if not csv_path.exists():
            return None
        
        # Try multiple encodings
        encodings = ['cp949', 'utf-8', 'euc-kr', 'latin1']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding, low_memory=False)
                print(f"[INFO] CSV loaded successfully: {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print(f"[ERROR] All encoding attempts failed")
            return None
        
        # Code column name
        code_col = '코드'
        
        # Find matching row
        matched = df[df[code_col] == store_code]
        
        if matched.empty:
            print(f"[ERROR] Store code {store_code} not found")
            return None
        
        # Address column
        address_col = '기준면적'
        if address_col in df.columns:
            address = matched[address_col].iloc[0]
            if pd.isna(address) or not address:
                print(f"[ERROR] Address is empty for store code {store_code}")
                return None
            print(f"[OK] Address extracted successfully: {address}")
            return str(address)
        
        print(f"[ERROR] Address column '{address_col}' not found")
        return None
        
    except Exception as e:
        print(f"[WARN] Address extraction failed: {e}")
        return None


@observe()
def _extract_dong_from_address(address: str) -> str:
    """Extract dong (administrative district) from address using Gemini AI"""
    import re
    
    # 1. Try direct extraction from address
    match = re.search(r'([가-힣]+[0-9]?가?[0-9]?동)\s', address)
    if match:
        dong_candidate = match.group(1)
        # Verify it's an actual dong, not a gu name
        if not dong_candidate.endswith("구동"):
            print(f"[INFO] Extracted directly from address: {dong_candidate}")
            return dong_candidate
    
    # 2. Request Gemini AI to determine administrative dong
    try:
        from agents_new.utils.gemini_client import get_gemini_client
        gemini = get_gemini_client()
        
        # Simple prompt
        prompt = f"""Address: {address}

Seoul Seongdong-gu Administrative Dongs: Geumho1-ga-dong, Geumho2.3-ga-dong, Geumho4-ga-dong, Majang-dong, Sageun-dong, Seongsu1-ga1-dong, Seongsu1-ga2-dong, Seongsu2-ga1-dong, Seongsu2-ga3-dong, Songjeong-dong, Oksu-dong, Wangsimni2-dong, Wangsimni-doseon-dong, Yongdap-dong, Eungbong-dong, Haengdang1-dong, Haengdang2-dong

Which dong is this address in? Answer with dong name only."""
        
        response = gemini.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=30
        ).strip()
        
        print(f"[INFO] Gemini response: {response}")
        
        # Find dong name in response
        available_dongs = [
            "금호1가동", "금호2.3가동", "금호4가동",
            "마장동", "사근동",
            "성수1가1동", "성수1가2동", "성수2가1동", "성수2가3동",
            "송정동", "옥수동",
            "왕십리2동", "왕십리도선동",
            "용답동", "응봉동",
            "행당1동", "행당2동"
        ]
        
        for dong in available_dongs:
            if dong in response:
                print(f"[INFO] Gemini determined: {dong}")
                return dong
        
    except Exception as e:
        print(f"[WARN] Gemini dong determination error: {e}")
    
    # 3. Default fallback
    print(f"[WARN] Administrative dong determination failed, using default: Wangsimni2-dong")
    return "왕십리2동"


def _find_nearest_marketplace(address: str) -> str:
    """가장 가까운 상권 판단 (Gemini 사용)"""
    try:
        from agents_new.utils.gemini_client import get_gemini_client
        gemini = get_gemini_client()
        
        marketplace_dir = project_root / "agents_new" / "data outputs" / "상권분석서비스_결과"
        if not marketplace_dir.exists():
            return None
        
        json_files = list(marketplace_dir.glob("*.json"))
        if not json_files:
            return None
        
        file_names = [f.stem for f in json_files]
        
        prompt = f"""주소: {address}

위 주소와 가장 가까운 상권을 선택하세요.

사용 가능한 상권: {', '.join(file_names[:20])}

파일명만 답하세요 (예: 왕십리역3번)"""
        
        response = gemini.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        # 응답에서 파일명 찾기
        for name in file_names:
            if name in response:
                matched_file = [f for f in json_files if f.stem == name][0]
                return str(matched_file)
        
    except Exception as e:
        print(f"[WARN] 상권 판단 실패: {e}")
    
    return None


def convert_absolute_to_relative_path(absolute_path: str) -> str:
    """절대 경로를 상대 경로로 변환"""
    if not absolute_path:
        return absolute_path
    
    # 프로젝트 루트 기준으로 상대 경로 계산
    project_root = Path(__file__).parent.parent
    
    try:
        abs_path = Path(absolute_path)
        if abs_path.is_absolute():
            # 프로젝트 루트를 기준으로 상대 경로 계산
            relative_path = abs_path.relative_to(project_root)
            return str(relative_path).replace('\\', '/')  # Windows 경로 구분자 통일
        else:
            return absolute_path
    except ValueError:
        # 프로젝트 루트 밖의 경로인 경우 원본 반환
        return absolute_path


async def run_mobility_analysis(address: str, dong: str = None) -> Dict[str, Any]:
    """Step 4: Mobility Analysis (Mandatory) - Copy JSON + PNG from data outputs"""
    print("\n" + "="*60)
    print("[Step 4] Mobility Analysis")
    print("="*60)
    
    try:
        import shutil
        from datetime import datetime
        
        # Use dong (if already extracted) or extract from address
        if not dong:
            dong = _extract_dong_from_address(address)
        
        if not dong:
            print("[WARN] Dong name not found, skipping Mobility analysis")
            return {"status": "skipped", "reason": "No dong name"}
        
        print(f"Dong: {dong}")
        
        # Find dong folder in data outputs
        mobility_base_dir = project_root / "agents_new" / "data outputs" / "이동분석_결과"
        if not mobility_base_dir.exists():
            print("[WARN] Mobility data folder not found")
            return {"status": "skipped", "reason": "Data folder not found"}
        
        # Find dong folder
        dong_folder = mobility_base_dir / dong
        if not dong_folder.exists():
            print(f"[WARN] {dong} folder not found")
            return {"status": "skipped", "reason": f"{dong} folder not found"}
        
        print(f"[OK] {dong} folder found")
        
        # Set output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent / "output" / f"mobility_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy JSON file
        json_files = list(dong_folder.glob("results_*.json"))
        if json_files:
            src_json = json_files[0]
            dest_json = output_dir / "mobility_data.json"
            shutil.copy2(src_json, dest_json)
            print(f"   [OK] JSON copied: {src_json.name}")
        else:
            print(f"   [WARN] No JSON file found")
            dest_json = None
        
        # Copy PNG files (9 charts)
        png_files = list(dong_folder.glob("*.png"))
        copied_charts = []
        
        for png_file in png_files:
            dest_png = output_dir / png_file.name
            shutil.copy2(png_file, dest_png)
            copied_charts.append(str(dest_png))
        
        print(f"[OK] Mobility analysis completed")
        print(f"   Charts copied: {len(copied_charts)}")
        print(f"   Saved to: {output_dir}")
        
        # Load JSON data (if available)
        data = None
        if dest_json and dest_json.exists():
            with open(dest_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        return {
            "status": "success",
            "dong": dong,
            "charts": copied_charts,
            "output_dir": str(output_dir),
            "data": data
        }
        
    except Exception as e:
        print(f"[ERROR] Mobility analysis error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}


async def run_panorama_analysis(address: str) -> Dict[str, Any]:
    """Step 5: Panorama Analysis (Mandatory)"""
    print("\n" + "="*60)
    print("[Step 5] Panorama Analysis")
    print("="*60)
    
    # Skip in cloud environment due to network restrictions
    if IS_CLOUD:
        print(f"[SKIP] 클라우드 환경 - Panorama Analysis 비활성화 (외부 API 접근 제한)")
        return {"status": "skipped", "reason": "Cloud environment - network restrictions"}
    
    try:
        import importlib.util
        import shutil
        from datetime import datetime
        
        spec = importlib.util.spec_from_file_location(
            "analyze_area_by_address",
            project_root / "agents_new" / "panorama_img_anal" / "analyze_area_by_address.py"
        )
        panorama_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(panorama_module)
        
        print(f"Address: {address}")
        print("Analyzing panorama images... (3-5 minutes)")
        
        # Execute Panorama analysis (save to default path)
        result = panorama_module.analyze_area_by_address(
            address=address,
            buffer_meters=300,
            max_images=5,
            create_map=True,
            data_csv_path=str(project_root / "agents_new" / "panorama_img_anal" / "Step1_Result_final (1).csv"),
            image_folder=str(project_root / "agents_new" / "panorama_img_anal" / "downloaded_img")
        )
        
        if result.get("error"):
            print(f"[ERROR] Panorama analysis failed: {result['error']}")
            return {"status": "failed", "error": result["error"]}
        
        # Copy results to open_sdk/output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent / "output" / f"panorama_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        original_folder = Path(result.get('output_folder', ''))
        if original_folder.exists():
            # Generate comprehensive analysis summary
            synthesis = result.get("synthesis", {})
            summary = {
                "area_characteristics": synthesis.get('area_summary', {}).get('dominant_zone_type', 'N/A'),
                "commercial_type": synthesis.get('area_summary', {}).get('overall_commercial_type', 'N/A'),
                "scores": synthesis.get('comprehensive_scores', {}),
                "strengths": synthesis.get('strengths', []),
                "weaknesses": synthesis.get('weaknesses', []),
                "recommended_industries": synthesis.get('recommended_business_types', []),
                "expert_opinion": synthesis.get('expert_opinion', '')
            }
            
            # Load JSON file and add summary
            json_file = original_folder / "analysis_result.json"
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    full_data = json.load(f)
                
                # Add summary
                full_data['summary'] = summary
                
                # Save to new file
                dest_json = output_dir / "analysis_result.json"
                with open(dest_json, 'w', encoding='utf-8') as f:
                    json.dump(full_data, f, ensure_ascii=False, indent=2)
                
                print(f"   [OK] Comprehensive summary added")
            
            # Copy HTML map
            html_file = original_folder / "analysis_map.html"
            if html_file.exists():
                shutil.copy2(html_file, output_dir / "analysis_map.html")
            
            # Copy images folder
            images_folder = original_folder / "images"
            if images_folder.exists():
                dest_images = output_dir / "images"
                shutil.copytree(images_folder, dest_images, dirs_exist_ok=True)
            
            print(f"   Results copied: {output_dir}")
        
        synthesis = result.get("synthesis", {})
        print(f"[OK] Panorama analysis completed")
        print(f"   Area type: {synthesis.get('area_summary', {}).get('dominant_zone_type', 'N/A')}")
        print(f"   Commercial atmosphere: {synthesis.get('comprehensive_scores', {}).get('commercial_atmosphere', 'N/A')}/10")
        print(f"   Saved to: {output_dir}")
        
        # Add copied path to result
        result['copied_output_folder'] = str(output_dir)
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Panorama analysis error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}


def get_marketplace_json(address: str, spatial_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """Step 6: Marketplace Analysis (Mandatory) - Using spatial_matcher result"""
    print("\n" + "="*60)
    print("[Step 6] Marketplace Analysis (Spatial Matcher Based)")
    print("="*60)
    
    try:
        import shutil
        from datetime import datetime
        
        # Marketplace analysis results directory
        marketplace_dir = project_root / "agents_new" / "data outputs" / "상권분석서비스_결과"
        
        if not marketplace_dir.exists():
            print(f"[ERROR] Marketplace directory not found")
            return {"status": "no_directory"}
        
        # JSON file list
        json_files = list(marketplace_dir.glob("*.json"))
        print(f"Total marketplace JSON files: {len(json_files)}")
        
        if not json_files:
            print("[ERROR] No JSON files found")
            return {"status": "no_files"}
        
        # Use spatial_matcher result if available
        best_match = None
        if spatial_info and spatial_info.get("marketplace") and spatial_info["marketplace"].get("상권명"):
            marketplace_name = spatial_info["marketplace"]["상권명"]
            print(f"[INFO] Using spatial_matcher result: {marketplace_name}")
            
            # Find matching JSON file by marketplace name
            for json_file in json_files:
                if marketplace_name in json_file.stem:
                    best_match = json_file
                    print(f"[OK] Found matching file: {best_match.name}")
                    break
        
        # Fallback to keyword matching if spatial_matcher result not available
        if not best_match:
            print("[INFO] Spatial matcher result not available, using keyword matching...")
            import re
            
            # Extract keywords from address
            keywords = []
            
            # Extract station names (highest priority)
            station_matches = re.findall(r'([가-힣]+역)', address)
            keywords.extend(station_matches)
            
            # Road name based keywords
            if "왕십리" in address:
                keywords.extend(["왕십리역", "상왕십리역", "왕십리"])
            if "성수" in address or "서울숲" in address:
                keywords.extend(["성수역", "서울숲역", "뚝섬역"])
            if "금호" in address:
                keywords.extend(["금호역", "신금호역"])
            if "옥수" in address:
                keywords.append("옥수역")
            if "행당" in address or "한양대" in address:
                keywords.extend(["행당역", "한양대역"])
            if "마장" in address:
                keywords.append("마장역")
            if "답십리" in address:
                keywords.append("답십리역")
            
            keywords = list(set(keywords))
            print(f"Search keywords: {keywords}")
            
            # Keyword-based scoring
            best_score = 0
            
            for json_file in json_files:
                filename = json_file.stem
                score = 0
                
                for keyword in keywords:
                    if keyword in filename:
                        # Higher score for exact station name match
                        if keyword.endswith("역"):
                            score += len(keyword) * 5
                        else:
                            score += len(keyword) * 2
                
                if score > best_score:
                    best_score = score
                    best_match = json_file
            
            if best_match and best_score > 0:
                print(f"[OK] Keyword matching successful: {best_match.name} (score: {best_score})")
            else:
                # Use first file if no match found
                print(f"[WARN] No keyword match found, using default file")
                best_match = json_files[0]
        
        print(f"[OK] Selected marketplace: {best_match.name}")
        
        # Load JSON data
        with open(best_match, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        if "상권명" in json_data:
            print(f"   Marketplace name: {json_data['상권명']}")
        
        # Copy to output folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent / "output" / f"marketplace_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        dest_file = output_dir / "marketplace_data.json"
        shutil.copy2(best_match, dest_file)
        print(f"   Saved: marketplace_data.json")
        
        return {
            "status": "success", 
            "data": json_data, 
            "file": best_match.name,
            "output_dir": str(output_dir)
        }
            
    except Exception as e:
        print(f"[ERROR] Marketplace analysis error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}


def save_results(store_code: str, store_analysis: Dict[str, Any], 
                mobility_result: Dict[str, Any] = None,
                panorama_result: Dict[str, Any] = None,
                marketplace_result: Dict[str, Any] = None,
                spatial_info: Dict[str, Any] = None) -> str:
    """Step 8: Save results to open_sdk/output"""
    print("\n" + "="*60)
    print("[Step 8] Saving Results")
    print("="*60)
    
    try:
        import shutil
        
        # 출력 폴더 생성
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 통합 결과 폴더 생성
        result_dir = output_dir / f"analysis_{store_code}_{timestamp}"
        result_dir.mkdir(exist_ok=True)
        
        # 통합 결과 JSON
        integrated_result = {
            "metadata": {
                "store_code": store_code,
                "analysis_timestamp": timestamp,
                "pipeline_version": "1.0"
            },
            "store_analysis": store_analysis["json_output"] if store_analysis else None,
            "mobility_analysis": mobility_result.get("data") if mobility_result and mobility_result.get("data") else None,
            "panorama_analysis": panorama_result.get("synthesis") if panorama_result and panorama_result.get("synthesis") else None,
            "marketplace_analysis": marketplace_result.get("data") if marketplace_result and marketplace_result.get("data") else None
        }
        
        # 종합 분석 JSON 생성
        comprehensive_analysis = {
            "metadata": {
                "store_code": store_code,
                "analysis_timestamp": timestamp,
                "analysis_type": "comprehensive_analysis"
            },
            "spatial_analysis": {
                "address": spatial_info.get("address") if spatial_info else None,
                "coordinates": spatial_info.get("coordinates") if spatial_info else None,
                "administrative_dong": spatial_info.get("dong") if spatial_info else None,
                "marketplace": spatial_info.get("marketplace") if spatial_info else None
            },
            "store_summary": {
                "store_name": store_analysis["json_output"]["store_overview"]["name"] if store_analysis and store_analysis.get("json_output") else None,
                "industry": store_analysis["json_output"]["store_overview"]["industry"] if store_analysis and store_analysis.get("json_output") else None,
                "commercial_area": store_analysis["json_output"]["store_overview"]["commercial_area"] if store_analysis and store_analysis.get("json_output") else None,
                "quality_score": store_analysis["json_output"]["evaluation"]["quality_score"] if store_analysis and store_analysis.get("json_output") else None
            },
            "panorama_summary": {
                "area_characteristics": panorama_result.get("synthesis", {}).get("area_summary", {}).get("overall_character") if panorama_result else None,
                "marketplace_type": panorama_result.get("synthesis", {}).get("area_summary", {}).get("primary_commercial_type") if panorama_result else None,
                "scores": panorama_result.get("synthesis", {}).get("comprehensive_scores") if panorama_result else None,
                "strengths": panorama_result.get("synthesis", {}).get("detailed_assessment", {}).get("strengths") if panorama_result else None,
                "weaknesses": panorama_result.get("synthesis", {}).get("detailed_assessment", {}).get("weaknesses") if panorama_result else None,
                "recommended_industries": panorama_result.get("synthesis", {}).get("detailed_assessment", {}).get("recommended_industries") if panorama_result else None,
                "expert_opinion": panorama_result.get("synthesis", {}).get("detailed_assessment", {}).get("expert_opinion") if panorama_result else None
            },
            "marketplace_summary": {
                "marketplace_name": marketplace_result.get("data", {}).get("상권명") if marketplace_result else None,
                "store_count": marketplace_result.get("data", {}).get("상권_점포수") if marketplace_result else None,
                "sales_volume": marketplace_result.get("data", {}).get("상권_매출액") if marketplace_result else None
            },
            "mobility_summary": {
                "analysis_period": mobility_result.get("data", {}).get("분석_기간") if mobility_result else None,
                "total_charts": len(mobility_result.get("chart_files", [])) if mobility_result else 0
            }
        }
        
        # Save JSON
        output_file = result_dir / "analysis_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(integrated_result, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] Integrated results saved: {output_file.name}")
        
        # Save comprehensive analysis JSON
        comprehensive_file = result_dir / "comprehensive_analysis.json"
        with open(comprehensive_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_analysis, f, ensure_ascii=False, indent=2)
        print(f"[OK] Comprehensive analysis saved: {comprehensive_file.name}")
        
        # Copy Store analysis original file
        if store_analysis and "output_file_path" in store_analysis:
            original_report = Path(store_analysis["output_file_path"])
            if original_report.exists():
                dest_report = result_dir / "store_analysis_report.json"
                shutil.copy2(original_report, dest_report)
                print(f"[OK] Store analysis original: store_analysis_report.json")
        
        # Copy Store charts
        if store_analysis and "json_output" in store_analysis:
            chart_files = store_analysis["json_output"]["visualizations"]["chart_files"]
            
            chart_dir = result_dir / "store_charts"
            chart_dir.mkdir(exist_ok=True)
            
            for chart_name, chart_path in chart_files.items():
                if chart_path and Path(chart_path).exists():
                    dest = chart_dir / Path(chart_path).name
                    shutil.copy2(chart_path, dest)
            
            print(f"[OK] Store charts: {len(chart_files)} -> store_charts/")
        
        # Copy Mobility charts (already in open_sdk/output)
        if mobility_result and mobility_result.get("output_dir"):
            mobility_charts = Path(mobility_result["output_dir"])
            if mobility_charts.exists():
                dest_mobility = result_dir / "mobility_charts"
                shutil.copytree(mobility_charts, dest_mobility, dirs_exist_ok=True)
                print(f"[OK] Mobility charts: {len(list(mobility_charts.glob('*.png')))} -> mobility_charts/")
        
        # Copy Panorama results (already in open_sdk/output)
        if panorama_result and panorama_result.get("copied_output_folder"):
            panorama_folder = Path(panorama_result["copied_output_folder"])
            if panorama_folder.exists():
                dest_panorama = result_dir / "panorama"
                shutil.copytree(panorama_folder, dest_panorama, dirs_exist_ok=True)
                print(f"[OK] Panorama results -> panorama/")
        
        # Copy Marketplace data
        if marketplace_result and marketplace_result.get("output_dir"):
            marketplace_folder = Path(marketplace_result["output_dir"])
            if marketplace_folder.exists():
                dest_marketplace = result_dir / "marketplace"
                shutil.copytree(marketplace_folder, dest_marketplace, dirs_exist_ok=True)
                print(f"[OK] Marketplace results -> marketplace/")
        
        # Copy Spatial visualization files
        if spatial_info and spatial_info.get("visualization"):
            viz_files = spatial_info["visualization"]
            
            # Copy map file
            if viz_files.get("map_file"):
                map_src = Path(viz_files["map_file"])
                if map_src.exists():
                    map_dest = result_dir / "spatial_map.html"
                    shutil.copy2(map_src, map_dest)
                    print(f"[OK] Spatial map: spatial_map.html")
            
            # Copy chart file
            if viz_files.get("chart_file"):
                chart_src = Path(viz_files["chart_file"])
                if chart_src.exists():
                    chart_dest = result_dir / "spatial_analysis.png"
                    shutil.copy2(chart_src, chart_dest)
                    print(f"[OK] Spatial chart: spatial_analysis.png")
        
        print(f"\n[SAVE] All results saved successfully: {result_dir.name}/")
        
        return str(output_file)
        
    except Exception as e:
        print(f"[ERROR] Failed to save results: {e}")
        import traceback
        traceback.print_exc()
        return None


async def run_full_analysis_pipeline(store_code: str) -> Dict[str, Any]:
    """Execute full analysis pipeline (integrated with spatial_matcher)"""
    print("\n" + "="*60)
    print("INTEGRATED ANALYSIS PIPELINE START")
    print("="*60)
    print(f"\n[INFO] Store code: {store_code}")
    print(f"[INFO] Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 0: Address information analysis (using spatial_matcher)
    print("\n" + "="*60)
    print("[Step 0] Address Information Analysis (spatial_matcher)")
    print("="*60)
    
    # Extract address from Store Agent
    address = _get_address_from_store_code(store_code)
    if not address:
        print(f"\n[ERROR] Failed to extract address from store code {store_code}")
        return {"status": "failed", "step": "address_extraction"}
    
    print(f"[INFO] Analysis address: {address}")
    
    # Analyze address with spatial_matcher
    try:
        from spatial_matcher import get_location_info
        
        spatial_info = get_location_info(address, create_visualization=True)
        
        if spatial_info["status"] == "success":
            dong = spatial_info["dong"]
            marketplace_info = spatial_info["marketplace"]
            visualization_files = spatial_info["visualization"]
            
            print(f"[OK] Administrative dong: {dong}")
            print(f"[OK] Marketplace: {marketplace_info.get('상권명') if marketplace_info else 'N/A'}")
            print(f"[OK] Visualization: map/chart generated")
        else:
            print(f"[WARN] spatial_matcher failed, using default values")
            dong = "왕십리2동"  # Default
            marketplace_info = None
            visualization_files = None
            
    except Exception as e:
        print(f"[WARN] spatial_matcher error: {e}")
        dong = "왕십리2동"  # Default
        marketplace_info = None
        visualization_files = None
    
    # Step 1: Store Agent analysis
    store_analysis = await run_store_analysis(store_code)
    if not store_analysis:
        print("\n[ERROR] Pipeline interrupted due to Store Agent analysis failure")
        return {"status": "failed", "step": "store_analysis"}
    
    # Step 2: Marketing Agent analysis - SKIPPED (handled by app.py)
    print("\n" + "="*60)
    print("[Step 2] Marketing Agent Analysis - SKIPPED")
    print("="*60)
    print("[INFO] Marketing Agent는 app.py에서 직접 호출됩니다")
    print("[INFO] New Product Agent는 상담 시작 시 실행됩니다")
    
    # Step 3: Mobility analysis
    mobility_result = await run_mobility_analysis(address, dong)
    
    # Step 6: Panorama analysis (클라우드 환경에서는 자동 스킵)
    panorama_result = await run_panorama_analysis(address)
    
    # Step 7: Marketplace analysis - Using spatial_matcher result
    marketplace_result = get_marketplace_json(address, spatial_info)
    
    # Step 8: Save results (including visualization files)
    output_file = save_results(
        store_code, 
        store_analysis, 
        mobility_result,
        panorama_result,
        marketplace_result,
        spatial_info=spatial_info if 'spatial_info' in locals() else None
    )
    
    # Completion summary
    print("\n" + "="*60)
    print("ANALYSIS PIPELINE COMPLETED!")
    print("="*60)
    print(f"\n[SUMMARY] Results Summary:")
    print(f"   [OK] Address analysis: Completed (dong: {dong})")
    print(f"   [OK] Store analysis: Completed")
    print(f"   [INFO] Marketing strategy: Handled by app.py (상담 시작 시)")
    print(f"   [INFO] New Product Agent: Handled by app.py (상담 시작 시)")
    print(f"   [WARN] Mobility: {mobility_result.get('status', 'unknown')}")
    print(f"   [WARN] Panorama: {panorama_result.get('status', 'unknown')}")
    print(f"   [INFO] Marketplace: {marketplace_result.get('status', 'unknown')}")
    
    if output_file:
        print(f"\n[OUTPUT] Output file: {output_file}")
    
    if visualization_files:
        print(f"\n[VISUALIZATION] Map: {visualization_files['map_file']}")
        print(f"   Chart: {visualization_files['chart_file']}")
    
    print(f"\n[INFO] Completion time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        "status": "success",
        "store_code": store_code,
        "output_file": output_file,
        "store_analysis": store_analysis,
        "spatial_info": spatial_info if 'spatial_info' in locals() else None
    }


async def main():
    """Main function"""
    # Default test store code
    store_code = "000F03E44A"
    
    # Use command line argument if available
    if len(sys.argv) > 1:
        store_code = sys.argv[1]
    
    # Execute full pipeline
    result = await run_full_analysis_pipeline(store_code)
    
    return result


if __name__ == "__main__":
    # Async execution
    result = asyncio.run(main())
    
    if result and result.get("status") == "success":
        print("\n[SUCCESS] All analyses completed successfully!")
    else:
        print("\n[FAILED] Some analyses failed.")

