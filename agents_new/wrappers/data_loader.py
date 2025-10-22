"""
Data Loader - Load existing analysis data from data outputs
기존 분석 결과 JSON 파일 로딩
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List


class DataLoader:
    """
    Load existing analysis data from data outputs folder
    
    데이터 소스:
    1. 상권분석서비스_결과/*.json - 50개 상권 분석
    2. 이동분석_결과/{동}/results_*.json - 동별 이동 데이터
    3. store_agent_reports/*.json - 점포 분석
    4. 파노라마analysis_img_300m/*.json - 파노라마 분석
    """
    
    def __init__(self):
        """Initialize data loader"""
        self.data_dir = Path(__file__).parent.parent / "data outputs"
        
        # Available data
        self.marketplace_dir = self.data_dir / "상권분석서비스_결과"
        self.mobility_dir = self.data_dir / "이동분석_결과"
        self.store_dir = self.data_dir / "store_agent_reports"
        self.panorama_dir = self.data_dir / "파노라마analysis_img_300m"
        
        # Cache available locations
        self._load_available_data()
    
    def _load_available_data(self):
        """Load available data locations"""
        # Marketplace locations
        self.marketplace_locations = []
        if self.marketplace_dir.exists():
            for file in self.marketplace_dir.glob("*.json"):
                self.marketplace_locations.append(file.stem)
        
        # Mobility dongs
        self.mobility_dongs = []
        if self.mobility_dir.exists():
            for dong_dir in self.mobility_dir.iterdir():
                if dong_dir.is_dir():
                    self.mobility_dongs.append(dong_dir.name)
        
        print(f"[DataLoader] Available: {len(self.marketplace_locations)} marketplace, "
              f"{len(self.mobility_dongs)} mobility dongs")
    
    def find_marketplace_data(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Find marketplace data matching query
        
        Args:
            query: Search query (address or location name)
            
        Returns:
            Marketplace data or None
        """
        # Search in available locations
        best_match = None
        max_score = 0
        
        for location in self.marketplace_locations:
            score = self._match_score(query, location)
            if score > max_score:
                max_score = score
                best_match = location
        
        if best_match and max_score > 0:
            file_path = self.marketplace_dir / f"{best_match}.json"
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"[DataLoader] Loaded marketplace: {best_match}")
                return data
            except Exception as e:
                print(f"[DataLoader] Error loading {best_match}: {e}")
                return None
        
        print(f"[DataLoader] No marketplace match for: {query}")
        return None
    
    def find_mobility_data(self, dong: str) -> Optional[Dict[str, Any]]:
        """
        Find mobility data for dong
        
        Args:
            dong: Dong name (e.g., "왕십리2동")
            
        Returns:
            Mobility data or None
        """
        # Direct match
        if dong in self.mobility_dongs:
            dong_dir = self.mobility_dir / dong
            json_files = list(dong_dir.glob("results_*.json"))
            
            if json_files:
                # Get most recent
                latest = max(json_files, key=lambda p: p.stat().st_mtime)
                try:
                    with open(latest, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"[DataLoader] Loaded mobility: {dong}")
                    return data
                except Exception as e:
                    print(f"[DataLoader] Error loading mobility: {e}")
                    return None
        
        # Fuzzy match
        best_match = None
        max_score = 0
        
        for available_dong in self.mobility_dongs:
            score = self._match_score(dong, available_dong)
            if score > max_score:
                max_score = score
                best_match = available_dong
        
        if best_match and max_score > 0.5:
            print(f"[DataLoader] Fuzzy match: {dong} -> {best_match}")
            return self.find_mobility_data(best_match)
        
        print(f"[DataLoader] No mobility data for: {dong}")
        return None
    
    def load_store_data(self, store_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Load store analysis data
        
        Args:
            store_code: Store code (optional)
            
        Returns:
            Store data or None
        """
        if not self.store_dir.exists():
            return None
        
        json_files = list(self.store_dir.glob("*.json"))
        
        if not json_files:
            print("[DataLoader] No store data available")
            return None
        
        # If store_code specified, find exact match
        if store_code:
            for file in json_files:
                if store_code in file.name:
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        print(f"[DataLoader] Loaded store: {store_code}")
                        return data
                    except Exception as e:
                        print(f"[DataLoader] Error loading store: {e}")
                        return None
        
        # Otherwise, return most recent
        latest = max(json_files, key=lambda p: p.stat().st_mtime)
        try:
            with open(latest, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"[DataLoader] Loaded latest store data")
            return data
        except Exception as e:
            print(f"[DataLoader] Error loading store: {e}")
            return None
    
    def load_panorama_data(self) -> Optional[Dict[str, Any]]:
        """
        Load panorama analysis data
        
        Returns:
            Panorama data or None
        """
        json_file = self.panorama_dir / "analysis_result.json"
        
        if not json_file.exists():
            print("[DataLoader] No panorama data available")
            return None
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print("[DataLoader] Loaded panorama data")
            return data
        except Exception as e:
            print(f"[DataLoader] Error loading panorama: {e}")
            return None
    
    def _match_score(self, query: str, target: str) -> float:
        """
        Calculate match score between query and target
        
        Args:
            query: Query string
            target: Target string
            
        Returns:
            Match score (0.0 - 1.0)
        """
        query = query.lower().replace(" ", "")
        target = target.lower().replace(" ", "")
        
        # Exact match
        if query == target:
            return 1.0
        
        # Contains match
        if query in target or target in query:
            return 0.8
        
        # Character overlap
        common = set(query) & set(target)
        if common:
            return len(common) / max(len(query), len(target)) * 0.5
        
        return 0.0
    
    def get_available_locations(self) -> Dict[str, List[str]]:
        """
        Get all available data locations
        
        Returns:
            Dictionary of available locations by type
        """
        return {
            "marketplace": self.marketplace_locations,
            "mobility": self.mobility_dongs,
            "store": "available" if list(self.store_dir.glob("*.json")) else "none",
            "panorama": "available" if (self.panorama_dir / "analysis_result.json").exists() else "none"
        }


# Singleton instance
_data_loader = None

def get_data_loader() -> DataLoader:
    """Get singleton data loader instance"""
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader

