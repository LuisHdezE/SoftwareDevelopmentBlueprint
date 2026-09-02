# Infrastructure Runbooks

Operational procedures in this directory are intended to make Blueprint-compatible development and CI infrastructure reproducible.

Current runbooks:

- [`SELF_HOSTED_WSL_RUNNER_BOOTSTRAP.md`](SELF_HOSTED_WSL_RUNNER_BOOTSTRAP.md): rebuild a Windows + WSL2 host for isolated self-hosted GitHub Actions runners, Docker Engine, local-development services, and ephemeral CI service containers.

Runbooks must not contain secrets, runner registration tokens, personal credentials, or machine-specific data that is not required for reproducibility.
