## Purpose
Short, actionable guidance for AI coding agents working on this repository: a monero-mining deployment that bundles XMRig (the miner), a Monero daemon, and P2Pool glue scripts.

Be brief and specific: point to exact files to change, concrete commands to run, and the minimal reproducer for common tasks (build, run, debug, smoke-test).

## Big-picture architecture
- Top-level orchestrator: shell scripts in the repo root (`setup.sh`, `start-mining.sh`, `monitor.sh`, `stop-mining.sh`). They install deps, build components and launch services.
- Miner: `xmrig/` — full XMRig source (CMake-based). Key source directories: `xmrig/src` (App.cpp, xmrig.cpp, core/, crypto/, backend/), `xmrig/src/3rdparty/` for vendored libs.
- Blockchain node: `monero/` contains Monero CLI tools (monerod, wallet tools). The scripts launch `monerod` locally.
- Pool: `p2pool/` contains a local pool instance; XMRig connects to P2Pool (or external pool) via stratum.

Data flow: monerod (local node, ZMQ on 127.0.0.1:18083) ↔ p2pool (web UI 3380, stratum 3333) ← XMRig (connects to pool; provides HTTP API on 127.0.0.1:8080).

## Where to look (quick links)
- Build & orchestration scripts: `/setup.sh`, `/start-mining.sh`, `/monitor.sh`, `/stop-mining.sh`
- XMRig build & source: `/xmrig/`, particularly `xmrig/CMakeLists.txt`, `xmrig/scripts/`, and `xmrig/src/`.
- Config used at runtime: `/config.json` (root) — XMRig is launched with `--config=~/monero-mining/config.json` in scripts.
- Useful READMEs: `/README.md`, `/xmrig/README.md`, `/monero/README.md`, `/p2pool/README.md` — these have contextual and build info.

## Build / run / debug commands (concrete)
- Build XMRig (from repo root):
  - cd xmrig && mkdir -p build && cd build
  - cmake .. -DWITH_HWLOC=ON
  - make -j$(nproc)
- Quick run (foreground):
  - Start monerod: `./monero/monerod --zmq-pub tcp://127.0.0.1:18083 --disable-dns-checkpoints ...`
  - Start xmrig: `./xmrig/build/xmrig --config=$HOME/monero-mining/config.json`
- Background (repo uses screen sessions):
  - `screen -dmS monerod bash -c "cd ~/monero-mining/monero && ./monerod ..."`
  - `screen -dmS xmrig bash -c "cd ~/monero-mining/xmrig/build && ./xmrig --config=~/monero-mining/config.json"`
- Smoke test (verify miner API):
  - `curl -s http://127.0.0.1:8080/1/summary | grep -oP '"hashrate":\{"total":\[\K[^]]+'`
- Debug build (reproduce crashes / attach gdb):
  - `cmake .. -DCMAKE_BUILD_TYPE=Debug && make -j1`
  - run `gdb --args ./xmrig --config=...`

## Project-specific conventions & gotchas
- Build artifacts live in `xmrig/build/` — source edits happen in `xmrig/src/` and CMake reconfigure is required when adding files.
- Scripts expect `config.json` in repository root; editing that file changes runtime behavior (pool, wallet, threads, huge pages). Keep changes local or in branches to avoid accidental wallet changes.
- The deployment uses `screen` sessions named `xmrig`, `monerod`, and `p2pool` by convention — don't change session names without updating the scripts.
- HugePages and system tuning is commonly used (see README); scripts do not auto-apply hugepage settings.
- Donation level: XMRig defaults to 1% donate in source/config; look in `xmrig/src/version.h` and `config.json` if changing.

## Integration points and external dependencies
- Monerod binary in `/monero/` — scripts rely on that binary and ZMQ port `18083` for P2Pool/XMRig integration.
- P2Pool in `/p2pool/` — stratum port `3333`, web UI port `3380` (see start scripts).
- XMRig HTTP API: default `127.0.0.1:8080` provides runtime stats and is the preferred programmatic interface for health checks.
- Third-party libraries exist under `xmrig/src/3rdparty/` — prefer CMake options and provided `scripts/` for building dependencies.

## Small, reproducible tasks for agents
- To add a new miner flag or change default threads:
  1. Edit `config.json` (root) for runtime default.
  2. Edit `xmrig/src/*` only if adding new CLI/API behavior; update `CMakeLists.txt` if adding files.
  3. Build in `xmrig/build/` and run smoke test (API check above).
- To debug a crash in the miner, produce a Debug build and run under gdb as shown above. Capture stack traces and point to exact lines in `xmrig/src/`.

## What NOT to do
- Do not commit built binaries from `xmrig/build/`.
- Avoid changing the wallet address in `README.md` or `config.json` unless explicitly asked — this is a user-specific secret in this repo.

## Where to ask follow-ups
- If unclear about runtime behavior, check `start-mining.sh` and `monitor.sh` — they demonstrate the exact sequence the deployment expects.
- When in doubt about algorithm implementations, inspect `xmrig/src/crypto/` (e.g., `ghostrider/`) and its README.

If any part is unclear or you'd like more automation (systemd units, CI steps, or tests), tell me which area to expand and I will iterate.
