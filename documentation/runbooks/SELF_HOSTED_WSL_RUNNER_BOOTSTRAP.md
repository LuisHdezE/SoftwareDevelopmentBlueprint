# Self-Hosted WSL Runner Bootstrap Runbook

Status: DRAFT / 0.5.3-dev hardening support

## Purpose

This runbook defines a reproducible way to rebuild the Windows + WSL2 host used for Blueprint-compatible self-hosted GitHub Actions runners. It is intended for a fresh PC, a Windows reinstall, a WSL rebuild, or recovery after storage failure.

The design deliberately separates:

- the Windows host;
- the WSL distributions;
- GitHub Actions runners;
- Docker Engine and cached container images;
- local-development database/cache services;
- ephemeral CI service containers.

A runner does not own a database or cache installation. CI services are job-scoped and ephemeral. Shared Docker image cache is allowed; shared mutable CI service instances are not.

## Target layout

Recommended Windows storage layout:

```text
G:\WSL\
├── Ubuntu-24.04-MAIN\
└── Ubuntu-24.04-VALIDATION\
```

Recommended WSL MAIN layout:

```text
/home/<user>/
├── actions-runners/
│   └── cusa-digital/
│       └── actions-runner/
└── actions-runner-efactura/
    └── actions-runner/
```

Do not place runner workspaces manually under Windows-mounted paths such as `/mnt/c`. Keep runner `_work` directories on the native Linux filesystem and let GitHub Actions manage them.

## 1. Preflight on Windows

Open PowerShell as Administrator.

Verify available disks and choose a healthy destination with enough free space:

```powershell
Get-Disk |
Select-Object Number,FriendlyName,SerialNumber,BusType,HealthStatus,OperationalStatus,
@{N='SizeGB';E={[math]::Round($_.Size/1GB,1)}} |
Format-Table -AutoSize

Get-Volume |
Where-Object DriveLetter |
Select-Object DriveLetter,FileSystemLabel,
@{N='SizeGB';E={[math]::Round($_.Size/1GB,1)}},
@{N='FreeGB';E={[math]::Round($_.SizeRemaining/1GB,1)}} |
Format-Table -AutoSize
```

If rebuilding after storage faults, check the Windows System event log before selecting the destination:

```powershell
Get-WinEvent -FilterHashtable @{
  LogName='System'
  StartTime=(Get-Date).AddHours(-24)
} -ErrorAction SilentlyContinue |
Where-Object {
  $_.ProviderName -match 'disk|stor|ntfs|volmgr|vhd|hyper-v' -or
  $_.Message -match 'disk|I/O|storage|VHD|bloque defectuoso|bad block'
} |
Select-Object -First 100 TimeCreated,ProviderName,Id,LevelDisplayName,Message |
Format-List
```

Do not install WSL on a disk that is producing current storage errors.

## 2. Install or update WSL

```powershell
wsl --update
wsl --status
```

Create the destination root:

```powershell
New-Item -ItemType Directory -Force 'G:\WSL' | Out-Null
```

Install the primary distribution directly on the selected disk:

```powershell
wsl --install `
  --distribution Ubuntu-24.04 `
  --name Ubuntu-24.04 `
  --location 'G:\WSL\Ubuntu-24.04-MAIN' `
  --web-download `
  --no-launch
```

Install the isolated validation distribution:

```powershell
wsl --install `
  --distribution Ubuntu-24.04 `
  --name Ubuntu-24.04-VALIDATION `
  --location 'G:\WSL\Ubuntu-24.04-VALIDATION' `
  --web-download `
  --no-launch
```

Verify:

```powershell
wsl --list --verbose
```

Expected conceptual result:

```text
Ubuntu-24.04               Stopped   2
Ubuntu-24.04-VALIDATION    Stopped   2
```

## 3. First boot and Linux user

Launch MAIN:

```powershell
wsl -d Ubuntu-24.04
```

Create the normal Linux user requested by Ubuntu first-run setup. The canonical examples below use `<user>` as a placeholder.

Confirm identity and native Linux home:

```bash
whoami
pwd
findmnt -T "$HOME"
```

The home directory should resolve to the Linux ext4 filesystem, not `/mnt/c`, `/mnt/g`, or another Windows-mounted filesystem.

## 4. Enable systemd

Inside Ubuntu MAIN:

```bash
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Exit Ubuntu, then from PowerShell:

```powershell
wsl --shutdown
wsl -d Ubuntu-24.04
```

Verify:

```bash
systemctl is-system-running || true
systemctl --version
```

## 5. Base operating-system packages

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt install -y \
  ca-certificates \
  curl \
  git \
  jq \
  unzip \
  zip \
  gnupg \
  lsb-release \
  software-properties-common \
  build-essential
```

Record baseline versions:

```bash
uname -a
git --version
curl --version
```

## 6. Docker Engine

Install Docker Engine using Docker's supported Ubuntu repository for the current Ubuntu release. Do not rely on an ad-hoc desktop-managed daemon for the canonical self-hosted runner profile unless the runtime profile explicitly says so.

After installation:

```bash
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Log out and back in, then verify:

```bash
docker version
docker info
docker run --rm hello-world
```

The host may cache approved images such as:

```text
mysql:8.4
postgres:16
redis:<controlled-pinned-version>
```

Do not use `latest` for canonical CI service images.

## 7. Local-development services are not CI services

Local development may use native services when explicitly required by the project, for example MySQL or PostgreSQL. These are separate from CI service containers.

Rules:

1. Local-development databases/caches may be persistent.
2. CI databases/caches must be job-scoped ephemeral service containers when `runner.service_containers=true`.
3. CI workflows must not depend on a fixed host port such as `3306:3306`.
4. CI workflows consume the dynamically assigned service port from the GitHub Actions service context.
5. Docker image cache may be shared across jobs; live mutable database/cache containers may not be shared across jobs.

Canonical GitHub Actions pattern:

```yaml
services:
  mysql:
    image: mysql:8.4
    ports:
      - 3306
```

Runtime port binding example:

```yaml
- name: Bind dynamic MySQL service port
  run: echo "DB_PORT=${{ job.services.mysql.ports[3306] }}" >> "$GITHUB_ENV"
```

Equivalent container ports:

```text
MySQL      3306
PostgreSQL 5432
Redis      6379
```

## 8. GitHub Actions runner directories

Create separate runner installations. Do not share one runner installation between independently governed projects.

```bash
mkdir -p "$HOME/actions-runners/cusa-digital/actions-runner"
mkdir -p "$HOME/actions-runner-efactura/actions-runner"
```

Recommended logical identities:

```text
CUSA
  runner name: cusa-digital-wsl
  labels: self-hosted,linux,x64,blueprint
  installation: /home/<user>/actions-runners/cusa-digital/actions-runner

Electronic invoicing
  runner name: efactura-ci-01
  labels: self-hosted,linux,x64,efactura-ci
  installation: /home/<user>/actions-runner-efactura/actions-runner
```

Runner registration tokens are ephemeral credentials. Never store them in this repository, a shell history intended for sharing, or a committed configuration file.

Download the current GitHub Actions runner release for Linux x64 from the GitHub repository's runner setup instructions at provisioning time. Do not hard-code an obsolete runner release in this runbook.

Register each runner from its own installation directory using the repository-specific URL and a newly generated registration token.

Conceptual example:

```bash
./config.sh \
  --url https://github.com/<owner>/<repo> \
  --token '<EPHEMERAL_REGISTRATION_TOKEN>' \
  --name '<RUNNER_NAME>' \
  --labels '<LABEL1>,<LABEL2>,<LABEL3>' \
  --work '_work' \
  --unattended
```

## 9. Runner lifecycle

The current architecture distinguishes two operational modes.

### CUSA transient runner

The CUSA runner may be started as a transient systemd unit when explicitly needed. Its runtime must remain isolated from eFactura and must not commandeer eFactura's runner directory, service, labels, or workspace.

### eFactura persistent runner

The eFactura runner is maintained as its own persistent service and must not be restarted, stopped, reconfigured, or have its workspace modified as a side effect of CUSA maintenance.

When recreating systemd units, preserve this isolation explicitly.

## 10. Workspace safety

Never manually develop inside a runner `_work` directory.

Never use runner `_work` as a long-lived project clone.

Before destructive cleanup, verify that no `Runner.Worker`, `actions/checkout`, `git clean`, `git fetch`, or project process is using the workspace.

Useful read-only diagnostic:

```bash
ps -eo pid,ppid,etime,stat,args \
  | grep -E 'Runner.Worker|git-remote-https|git (fetch|clean|reset|checkout|config)' \
  | grep -v grep || true
```

A `git clean` process stuck in Linux state `D` with a kernel wait such as `wait_on_buffer` is an I/O/storage problem until proven otherwise. Do not repeatedly kill/retry it or launch additional jobs while storage errors are active.

## 11. Validation distribution

`Ubuntu-24.04-VALIDATION` exists to test bootstrap, infrastructure, or Blueprint changes independently of MAIN.

It must not silently become the production runner host. It should be safe to destroy and recreate.

Use it for operations such as:

- validating WSL bootstrap changes;
- testing Docker/runner installation procedures;
- testing infrastructure scripts before applying them to MAIN;
- verifying recovery procedures.

## 12. Minimum post-build verification

From PowerShell:

```powershell
wsl --list --verbose
```

Inside MAIN:

```bash
id
findmnt -T "$HOME"
systemctl is-active docker
docker version
git --version
```

Check runner processes only after runner installation:

```bash
pgrep -af 'Runner.Listener|Runner.Worker' || true
```

Check listening ports and distinguish local-development services from CI containers:

```bash
ss -lntp || true
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}'
```

In GitHub, verify runner names and labels before enabling workflows.

## 13. Rebuild checklist after a PC/Windows reinstall

```text
[ ] Select healthy destination disk
[ ] Install/update WSL
[ ] Create MAIN distribution on target disk
[ ] Create VALIDATION distribution on target disk
[ ] Create normal Linux user
[ ] Enable systemd
[ ] Apply Ubuntu updates
[ ] Install base tooling
[ ] Install and verify Docker Engine
[ ] Install project-required local-development services only
[ ] Recreate CUSA runner installation and labels
[ ] Recreate eFactura runner installation and labels
[ ] Restore only non-secret infrastructure configuration
[ ] Verify runner isolation
[ ] Verify Docker image cache capability
[ ] Verify CI uses ephemeral service containers and dynamic host ports
[ ] Verify no workflow depends on native host MySQL/PostgreSQL/Redis
[ ] Run repository CI validation
[ ] Keep VALIDATION disposable
```

## 14. Storage failure rule

If Windows reports current disk errors, CRC failures, bad blocks, or WSL reports repeated virtual-storage I/O failures:

1. stop launching new CI jobs;
2. verify whether any protected runner has active work;
3. avoid repeated full-disk reads and retry storms;
4. move/rebuild WSL on known-good storage when the distributions are disposable;
5. prefer rebuild over data recovery when the WSL instances contain no unique data;
6. only repair or retire the failed disk after the runtime has been evacuated.

The runner host is reproducible infrastructure. Source code and canonical configuration live in version control; the WSL VM itself must not become the only copy of anything important.

## 15. Canonical principle

A healthy Blueprint-compatible self-hosted runner host should be reconstructible from documentation plus repository configuration. Losing a WSL distribution should cost setup time, not source code, project state, credentials, or irreplaceable operational knowledge.
