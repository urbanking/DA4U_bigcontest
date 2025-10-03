"""
에이전트 메모리 시스템
장기/단기 메모리 관리 및 학습 기능
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass, asdict

from database.connection import get_db_manager

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """메모리 엔트리 구조"""
    user_id: str
    session_id: str
    query: str
    analysis_result: Dict[str, Any]
    evaluation_scores: Dict[str, float]
    timestamp: datetime
    memory_type: str  # "short_term" or "long_term"
    importance_score: float  # 0.0 to 1.0


class AgentMemoryManager:
    """에이전트 메모리 관리자"""
    
    def __init__(self):
        """메모리 관리자 초기화"""
        self.db = get_db_manager()
        self.short_term_memory = {}  # 세션 기반 단기 메모리
        self.learning_patterns = {}  # 학습된 패턴들
        
        # 메모리 설정
        self.SHORT_TERM_DURATION = timedelta(hours=24)  # 단기 메모리 유지 시간
        self.IMPORTANCE_THRESHOLD = 0.7  # 장기 메모리 저장 임계값
        
    async def load_user_memory(
        self, 
        user_id: str, 
        query: str
    ) -> Dict[str, Any]:
        """
        사용자 메모리 로드 및 관련 인사이트 제공
        
        Args:
            user_id: 사용자 ID
            query: 현재 쿼리
            
        Returns:
            메모리 기반 인사이트
        """
        try:
            # 1. 단기 메모리에서 관련 정보 검색
            short_term_insights = self._search_short_term_memory(user_id, query)
            
            # 2. 장기 메모리에서 관련 패턴 검색
            long_term_insights = await self._search_long_term_memory(user_id, query)
            
            # 3. 학습된 패턴에서 유사한 케이스 검색
            pattern_insights = self._search_learned_patterns(query)
            
            # 4. 메모리 기반 추천 생성
            recommendations = self._generate_memory_recommendations(
                short_term_insights,
                long_term_insights,
                pattern_insights
            )
            
            return {
                "short_term": short_term_insights,
                "long_term": long_term_insights,
                "patterns": pattern_insights,
                "recommendations": recommendations,
                "memory_available": True
            }
            
        except Exception as e:
            logger.error(f"메모리 로드 에러: {e}")
            return {"memory_available": False, "error": str(e)}
    
    async def save_analysis_result(
        self,
        user_id: str,
        session_id: str,
        analysis_result: Dict[str, Any],
        evaluation_scores: Dict[str, float]
    ):
        """
        분석 결과를 메모리에 저장
        
        Args:
            user_id: 사용자 ID
            session_id: 세션 ID
            analysis_result: 분석 결과
            evaluation_scores: 평가 점수
        """
        try:
            query = analysis_result.get("user_query", "")
            
            # 중요도 점수 계산
            importance_score = self._calculate_importance_score(
                analysis_result,
                evaluation_scores
            )
            
            # 단기 메모리에 저장
            memory_entry = MemoryEntry(
                user_id=user_id,
                session_id=session_id,
                query=query,
                analysis_result=analysis_result,
                evaluation_scores=evaluation_scores,
                timestamp=datetime.now(),
                memory_type="short_term",
                importance_score=importance_score
            )
            
            # 세션 기반 단기 메모리 저장
            if user_id not in self.short_term_memory:
                self.short_term_memory[user_id] = []
            self.short_term_memory[user_id].append(memory_entry)
            
            # 중요도가 높으면 장기 메모리에도 저장
            if importance_score >= self.IMPORTANCE_THRESHOLD:
                await self._save_to_long_term_memory(memory_entry)
            
            # 학습 패턴 업데이트
            await self._update_learning_patterns(memory_entry)
            
            logger.info(f"메모리 저장 완료 - User: {user_id}, Session: {session_id}")
            
        except Exception as e:
            logger.error(f"메모리 저장 에러: {e}")
    
    def _search_short_term_memory(
        self, 
        user_id: str, 
        query: str
    ) -> List[Dict[str, Any]]:
        """단기 메모리에서 관련 정보 검색"""
        insights = []
        
        if user_id in self.short_term_memory:
            current_time = datetime.now()
            user_memories = self.short_term_memory[user_id]
            
            # 최근 24시간 내 메모리만 필터링
            recent_memories = [
                mem for mem in user_memories
                if current_time - mem.timestamp <= self.SHORT_TERM_DURATION
            ]
            
            # 쿼리 유사도 기반 검색
            for memory in recent_memories:
                similarity = self._calculate_query_similarity(query, memory.query)
                if similarity > 0.3:  # 유사도 임계값
                    insights.append({
                        "session_id": memory.session_id,
                        "similarity": similarity,
                        "previous_result": memory.analysis_result,
                        "timestamp": memory.timestamp.isoformat()
                    })
        
        return sorted(insights, key=lambda x: x["similarity"], reverse=True)[:3]
    
    async def _search_long_term_memory(
        self, 
        user_id: str, 
        query: str
    ) -> List[Dict[str, Any]]:
        """장기 메모리에서 관련 패턴 검색"""
        try:
            # 데이터베이스에서 장기 메모리 조회
            db = get_db_manager()
            query_sql = """
                SELECT session_id, query, analysis_result, evaluation_scores,
                       importance_score, timestamp
                FROM agent_long_term_memory
                WHERE user_id = :user_id
                  AND timestamp >= :cutoff_date
                ORDER BY importance_score DESC, timestamp DESC
                LIMIT 20
            """
            
            cutoff_date = datetime.now() - timedelta(days=30)  # 최근 30일
            results = db.execute_query(query_sql, {
                "user_id": user_id,
                "cutoff_date": cutoff_date
            })
            
            insights = []
            for row in results:
                similarity = self._calculate_query_similarity(query, row[1])
                if similarity > 0.2:
                    insights.append({
                        "session_id": row[0],
                        "similarity": similarity,
                        "importance": row[4],
                        "timestamp": row[5].isoformat()
                    })
            
            return sorted(insights, key=lambda x: x["similarity"], reverse=True)[:5]
            
        except Exception as e:
            logger.error(f"장기 메모리 검색 에러: {e}")
            return []
    
    def _search_learned_patterns(self, query: str) -> List[Dict[str, Any]]:
        """학습된 패턴에서 유사한 케이스 검색"""
        patterns = []
        
        # 쿼리 키워드 추출
        query_keywords = self._extract_keywords(query)
        
        for pattern_type, pattern_data in self.learning_patterns.items():
            similarity = self._calculate_keyword_similarity(
                query_keywords, 
                pattern_data.get("keywords", [])
            )
            
            if similarity > 0.3:
                patterns.append({
                    "pattern_type": pattern_type,
                    "similarity": similarity,
                    "recommendations": pattern_data.get("recommendations", []),
                    "success_rate": pattern_data.get("success_rate", 0)
                })
        
        return sorted(patterns, key=lambda x: x["similarity"], reverse=True)[:3]
    
    def _generate_memory_recommendations(
        self,
        short_term: List[Dict],
        long_term: List[Dict],
        patterns: List[Dict]
    ) -> Dict[str, Any]:
        """메모리 기반 추천 생성"""
        recommendations = {
            "based_on_history": len(short_term) > 0,
            "based_on_patterns": len(patterns) > 0,
            "suggestions": []
        }
        
        # 이전 분석 결과 기반 추천
        if short_term:
            recommendations["suggestions"].append({
                "type": "historical",
                "message": f"이전에 유사한 분석을 {len(short_term)}번 수행했습니다.",
                "action": "이전 결과와 비교하여 새로운 인사이트를 제공합니다."
            })
        
        # 패턴 기반 추천
        if patterns:
            best_pattern = patterns[0]
            recommendations["suggestions"].append({
                "type": "pattern",
                "message": f"유사한 패턴에서 {best_pattern['success_rate']:.1%} 성공률을 보였습니다.",
                "action": f"{best_pattern['pattern_type']} 접근법을 권장합니다."
            })
        
        return recommendations
    
    async def _save_to_long_term_memory(self, memory_entry: MemoryEntry):
        """중요한 메모리를 장기 메모리에 저장"""
        try:
            db = get_db_manager()
            query = """
                INSERT INTO agent_long_term_memory 
                (user_id, session_id, query, analysis_result, evaluation_scores,
                 importance_score, timestamp)
                VALUES (:user_id, :session_id, :query, :analysis_result, 
                        :evaluation_scores, :importance_score, :timestamp)
            """
            
            db.execute_query(query, {
                "user_id": memory_entry.user_id,
                "session_id": memory_entry.session_id,
                "query": memory_entry.query,
                "analysis_result": json.dumps(memory_entry.analysis_result),
                "evaluation_scores": json.dumps(memory_entry.evaluation_scores),
                "importance_score": memory_entry.importance_score,
                "timestamp": memory_entry.timestamp
            })
            
            logger.info(f"장기 메모리 저장 완료 - User: {memory_entry.user_id}")
            
        except Exception as e:
            logger.error(f"장기 메모리 저장 에러: {e}")
    
    async def _update_learning_patterns(self, memory_entry: MemoryEntry):
        """학습 패턴 업데이트"""
        try:
            # 쿼리 키워드 추출
            keywords = self._extract_keywords(memory_entry.query)
            
            # 평가 점수 기반 성공 여부 판단
            avg_score = sum(memory_entry.evaluation_scores.values()) / len(memory_entry.evaluation_scores)
            is_successful = avg_score > 0.7
            
            # 패턴 업데이트
            pattern_key = "_".join(keywords[:3])  # 상위 3개 키워드로 패턴 생성
            
            if pattern_key not in self.learning_patterns:
                self.learning_patterns[pattern_key] = {
                    "keywords": keywords,
                    "success_count": 0,
                    "total_count": 0,
                    "recommendations": []
                }
            
            pattern = self.learning_patterns[pattern_key]
            pattern["total_count"] += 1
            
            if is_successful:
                pattern["success_count"] += 1
            
            pattern["success_rate"] = pattern["success_count"] / pattern["total_count"]
            
            logger.info(f"학습 패턴 업데이트 - Pattern: {pattern_key}")
            
        except Exception as e:
            logger.error(f"학습 패턴 업데이트 에러: {e}")
    
    def _calculate_importance_score(
        self,
        analysis_result: Dict[str, Any],
        evaluation_scores: Dict[str, float]
    ) -> float:
        """중요도 점수 계산"""
        score = 0.0
        
        # 평가 점수 기반 (40%)
        if evaluation_scores:
            avg_eval_score = sum(evaluation_scores.values()) / len(evaluation_scores)
            score += avg_eval_score * 0.4
        
        # 분석 결과의 복잡성 기반 (30%)
        agent_count = len(analysis_result.get("agent_results", {}))
        complexity_score = min(agent_count / 6.0, 1.0)  # 최대 6개 에이전트
        score += complexity_score * 0.3
        
        # 최종 보고서 존재 여부 (30%)
        if analysis_result.get("final_report"):
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_query_similarity(self, query1: str, query2: str) -> float:
        """쿼리 유사도 계산 (간단한 키워드 기반)"""
        keywords1 = set(query1.lower().split())
        keywords2 = set(query2.lower().split())
        
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_keyword_similarity(self, keywords1: List[str], keywords2: List[str]) -> float:
        """키워드 유사도 계산"""
        set1 = set(keywords1)
        set2 = set(keywords2)
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 기법 사용 가능)
        stop_words = {"왜", "어떻게", "무엇", "어디", "언제", "누가", "의", "를", "을", "가", "이"}
        words = text.lower().split()
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        return keywords[:10]  # 상위 10개 키워드만
    
    async def get_analysis_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 ID로 분석 결과 조회"""
        try:
            db = get_db_manager()
            query = """
                SELECT analysis_result, evaluation_scores, timestamp
                FROM agent_long_term_memory
                WHERE session_id = :session_id
            """
            
            results = db.execute_query(query, {"session_id": session_id})
            if results:
                row = results[0]
                return {
                    "analysis_result": json.loads(row[0]),
                    "evaluation_scores": json.loads(row[1]),
                    "timestamp": row[2].isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"분석 결과 조회 에러: {e}")
            return None
    
    async def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """사용자 분석 히스토리 조회"""
        try:
            db = get_db_manager()
            query = """
                SELECT session_id, query, evaluation_scores, timestamp
                FROM agent_long_term_memory
                WHERE user_id = :user_id
                ORDER BY timestamp DESC
                LIMIT :limit
            """
            
            results = db.execute_query(query, {
                "user_id": user_id,
                "limit": limit
            })
            
            history = []
            for row in results:
                history.append({
                    "session_id": row[0],
                    "query": row[1],
                    "evaluation_scores": json.loads(row[2]),
                    "timestamp": row[3].isoformat()
                })
            
            return history
            
        except Exception as e:
            logger.error(f"사용자 히스토리 조회 에러: {e}")
            return []
    
    def is_healthy(self) -> bool:
        """메모리 시스템 상태 확인"""
        try:
            # 단기 메모리 상태 확인
            short_term_ok = isinstance(self.short_term_memory, dict)
            
            # 데이터베이스 연결 확인
            db_ok = self.db.test_connection()
            
            return short_term_ok and db_ok
            
        except Exception as e:
            logger.error(f"메모리 시스템 상태 확인 에러: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """메모리 시스템 상태 정보"""
        return {
            "short_term_memory_entries": sum(
                len(memories) for memories in self.short_term_memory.values()
            ),
            "learned_patterns": len(self.learning_patterns),
            "is_healthy": self.is_healthy()
        }
