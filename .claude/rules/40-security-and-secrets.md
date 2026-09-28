# Security and secrets

- Secrets belong only in GitHub Actions Secrets or protected Environments.
- Never commit `.env`, database dumps, private keys, API tokens, FTP credentials, WordPress passwords, cookies, or unredacted logs.
- Before push, scan changed content for credentials, bearer tokens, private keys, connection strings, and large database exports.
- Use least-privilege workflow `permissions`; default to `contents: read`.
- Do not execute untrusted PR code with production secrets. Avoid `pull_request_target` for build/test execution.
- Parameterize SQL where runtime input is involved; generated SQL must escape values and stay marker-scoped.
- Validate archive paths and filenames; reject path traversal and unexpected executable content.
- If exposure is suspected: stop, revoke/rotate first, then remove from history and document the incident without repeating the secret.
