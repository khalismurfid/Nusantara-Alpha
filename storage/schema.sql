PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS model_catalogue (
    model_id TEXT NOT NULL,
    model_version TEXT NOT NULL,
    model_name TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    model_origin TEXT NOT NULL,
    public_demo_eligible INTEGER NOT NULL DEFAULT 0,
    supported_universe_id TEXT NOT NULL,
    evaluation_period_start TEXT NOT NULL,
    evaluation_period_end TEXT NOT NULL,
    evidence_available INTEGER NOT NULL DEFAULT 0,
    evidence_load_status TEXT NOT NULL,
    limitations_json TEXT NOT NULL DEFAULT '[]',
    mlflow_run_id TEXT,
    mlflow_model_uri TEXT,
    sqlite_catalogue_revision TEXT,
    mlflow_registry_revision TEXT,
    registry_sync_status TEXT NOT NULL DEFAULT 'incomplete',
    registry_conflict_reason TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (model_id, model_version)
);

CREATE TABLE IF NOT EXISTS model_evidence (
    evidence_id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    model_version TEXT NOT NULL,
    evidence_type TEXT NOT NULL,
    evaluation_period_start TEXT NOT NULL,
    evaluation_period_end TEXT NOT NULL,
    key_metrics_json TEXT NOT NULL DEFAULT '[]',
    performance_summary TEXT NOT NULL,
    supported_universe_json TEXT NOT NULL DEFAULT '[]',
    known_limitations_json TEXT NOT NULL DEFAULT '[]',
    data_quality_notes_json TEXT NOT NULL DEFAULT '[]',
    historical_performance_caveat TEXT NOT NULL,
    evidence_status TEXT NOT NULL,
    evidence_load_status TEXT NOT NULL,
    evidence_as_of TEXT NOT NULL,
    data_source_mode TEXT NOT NULL,
    barrier_config_json TEXT NOT NULL DEFAULT '{}',
    paper_trading_summary TEXT,
    FOREIGN KEY (model_id, model_version) REFERENCES model_catalogue(model_id, model_version)
);

CREATE TABLE IF NOT EXISTS supported_stocks (
    ticker TEXT NOT NULL,
    name TEXT NOT NULL,
    exchange TEXT NOT NULL DEFAULT 'IDX',
    universe_id TEXT NOT NULL,
    support_status TEXT NOT NULL,
    unavailable_reason TEXT,
    data_as_of TEXT,
    freshness_status TEXT,
    market_data_flags_json TEXT NOT NULL DEFAULT '[]',
    PRIMARY KEY (ticker, universe_id)
);

CREATE TABLE IF NOT EXISTS data_availability (
    model_id TEXT NOT NULL,
    ticker TEXT NOT NULL,
    required_period_start TEXT,
    required_period_end TEXT,
    data_as_of TEXT,
    feature_generation_timestamp TEXT,
    freshness_status TEXT NOT NULL,
    chronology_status TEXT NOT NULL,
    quality_flags_json TEXT NOT NULL DEFAULT '[]',
    blocking_reason TEXT,
    PRIMARY KEY (model_id, ticker)
);

CREATE TABLE IF NOT EXISTS disclaimers (
    disclaimer_id TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    text TEXT NOT NULL,
    placement TEXT NOT NULL,
    effective_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prediction_logs (
    log_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    prediction_id TEXT,
    model_id TEXT NOT NULL,
    model_version TEXT NOT NULL,
    tickers_json TEXT NOT NULL,
    data_as_of_timestamp TEXT,
    feature_generation_timestamp TEXT,
    prediction_timestamp TEXT NOT NULL,
    prediction_output_json TEXT,
    confidence TEXT,
    disclaimer_version TEXT,
    status TEXT NOT NULL,
    error_message TEXT,
    runtime_context TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS unsupported_stock_interest (
    ticker TEXT NOT NULL,
    model_id TEXT,
    reason TEXT NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    PRIMARY KEY (ticker, model_id, reason)
);

CREATE TABLE IF NOT EXISTS registry_conflicts (
    conflict_id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    model_version TEXT NOT NULL,
    conflict_type TEXT NOT NULL,
    sqlite_value TEXT,
    mlflow_value TEXT,
    detected_at TEXT NOT NULL,
    resolution_status TEXT NOT NULL,
    user_message TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS deployable_data_assets (
    asset_id TEXT PRIMARY KEY,
    asset_type TEXT NOT NULL,
    classification TEXT NOT NULL,
    data_as_of TEXT,
    limitations TEXT NOT NULL,
    approval_reference TEXT
);

CREATE TABLE IF NOT EXISTS idx_universe (
    ticker TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    yahoo_symbol TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    source TEXT NOT NULL,
    source_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS market_prices (
    ticker TEXT NOT NULL,
    price_date TEXT NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    adj_close REAL,
    volume REAL NOT NULL,
    source TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    PRIMARY KEY (ticker, price_date)
);

CREATE TABLE IF NOT EXISTS model_feature_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    model_version TEXT NOT NULL,
    ticker TEXT NOT NULL,
    feature_date TEXT NOT NULL,
    feature_generation_timestamp TEXT NOT NULL,
    features_json TEXT NOT NULL,
    feature_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);
