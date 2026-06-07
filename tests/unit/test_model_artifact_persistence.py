from ml.backtesting.realistic import fit_pooled_logistic_model, load_pooled_model, predict_scores, save_pooled_model
from storage.seed_local_demo import BASELINE_MODEL_ID, BASELINE_UNIVERSE_ID, _sample_market_prices, refresh_baseline_artifact


def test_baseline_logistic_model_can_be_saved_and_loaded(tmp_path):
    rows = _sample_market_prices([("BBCA", "Bank Central Asia Tbk"), ("TLKM", "Telkom Indonesia Tbk"), ("ASII", "Astra International Tbk")])
    model = fit_pooled_logistic_model(rows)
    path = tmp_path / "model.joblib"

    save_pooled_model(model, path)
    loaded = load_pooled_model(path)
    scores = predict_scores(loaded)

    assert path.exists()
    assert {"BBCA", "TLKM", "ASII"} == set(scores["ticker"])
    assert set(scores["model_signal"]).issubset({"up", "down", "neutral"})


def test_baseline_logistic_model_can_train_on_expanded_approved_universe():
    rows = _sample_market_prices(
        [
            ("BBCA", "Bank Central Asia Tbk"),
            ("TLKM", "Telkom Indonesia Tbk"),
            ("ASII", "Astra International Tbk"),
            ("BBRI", "Bank Rakyat Indonesia Persero Tbk"),
            ("BMRI", "Bank Mandiri Persero Tbk"),
        ]
    )

    model = fit_pooled_logistic_model(rows)
    scores = predict_scores(model)

    assert {"BBCA", "TLKM", "ASII", "BBRI", "BMRI"} == set(scores["ticker"])
    assert model.training_rows > 0


def test_baseline_artifact_refresh_uses_supported_tickers_only(seeded_repo, tmp_path):
    seeded_repo.upsert_stock(
        {
            "ticker": "WBSA",
            "name": "PT BSA Logistics Indonesia Tbk",
            "exchange": "IDX",
            "universe_id": BASELINE_UNIVERSE_ID,
            "support_status": "temporarily_unavailable",
            "unavailable_reason": "Insufficient history.",
            "data_as_of": "2026-05-29T00:00:00+00:00",
            "freshness_status": "missing",
            "market_data_flags": ["insufficient_history"],
        }
    )
    seeded_repo.upsert_market_prices(_sample_market_prices([("WBSA", "PT BSA Logistics Indonesia Tbk")]))

    model = refresh_baseline_artifact(seeded_repo, tmp_path / "model.joblib")

    assert "WBSA" not in model.trained_tickers
    assert set(model.trained_tickers) == {"BBCA", "TLKM", "ASII"}
