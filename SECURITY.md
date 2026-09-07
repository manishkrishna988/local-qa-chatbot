# Security

This project is configured for local use. Do not expose Ollama's unauthenticated API to the internet. Before public hosting, follow `docs/DEPLOYMENT.md` and add authentication and server-side inference quotas.

Do not commit `.env`, credentials or conversation exports. Report vulnerabilities privately through GitHub's security advisory feature if enabled; do not include secrets in a public issue.

The assistant generates text only; it does not execute generated code or call tools. Review any generated commands before running them yourself.
