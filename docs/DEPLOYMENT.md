# Hosted deployment guide

## Recommended first deployment

Use a Linux VM with Docker Engine and Compose. Start with a private demo reachable over an SSH tunnel; choose memory, storage and CPU/GPU capacity by measuring your model rather than assuming a universal minimum.

1. Clone the GitHub repository on the VM and check out a reviewed commit.
2. Run `docker compose up --build -d` from the repository.
3. Check `docker compose logs model-pull` and `docker compose ps`. Model initialization must complete before the app starts.
4. From your laptop run `ssh -L 8501:127.0.0.1:8501 USER@SERVER`.
5. Open `http://localhost:8501` on your laptop.

The supplied Compose file keeps Streamlit on loopback and Ollama within Docker's network. Keep inbound ports 8501 and 11434 closed at the server firewall. Only allow SSH from approved sources.

## Before making a public demo

Place an authenticated reverse proxy on the host in front of `127.0.0.1:8501`. Configure a domain, HTTPS, WebSocket forwarding (Streamlit needs it), authentication and appropriate connection timeouts. Only expose 443 and any certificate-validation port required by your proxy. Preserve Streamlit's CORS and XSRF protections.

The starter intentionally does not configure a public proxy: domain, identity provider, traffic policy and hosting provider are deployment-specific. Streamlit Community Cloud would need a separately reachable, secured inference backend; its localhost is not your laptop.

A proxy request limit alone does not bound prompts sent through a long-lived WebSocket. For untrusted users, implement server-enforced per-user inference quotas and concurrency limits before allowing access. Session-only throttling can be bypassed by opening another session.

## Operations and release process

- Run CI and a real model smoke test before release. CI's fake model tests do not assess model quality or prove inference works.
- Record the code commit, Ollama image digest and model digest from `ollama list`. Model and container tags can change; pin digests for repeatable releases.
- Build an immutable application image in CI, scan dependencies/images and review findings before pushing it to your registry. The current workflow validates the image but does not publish it.
- Monitor container health, memory, disk, inference latency and failure counts without retaining chat text. The Streamlit health endpoint only checks the web process; separately verify real model readiness with a short inference.
- The app sets a 120-second HTTP timeout; for streaming this is not a guaranteed total wall-clock request deadline. Add cancellation and an enforced total deadline for production workloads.
- Load-test your intended concurrency. The supplied configuration is a single-host CPU demo, without autoscaling or high availability.
- Roll back by checking out the previous reviewed commit, restoring its image/model versions and rebuilding with `docker compose up --build -d`. Preserve the model volume.
- Review dependency updates and repeat tests. Back up any future persistent application data; this version has none.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| App does not start | Docker is running; inspect model-pull logs for download failures |
| Cannot complete answer | Model exists and Ollama is healthy; inspect `docker compose logs ollama` |
| Slow answers | Model download is complete; reduce model size or use supported GPU configuration |
| Port already in use | Free local port 8501 or change the host side of the Compose port mapping |
| Native app cannot connect | Run `ollama serve` if needed; check `OLLAMA_BASE_URL` |

GPU support is not enabled by default. Follow [Ollama's official Docker guide](https://docs.ollama.com/docker) for your hardware and driver setup.
