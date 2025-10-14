"""
Mobility 데이터 시각화 스크립트
Usage: python visualize_mobility.py <json_file_path>
"""
import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# 한글 폰트 설정
try:
    plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
except:
    try:
        plt.rcParams['font.family'] = 'AppleGothic'  # Mac
    except:
        plt.rcParams['font.family'] = 'DejaVu Sans'  # Fallback
plt.rcParams['axes.unicode_minus'] = False


def load_data(json_path: str) -> dict:
    """JSON 파일 로드"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def visualize_all(data: dict, output_dir: Path):
    """전체 시각화"""
    analysis = data['analysis']
    target_dong = data['target_dong']
    
    output_dir.mkdir(exist_ok=True)
    
    # 1. 이동 유형
    plot_move_types(analysis['part1_move_types'], target_dong, output_dir)
    
    # 2. 시간대별 패턴
    plot_time_pattern(analysis['part2_time_pattern'], target_dong, output_dir)
    
    # 3. 목적별 이동
    plot_purpose(analysis['part3_purpose'], target_dong, output_dir)
    
    # 4. 교통수단
    plot_transport(analysis['part4_transport'], target_dong, output_dir)
    
    # 5. 연령대별
    plot_age(analysis['part5_age'], target_dong, output_dir)
    
    # 6. 연령별 주요 목적
    plot_age_purpose(analysis['part5_2_age_purpose'], target_dong, output_dir)
    
    # 7. 연령별 피크 시간
    plot_age_time(analysis['part5_3_age_time'], target_dong, output_dir)
    
    print(f"\n✅ 시각화 완료! 📊")
    print(f"📂 저장 위치: {output_dir}/")
    print(f"   생성된 그래프: 7개")


def plot_move_types(data: dict, dong: str, output_dir: Path):
    """1. 이동 유형"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    labels = list(data.keys())
    values = list(data.values())
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    bars = ax.bar(labels, values, color=colors, alpha=0.8, edgecolor='black')
    
    # 값 표시
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_title(f'📊 {dong} - 이동 유형', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('이동 건수', fontsize=12)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_dir / '1_이동유형.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ 1_이동유형.png")


def plot_time_pattern(data: dict, dong: str, output_dir: Path):
    """2. 시간대별 패턴"""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    hours = [int(h) for h in data.keys()]
    values = list(data.values())
    
    # 그라데이션 색상
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(hours)))
    
    bars = ax.bar(hours, values, color=colors, alpha=0.8, edgecolor='black')
    
    # 피크 시간 표시
    peak_hour = max(data.items(), key=lambda x: x[1])
    peak_idx = hours.index(int(peak_hour[0]))
    bars[peak_idx].set_color('red')
    bars[peak_idx].set_alpha(1.0)
    
    ax.set_title(f'⏰ {dong} - 시간대별 이동 패턴 (피크: {peak_hour[0]}시)', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('시간 (시)', fontsize=12)
    ax.set_ylabel('이동 건수', fontsize=12)
    ax.set_xticks(hours)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_dir / '2_시간대별패턴.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ 2_시간대별패턴.png")


def plot_purpose(data: dict, dong: str, output_dir: Path):
    """3. 목적별 이동"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    labels = list(data.keys())
    values = list(data.values())
    
    # 막대 그래프
    colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
    bars = ax1.barh(labels, values, color=colors, alpha=0.8, edgecolor='black')
    
    for bar in bars:
        width = bar.get_width()
        ax1.text(width, bar.get_y() + bar.get_height()/2.,
                f'{int(width):,}',
                ha='left', va='center', fontsize=10, fontweight='bold')
    
    ax1.set_title('목적별 이동 건수', fontsize=14, fontweight='bold')
    ax1.set_xlabel('이동 건수', fontsize=12)
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    
    # 파이 차트
    ax2.pie(values, labels=labels, autopct='%1.1f%%', 
            colors=colors, startangle=90)
    ax2.set_title('목적별 비율', fontsize=14, fontweight='bold')
    
    fig.suptitle(f'🎯 {dong} - 이동 목적 분석', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / '3_목적별이동.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ 3_목적별이동.png")


def plot_transport(data: dict, dong: str, output_dir: Path):
    """4. 교통수단"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 정렬
    sorted_data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
    labels = list(sorted_data.keys())
    values = list(sorted_data.values())
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
    bars = ax.bar(labels, values, color=colors[:len(labels)], alpha=0.8, edgecolor='black')
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_title(f'🚗 {dong} - 교통수단별 이용', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('이용 건수', fontsize=12)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.xticks(rotation=15, ha='right')
    
    plt.tight_layout()
    plt.savefig(output_dir / '4_교통수단.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ 4_교통수단.png")


def plot_age(data: dict, dong: str, output_dir: Path):
    """5. 연령대별"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    labels = list(data.keys())
    values = list(data.values())
    
    colors = plt.cm.RdYlBu_r(np.linspace(0.2, 0.9, len(labels)))
    bars = ax.bar(labels, values, color=colors, alpha=0.8, edgecolor='black')
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_title(f'👥 {dong} - 연령대별 이동', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('이동 건수', fontsize=12)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_dir / '5_연령대별.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ 5_연령대별.png")


def plot_age_purpose(data: dict, dong: str, output_dir: Path):
    """6. 연령별 주요 목적"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    ages = list(data.keys())
    purposes = [data[age]['top_purpose'] for age in ages]
    percentages = [data[age]['percentage'] for age in ages]
    
    colors = ['#FF6B6B' if '기타' in p else '#4ECDC4' for p in purposes]
    bars = ax.barh(ages, percentages, color=colors, alpha=0.8, edgecolor='black')
    
    for i, (bar, purpose, pct) in enumerate(zip(bars, purposes, percentages)):
        ax.text(pct + 1, bar.get_y() + bar.get_height()/2.,
                f'{purpose} ({pct:.1f}%)',
                ha='left', va='center', fontsize=10, fontweight='bold')
    
    ax.set_title(f'🎯 {dong} - 연령대별 주요 이동 목적', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('비율 (%)', fontsize=12)
    ax.set_xlim(0, max(percentages) + 15)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_dir / '6_연령별목적.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ 6_연령별목적.png")


def plot_age_time(data: dict, dong: str, output_dir: Path):
    """7. 연령별 피크 시간"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    ages = list(data.keys())
    peak_hours = [data[age]['peak_hour'] for age in ages]
    peak_counts = [data[age]['peak_count'] for age in ages]
    
    # 산점도 + 막대 그래프 결합
    colors = plt.cm.rainbow(np.linspace(0, 1, len(ages)))
    
    for i, (age, hour, count, color) in enumerate(zip(ages, peak_hours, peak_counts, colors)):
        ax.scatter(hour, count, s=500, color=color, alpha=0.6, edgecolor='black', linewidth=2)
        ax.text(hour, count, age, ha='center', va='center', fontsize=9, fontweight='bold')
    
    ax.set_title(f'⏰ {dong} - 연령대별 피크 시간', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('시간 (시)', fontsize=12)
    ax.set_ylabel('피크 시간대 이동 건수', fontsize=12)
    ax.set_xticks(range(0, 24, 2))
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_dir / '7_연령별피크시간.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ 7_연령별피크시간.png")


def visualize_latest_from_folder(folder_path: str = "test_output") -> bool:
    """
    test_output 폴더에서 최신 mobility_*.json 파일을 찾아 시각화
    
    Returns:
        성공 여부
    """
    from glob import glob
    
    folder = Path(folder_path)
    mobility_files = sorted(glob(str(folder / "mobility_*.json")))
    
    if not mobility_files:
        print("[Mobility Viz] mobility_*.json 파일 없음")
        return False
    
    json_path = Path(mobility_files[-1])  # 최신 파일
    
    try:
        # 데이터 로드
        data = load_data(json_path)
        
        # 출력 디렉토리
        output_dir = json_path.parent / f"mobility_viz_{data['timestamp']}"
        
        # 시각화
        visualize_all(data, output_dir)
        return True
    except Exception as e:
        print(f"[Mobility Viz] Error: {e}")
        return False


def main():
    """메인 실행"""
    if len(sys.argv) < 2:
        # 인자 없으면 test_output에서 자동 찾기
        print("[Mobility] test_output에서 최신 파일 찾는 중...")
        success = visualize_latest_from_folder("test_output")
        if success:
            print("[Mobility] 시각화 완료!")
        return
    
    json_path = sys.argv[1]
    
    # 와일드카드 처리
    if '*' in json_path:
        from glob import glob
        files = glob(json_path)
        if not files:
            print(f"파일을 찾을 수 없습니다: {json_path}")
            return
        json_path = sorted(files)[-1]
        print(f"최신 파일 선택: {json_path}")
    
    json_path = Path(json_path)
    
    if not json_path.exists():
        print(f"파일이 없습니다: {json_path}")
        return
    
    # 데이터 로드
    data = load_data(json_path)
    
    # 출력 디렉토리
    output_dir = json_path.parent / f"mobility_viz_{data['timestamp']}"
    
    # 시각화
    visualize_all(data, output_dir)
    print("[Mobility] 완료!")


if __name__ == "__main__":
    main()

