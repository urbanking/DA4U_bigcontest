-- 에이전트 메모리 시스템을 위한 추가 테이블들

-- 장기 메모리 테이블
CREATE TABLE IF NOT EXISTS agent_long_term_memory (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    query TEXT NOT NULL,
    analysis_result JSONB NOT NULL,
    evaluation_scores JSONB NOT NULL,
    importance_score DECIMAL(3, 2) CHECK (importance_score >= 0.0 AND importance_score <= 1.0),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_timestamp (user_id, timestamp),
    INDEX idx_importance (importance_score),
    INDEX idx_session (session_id)
);

-- 평가 피드백 테이블
CREATE TABLE IF NOT EXISTS evaluation_feedback (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    feedback_type VARCHAR(50), -- 'user_rating', 'accuracy', 'usefulness'
    feedback_data JSONB NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comments TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session (session_id),
    INDEX idx_user (user_id)
);

-- 학습 패턴 테이블
CREATE TABLE IF NOT EXISTS learning_patterns (
    id SERIAL PRIMARY KEY,
    pattern_key VARCHAR(100) UNIQUE NOT NULL,
    pattern_type VARCHAR(50), -- 'query_pattern', 'success_pattern', 'failure_pattern'
    keywords TEXT[] NOT NULL,
    success_count INTEGER DEFAULT 0,
    total_count INTEGER DEFAULT 0,
    success_rate DECIMAL(3, 2) DEFAULT 0.0,
    recommendations JSONB,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_pattern_key (pattern_key),
    INDEX idx_success_rate (success_rate)
);

-- 시스템 성능 메트릭 테이블
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10, 4) NOT NULL,
    metric_unit VARCHAR(20),
    agent_name VARCHAR(100),
    session_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_metric_name (metric_name),
    INDEX idx_timestamp (timestamp),
    INDEX idx_agent (agent_name)
);

-- 에이전트 실행 로그 테이블
CREATE TABLE IF NOT EXISTS agent_execution_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    execution_time_ms INTEGER,
    status VARCHAR(20) NOT NULL, -- 'success', 'error', 'timeout'
    error_message TEXT,
    input_data JSONB,
    output_data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session (session_id),
    INDEX idx_agent (agent_name),
    INDEX idx_status (status),
    INDEX idx_timestamp (timestamp)
);

-- 메모리 인덱스 최적화
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agent_memory_user_query 
ON agent_long_term_memory USING GIN (to_tsvector('korean', query));

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agent_memory_analysis_result 
ON agent_long_term_memory USING GIN (analysis_result);

-- 파티셔닝 (월별)
-- 2024년 1월부터 시작
CREATE TABLE IF NOT EXISTS agent_long_term_memory_202401 
PARTITION OF agent_long_term_memory 
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- 뷰 생성
CREATE OR REPLACE VIEW agent_performance_summary AS
SELECT 
    agent_name,
    COUNT(*) as total_executions,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_executions,
    ROUND(
        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) as success_rate,
    AVG(execution_time_ms) as avg_execution_time_ms,
    MAX(timestamp) as last_execution
FROM agent_execution_logs
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY agent_name
ORDER BY success_rate DESC;

-- 사용자별 분석 통계 뷰
CREATE OR REPLACE VIEW user_analysis_stats AS
SELECT 
    user_id,
    COUNT(*) as total_analyses,
    AVG(importance_score) as avg_importance,
    MAX(timestamp) as last_analysis,
    COUNT(DISTINCT DATE(timestamp)) as active_days
FROM agent_long_term_memory
WHERE timestamp >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY user_id
ORDER BY total_analyses DESC;
