"""
JSON, CSV 저장
"""
import json
import csv
from pathlib import Path
from typing import Dict, Any, List


class DataWriter:
    """데이터 작성기"""
    
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def write_json(self, data: Dict[str, Any], filename: str, subdir: str = ""):
        """JSON 파일 저장"""
        if subdir:
            path = self.output_dir / subdir
            path.mkdir(parents=True, exist_ok=True)
        else:
            path = self.output_dir
        
        filepath = path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def write_csv(self, data: List[Dict[str, Any]], filename: str, subdir: str = ""):
        """CSV 파일 저장"""
        if not data:
            return
        
        if subdir:
            path = self.output_dir / subdir
            path.mkdir(parents=True, exist_ok=True)
        else:
            path = self.output_dir
        
        filepath = path / filename
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

