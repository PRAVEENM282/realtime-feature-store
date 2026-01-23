CREATE TABLE IF NOT EXISTS user_features (
    user_id VARCHAR(255) PRIMARY KEY,
    feature_a JSONB,
    feature_b INTEGER,
    last_updated_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
