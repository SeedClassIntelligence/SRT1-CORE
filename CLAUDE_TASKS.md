# SRT-1 Platform Finalization Instructions for Claude

**ATTENTION CLAUDE:** You are tasked with finalizing the production-ready deployment of the SRT-1 codebase. Do not diverge or hallucinate architecture. Strictly abide by the rules below to finish the platform.

## Rule 1: The Terminal Timeout Bug
You are operating in an environment where Windows PowerShell commands (like `run_command` or running `http.server`) will sporadically hang indefinitely and block execution. 
* **DO NOT** use terminal commands for general file operations, tree traversal, or string replacement. 
* **ONLY** use native filesystem API tools to read/write/delete files.

## Rule 2: Follow the Canonical Architecture
The root directory has been cleaned of confusing duplicates, but you must respect the explicit boundaries:
* **Production Live Dashboard:** `srt1_dashboard.html` (Served natively by the engine on Port 7483).
* **Static Sales/Marketing Funnel:** The `seed-reflection/` folder (Includes `home.html`, `comparison.html`, etc.).
* **Canonical Build Map:** Read `BUILD.md` in the root folder for the definitive structure. Ignore deprecated files.

---

## 🎯 Primary Objectives to Finish the Platform

### Phase 1: Wire Up the Admin Dashboard
* **Current State:** The admin interface features (or admin portal) currently rely on hardcoded "Demo Mode" mock parameters.
* **Task:** Wire the Admin Dashboard to the live API endpoints (e.g., `GET /admin/stats`). Ensure real-time state overrides the dummy data, just as we did with the Seed Farm in `srt1_dashboard.html`.

### Phase 2: Finalize the PWA Install Pipeline
* **Current State:** `srt1_mobile.html`, `manifest.json`, and `sw.js` exist for Progressive Web App (PWA) deployment as a differentiator.
* **Task:** Validate the Service Worker caching logic and ensure the mobile install-flow prompt correctly triggers when users access the dashboard from an external device.

### Phase 3: Integrate Activity Logs
* **Current State:** There is an Activity Log concept documented in our earlier workflow that still depends on hardcoded entries.
* **Task:** Verify the appropriate live endpoint (e.g., `GET /activity`) inside the engine and plug it into the respective interface, removing mock placeholders.

### Phase 4: Trust-Chain Validation & Licensing 
* **Current State:** The UI frequently flags the Trust Status as "UNVERIFIED".
* **Task:** Investigate the `srt1_remote_auth.py` and `srt1_tracing_system.py` logic to fully generate the first successful node license token. Turn the UNVERIFIED badge into a verified green state based on true system telemetry.

## Execution Requirements
1. Start by executing your `view_file` tool on `BUILD.md` and `srt1_code_indexer_engine.py` to get situated.
2. Attack one Phase at a time.
3. Once completed, package the final engine deployment.
