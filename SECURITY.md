# Security policy

Do not open a public Issue containing credentials, database exports, private URLs, or exploit details. Contact the repository owner privately and rotate any exposed credential immediately.

Secrets must be stored in GitHub Actions Secrets or protected Environments. Production workflows must use least privilege and must not expose secrets to untrusted pull requests.

When reporting a vulnerability, include the affected path, impact, safe reproduction steps, and recommended containment. Never include the secret value itself.
