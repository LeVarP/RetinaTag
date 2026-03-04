# Contributing & Development Workflow

## Environments

| Environment | URL | Data dir | Purpose |
|---|---|---|---|
| **prod** | http://localhost | `./data/` | Stable, always running |
| **stage** | http://localhost:8080 | `./data-stage/` | Preview changes before merging |

Both environments use the same OCT images (`OCT_DATA_PATH`) in read-only mode.
Each has its own database and cache under its data directory.

### .env keys

```env
OCT_DATA_PATH=/path/to/oct-images
JWT_SECRET_KEY=<prod key>
JWT_SECRET_KEY_STAGE=<stage key>
```

Generate keys with: `openssl rand -hex 32`

### Managing environments

```bash
make prod-up        # start prod
make prod-down      # stop prod
make prod-rebuild   # rebuild and restart prod (run after merging to main)

make stage-up       # start stage
make stage-down     # stop stage
make stage-build    # rebuild stage from current branch
```

---

## Development Workflow

### 1. Create a branch

Never commit directly to `main`. Always start from a feature branch:

```bash
git checkout main && git pull
git checkout -b feature/my-feature
```

### 2. Develop and preview on stage

While developing, test your changes on the stage environment:

```bash
make stage-build   # rebuilds stage containers from your current branch
# open http://localhost:8080
```

Prod stays untouched on port 80 the entire time.

### 3. Merge to main

When the feature is ready and verified on stage:

```bash
git checkout main
git merge feature/my-feature
git push
```

### 4. Rebuild prod

After merging, rebuild prod to pick up the changes:

```bash
make prod-rebuild
```

> **Important:** prod is never rebuilt automatically. It always requires an explicit `make prod-rebuild`.
