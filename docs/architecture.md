# Architecture

Nusantara Alpha uses a small Python monorepo with explicit boundaries:

- `app_streamlit/`: customer-facing presentation only;
- `backend/`: API routes, request/response schemas, and service orchestration;
- `ml/`: feature generation, model loading, prediction, chronology validation,
  and market-data validation;
- `storage/`: SQLite schema, database helpers, repositories, and safe seed data;
- `model_registry/`: MLflow metadata access, catalogue synchronization,
  approval decisions, and conflict logging;
- `deployment/`: container and Oracle Cloud Free Tier deployment notes.

The request flow is:

1. Streamlit requests model, evidence, stock, demo status, or prediction data
   from the FastAPI service.
2. FastAPI route handlers delegate to services and do not contain core ML
   logic.
3. Services validate model approval, evidence, stock support, data availability,
   chronology, feature timestamps, public-demo gates, and copy/disclaimer rules.
4. ML modules generate timestamped features and model signals outside the UI and
   route handlers.
5. SQLite records catalogue metadata, evidence metadata, data availability,
   registry conflicts, unsupported-stock interest, and prediction logs.

This structure keeps UI, API, model logic, validation, storage, registry, and
documentation separate while remaining small enough for a portfolio product.

