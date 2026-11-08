# Docker instructions

Launch with `docker compose up --build -d` in this directory, then use http://127.0.0.1:8081 through 8085. Every page has a single **Run** button for normal and gadget payloads. Full commands are in [payloads.md](payloads.md).

Logs: `docker compose logs --tail=100 php` (replace `php` with desired service).
Rebuild: `docker compose build --no-cache php`; then `docker compose up -d`.
Stop: `docker compose down`.

For Linux, Docker containers cannot open the Windows host calculator; use stdout or `/tmp/cc6-proof` as evidence. Published ports bind only `127.0.0.1`.
