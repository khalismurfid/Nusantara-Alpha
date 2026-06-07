# Linux VPS Public Demo Deployment

Preferred target: an Oracle Cloud Always Free compute instance or another
low-cost Linux server such as a Tencent Cloud Lighthouse Ubuntu instance.

1. Provision an Ubuntu 22.04 LTS or 24.04 LTS server.
2. Install Docker and Docker Compose.
3. Clone the repository.
4. Create `.local/` in the repository root on the server.
5. Copy only real approved runtime files into `.local/`:
   - `nusantara_alpha.sqlite3`
   - `mlflow_tracking.sqlite`
   - `model_artifacts/`
6. Review `deployment/env.example`; it is configured for `public_demo` by
   default.
7. Mount or copy only real approved model artifacts and approved non-sensitive
   data. Do not deploy private datasets, credentials, proprietary files,
   restricted source data, or unrestricted internal artifacts.
8. Run the public-demo release gate through `/demo/status`.
9. If the gate is degraded, keep prediction unavailable and show the degraded
   demo limitations.
10. Validate the prediction-first public demo behavior:
   - A supported ticker shows the prediction as the primary content only when
     public prediction gates pass.
   - Degraded mode shows `Demo mode: predictions unavailable` and does not
     claim full prediction availability.
   - The screen keeps model evidence and traceability available as secondary
     review context.
   - Mock models and dummy prediction outputs are not shown as public
     predictions.
11. Start the stack from the repository root:

```bash
docker compose -f deployment/compose.yaml --env-file deployment/env.example up --build -d
```

Expose only SSH and the Streamlit demo port publicly:

- `22` for SSH
- `8501` for the public demo UI

The backend API is bound to `127.0.0.1:8000` on the server and is intended for
internal Streamlit-to-FastAPI traffic only. High availability, autoscaling, paid
production deployment, brokerage integration, and live trading operations are
out of scope.
