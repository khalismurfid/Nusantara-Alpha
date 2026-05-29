# Oracle Cloud Free Tier Deployment

Preferred target: an Oracle Cloud Always Free compute instance or another
low-cost Linux server.

1. Provision an Always Free compute instance.
2. Install Docker and Docker Compose.
3. Clone the repository.
4. Create a server-local environment file from `deployment/env.example`.
5. Set `NUSANTARA_RUNTIME_CONTEXT=public_demo`.
6. Mount or copy only real approved model artifacts and approved non-sensitive
   data. Do not deploy private datasets, credentials, proprietary files,
   restricted source data, or unrestricted internal artifacts.
7. Run the public-demo release gate through `/demo/status`.
8. If the gate is degraded, keep prediction unavailable and show the degraded
   demo limitations.
9. Start the stack:

```bash
docker compose -f deployment/compose.yaml --env-file deployment/env.example up --build -d
```

Expose only the required HTTP ports. High availability, autoscaling, paid
production deployment, brokerage integration, and live trading operations are
out of scope.

