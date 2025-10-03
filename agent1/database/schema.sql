-- Multi-Agent Commercial District Analysis System
-- 3-Layer Database Schema

-- ============================================
-- MACRO LAYER: District-Level Data
-- ============================================

CREATE TABLE IF NOT EXISTS macro_district_trends (
    id SERIAL PRIMARY KEY,
    district_code VARCHAR(50) NOT NULL,
    district_name VARCHAR(100) NOT NULL,
    year_quarter VARCHAR(10) NOT NULL,
    status VARCHAR(20), -- 'expanding', 'stagnant', 'declining', 'dynamic'
    total_stores INTEGER,
    total_sales BIGINT,
    avg_sales_per_store DECIMAL(15, 2),
    population_flow INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(district_code, year_quarter)
);

CREATE TABLE IF NOT EXISTS macro_population_flow (
    id SERIAL PRIMARY KEY,
    district_code VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    hour INTEGER CHECK (hour >= 0 AND hour <= 23),
    flow_count INTEGER,
    age_group VARCHAR(20), -- '10s', '20s', '30s', etc.
    gender VARCHAR(10), -- 'male', 'female'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS macro_infrastructure (
    id SERIAL PRIMARY KEY,
    district_code VARCHAR(50) NOT NULL,
    subway_stations INTEGER DEFAULT 0,
    bus_stops INTEGER DEFAULT 0,
    parking_lots INTEGER DEFAULT 0,
    parking_capacity INTEGER DEFAULT 0,
    avg_accessibility_score DECIMAL(3, 2), -- 0.00 to 5.00
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- MESO LAYER: Competitor & Industry Data
-- ============================================

CREATE TABLE IF NOT EXISTS meso_competitor_info (
    id SERIAL PRIMARY KEY,
    store_name VARCHAR(200) NOT NULL,
    business_type VARCHAR(100),
    district_code VARCHAR(50),
    address TEXT,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    naver_rating DECIMAL(2, 1),
    review_count INTEGER,
    price_range VARCHAR(20), -- 'low', 'medium', 'high'
    last_crawled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS meso_industry_trends (
    id SERIAL PRIMARY KEY,
    business_type VARCHAR(100) NOT NULL,
    year_quarter VARCHAR(10) NOT NULL,
    avg_monthly_sales DECIMAL(15, 2),
    store_count INTEGER,
    closure_rate DECIMAL(5, 2), -- percentage
    trend_direction VARCHAR(20), -- 'up', 'down', 'stable'
    viral_menus TEXT[], -- array of trending menu items
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS meso_delivery_app_data (
    id SERIAL PRIMARY KEY,
    store_name VARCHAR(200),
    platform VARCHAR(50), -- 'baemin', 'coupang', 'yogiyo'
    promotion_type VARCHAR(100),
    discount_rate INTEGER,
    menu_items TEXT[],
    crawled_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- MICRO LAYER: Store-Specific Data
-- ============================================

CREATE TABLE IF NOT EXISTS micro_store_profile (
    id SERIAL PRIMARY KEY,
    store_id VARCHAR(50) UNIQUE NOT NULL,
    store_name VARCHAR(200) NOT NULL,
    business_type VARCHAR(100),
    district_code VARCHAR(50),
    opening_date DATE,
    owner_contact VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS micro_sales_data (
    id SERIAL PRIMARY KEY,
    store_id VARCHAR(50) NOT NULL,
    sale_date DATE NOT NULL,
    day_of_week VARCHAR(10),
    hour INTEGER CHECK (hour >= 0 AND hour <= 23),
    sales_amount DECIMAL(12, 2),
    transaction_count INTEGER,
    customer_count INTEGER,
    age_group VARCHAR(20),
    gender VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES micro_store_profile(store_id)
);

CREATE TABLE IF NOT EXISTS micro_menu_performance (
    id SERIAL PRIMARY KEY,
    store_id VARCHAR(50) NOT NULL,
    menu_item VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10, 2),
    total_orders INTEGER,
    total_revenue DECIMAL(15, 2),
    avg_rating DECIMAL(2, 1),
    last_updated DATE,
    FOREIGN KEY (store_id) REFERENCES micro_store_profile(store_id)
);

CREATE TABLE IF NOT EXISTS micro_customer_segments (
    id SERIAL PRIMARY KEY,
    store_id VARCHAR(50) NOT NULL,
    segment_name VARCHAR(100), -- e.g., 'loyal_20s_female'
    age_group VARCHAR(20),
    gender VARCHAR(10),
    visit_frequency VARCHAR(20), -- 'daily', 'weekly', 'monthly'
    avg_spending DECIMAL(10, 2),
    customer_count INTEGER,
    churn_rate DECIMAL(5, 2), -- percentage
    last_visit_avg_days INTEGER, -- days since last visit
    retention_score DECIMAL(3, 2), -- 0.00 to 1.00
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES micro_store_profile(store_id)
);

-- ============================================
-- USER PROFILE DATA
-- ============================================

CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    store_id VARCHAR(50),
    
    -- Demographic
    age INTEGER,
    location VARCHAR(100),
    business_type VARCHAR(100),
    experience_years INTEGER,
    
    -- Personality
    risk_preference VARCHAR(20), -- 'conservative', 'moderate', 'aggressive'
    experience_level VARCHAR(20), -- 'beginner', 'intermediate', 'expert'
    
    -- Social
    sns_usage TEXT[], -- ['instagram', 'facebook', 'kakao']
    marketing_capability VARCHAR(20), -- 'low', 'medium', 'high'
    
    -- Strategy Preferences
    profile_strategy VARCHAR(50), -- 'hand-crafted', 'llm-generated', 'dataset-aligned'
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES micro_store_profile(store_id)
);

-- ============================================
-- INDEXES for Performance
-- ============================================

CREATE INDEX idx_district_trends_code ON macro_district_trends(district_code);
CREATE INDEX idx_population_flow_district ON macro_population_flow(district_code, date);
CREATE INDEX idx_competitor_district ON meso_competitor_info(district_code);
CREATE INDEX idx_sales_store_date ON micro_sales_data(store_id, sale_date);
CREATE INDEX idx_customer_segments_store ON micro_customer_segments(store_id);
CREATE INDEX idx_user_profile_store ON user_profiles(store_id);

-- ============================================
-- SAMPLE DATA for Testing
-- ============================================

-- Insert sample district
INSERT INTO macro_district_trends (district_code, district_name, year_quarter, status, total_stores, total_sales, avg_sales_per_store, population_flow)
VALUES ('SD_001', '강남역', '2024Q1', 'dynamic', 1250, 50000000000, 40000000, 150000)
ON CONFLICT (district_code, year_quarter) DO NOTHING;

-- Insert sample store profile
INSERT INTO micro_store_profile (store_id, store_name, business_type, district_code, opening_date)
VALUES ('STORE_001', '테스트 카페', 'cafe', 'SD_001', '2023-01-15')
ON CONFLICT (store_id) DO NOTHING;

-- Insert sample user profile
INSERT INTO user_profiles (user_id, store_id, age, location, business_type, experience_years, risk_preference, experience_level, sns_usage, marketing_capability, profile_strategy)
VALUES ('USER_001', 'STORE_001', 35, '강남구', 'cafe', 2, 'moderate', 'intermediate', ARRAY['instagram', 'kakao'], 'medium', 'llm-generated')
ON CONFLICT (user_id) DO NOTHING;

