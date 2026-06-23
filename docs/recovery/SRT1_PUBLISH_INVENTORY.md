# SRT-1 Publish Inventory

Recovery root: `C:\Users\SEEDN\Downloads\SRT1 CODING`

Generated during Phase 2: Publish Inventory. No files were moved, deleted, staged, or committed as part of this inventory.

Bucket definitions:
- `PUBLIC CORE / PUSH`: Safe candidate for public SRT1-CORE after normal review.
- `PRIVATE / ENTERPRISE`: Must not be pushed to public Core as implementation.
- `GENERATED / LOCAL IGNORE`: Runtime, generated, local, cache, scratch output, backup, nested checkout, or local artifact.
- `REVIEW BEFORE DECISION`: Could be public contract/stub/docs or useful shell, but needs founder review before staging.

## Inventory

| Path | Git status | Bucket | Reason | Recommended action |
|---|---:|---|---|---|
| `.cursorrules` | modified | REVIEW BEFORE DECISION | No automatic safe classification; human review required before staging. | review |
| `AGENTS.md` | modified | REVIEW BEFORE DECISION | Canonical docs/instructions shape public Core boundary and may mention private systems. | review |
| `BUILD.md` | modified | REVIEW BEFORE DECISION | Canonical docs/instructions shape public Core boundary and may mention private systems. | review |
| `CLAUDE.md` | modified | REVIEW BEFORE DECISION | Canonical docs/instructions shape public Core boundary and may mention private systems. | review |
| `CTO_HANDOVER_TO_CLAUDE.md` | deleted | REVIEW BEFORE DECISION | Deleted tracked architecture/enforcement document; deletion needs human confirmation. | review |
| `PRODUCT_ARCHITECTURE.md` | deleted | REVIEW BEFORE DECISION | Deleted tracked architecture/enforcement document; deletion needs human confirmation. | review |
| `README.md` | modified | REVIEW BEFORE DECISION | Canonical docs/instructions shape public Core boundary and may mention private systems. | review |
| `SRT1_ENFORCEMENT_MODE.md` | deleted | REVIEW BEFORE DECISION | Deleted tracked architecture/enforcement document; deletion needs human confirmation. | review |
| `START_SRT1.bat` | modified | PUBLIC CORE / PUSH | Local Core launcher helper. | push |
| `developer-pwa/assets/style.css` | modified | PUBLIC CORE / PUSH | Public local dashboard/PWA shell asset or Core page. | push |
| `developer-pwa/auth.html` | modified | REVIEW BEFORE DECISION | PWA shell should remain available in Core, but page may mention Enterprise, SION, auth, or Seed Signature. | review |
| `developer-pwa/comparison.html` | modified | PUBLIC CORE / PUSH | Public local dashboard/PWA shell asset or Core page. | push |
| `developer-pwa/contact.html` | modified | REVIEW BEFORE DECISION | PWA shell should remain available in Core, but page may mention Enterprise, SION, auth, or Seed Signature. | review |
| `developer-pwa/dashboard.html` | modified | REVIEW BEFORE DECISION | PWA shell should remain available in Core, but page may mention Enterprise, SION, auth, or Seed Signature. | review |
| `developer-pwa/documentation.html` | modified | REVIEW BEFORE DECISION | PWA shell should remain available in Core, but page may mention Enterprise, SION, auth, or Seed Signature. | review |
| `developer-pwa/index.html` | modified | PUBLIC CORE / PUSH | Public local dashboard/PWA shell asset or Core page. | push |
| `developer-pwa/js/platform.js` | modified | PUBLIC CORE / PUSH | Public local dashboard/PWA shell asset or Core page. | push |
| `developer-pwa/manifest.json` | modified | PUBLIC CORE / PUSH | Public local dashboard/PWA shell asset or Core page. | push |
| `developer-pwa/mobile.html` | modified | REVIEW BEFORE DECISION | PWA shell should remain available in Core, but page may mention Enterprise, SION, auth, or Seed Signature. | review |
| `developer-pwa/sw.js` | modified | PUBLIC CORE / PUSH | Public local dashboard/PWA shell asset or Core page. | push |
| `developer-pwa/templates/compare-table.html` | modified | PUBLIC CORE / PUSH | Public local dashboard/PWA shell asset or Core page. | push |
| `developer-pwa/templates/footer.html` | modified | PUBLIC CORE / PUSH | Public local dashboard/PWA shell asset or Core page. | push |
| `developer-pwa/templates/nav-header.html` | modified | PUBLIC CORE / PUSH | Public local dashboard/PWA shell asset or Core page. | push |
| `developer-pwa/workspace-demo.html` | modified | PUBLIC CORE / PUSH | Public local dashboard/PWA shell asset or Core page. | push |
| `packages/scia_memory/requirements.txt` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_memory/scia_memory/__init__.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_memory/scia_memory/frame_persistence.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_memory/scia_memory/memory_system.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_memory/scia_memory/memory_system_v2.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_memory/scia_memory/orchestrator_api.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_memory/scia_memory/reflex_memory.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_memory/scia_memory/reflex_memory_redis.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_memory/scia_memory/regenerative_memory.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_memory/setup.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_security/requirements.txt` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_security/scia_security/__init__.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_security/scia_security/audit_log.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_security/scia_security/db_utils.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_security/scia_security/encryption.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_security/scia_security/execution_graph.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_security/scia_security/integrity.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_security/scia_security/signing_client.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `packages/scia_security/setup.py` | deleted | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `srt1_code_indexer/engine.py` | modified | REVIEW BEFORE DECISION | Core engine authority; review for private imports, signing hooks, or Enterprise execution coupling. | review |
| `srt1_code_indexer/indexer.py` | modified | PUBLIC CORE / PUSH | Core public indexer, manifest, or parser capability. | push |
| `srt1_platform/__init__.py` | modified | REVIEW BEFORE DECISION | Platform file may be public hook/stub or private Enterprise coupling; must fail closed if private backend is unavailable. | review |
| `srt1_platform/execution_bridge.py` | modified | REVIEW BEFORE DECISION | Platform file may be public hook/stub or private Enterprise coupling; must fail closed if private backend is unavailable. | review |
| `srt1_platform/pwa/assets/style.css` | modified | PUBLIC CORE / PUSH | Packaged public PWA shell/helper for local Core. | push |
| `srt1_platform/pwa/dashboard.html` | modified | REVIEW BEFORE DECISION | Packaged PWA file may mention Enterprise, SION, Seed Signature, memory, security, auth, or pricing. | review |
| `srt1_platform/pwa/js/platform.js` | modified | PUBLIC CORE / PUSH | Packaged public PWA shell/helper for local Core. | push |
| `srt1_platform/pwa/manifest.json` | modified | PUBLIC CORE / PUSH | Packaged public PWA shell/helper for local Core. | push |
| `srt1_platform/pwa/mobile.html` | modified | REVIEW BEFORE DECISION | Packaged PWA file may mention Enterprise, SION, Seed Signature, memory, security, auth, or pricing. | review |
| `srt1_platform/pwa/sw.js` | modified | PUBLIC CORE / PUSH | Packaged public PWA shell/helper for local Core. | push |
| `srt1_platform/tracing_system.py` | modified | REVIEW BEFORE DECISION | No automatic safe classification; human review required before staging. | review |
| `srt1_pro/__init__.py` | modified | REVIEW BEFORE DECISION | Pro package surface/self-heal must remain advisory and not autonomous Enterprise remediation. | review |
| `srt1_pro/context_bundler.py` | modified | PUBLIC CORE / PUSH | Public Core/Pro context or workspace-manifest capability. | push |
| `srt1_pro/self_heal.py` | modified | REVIEW BEFORE DECISION | Pro package surface/self-heal must remain advisory and not autonomous Enterprise remediation. | review |
| `srt1_pro/workspace_connector.py` | modified | PUBLIC CORE / PUSH | Public Core/Pro context or workspace-manifest capability. | push |
| `Install-SRT1.ps1` | untracked | REVIEW BEFORE DECISION | Installer may reference private Enterprise path or distribution flow. | review |
| `PHASE_AB_WALKTHROUGH.md` | untracked | REVIEW BEFORE DECISION | Phase walkthrough may contain Enterprise/SION process history; sanitize or archive before publish. | review |
| `PHASE_C_WALKTHROUGH.md` | untracked | REVIEW BEFORE DECISION | Phase walkthrough may contain Enterprise/SION process history; sanitize or archive before publish. | review |
| `PHASE_D_WALKTHROUGH.md` | untracked | REVIEW BEFORE DECISION | Phase walkthrough may contain Enterprise/SION process history; sanitize or archive before publish. | review |
| `PHASE_E_WALKTHROUGH.md` | untracked | REVIEW BEFORE DECISION | Phase walkthrough may contain Enterprise/SION process history; sanitize or archive before publish. | review |
| `PHASE_F2_WALKTHROUGH.md` | untracked | REVIEW BEFORE DECISION | Phase walkthrough may contain Enterprise/SION process history; sanitize or archive before publish. | review |
| `PHASE_F_WALKTHROUGH.md` | untracked | REVIEW BEFORE DECISION | Phase walkthrough may contain Enterprise/SION process history; sanitize or archive before publish. | review |
| `SRT1_CONSTITUTION.md` | untracked | REVIEW BEFORE DECISION | Canonical docs/instructions shape public Core boundary and may mention private systems. | review |
| `SRT1_CONTEXT_INDEX.md` | untracked | REVIEW BEFORE DECISION | Canonical docs/instructions shape public Core boundary and may mention private systems. | review |
| `SRT1_CURRENT_STATE.md` | untracked | REVIEW BEFORE DECISION | Canonical docs/instructions shape public Core boundary and may mention private systems. | review |
| `SRT1_DECISIONS.md` | untracked | REVIEW BEFORE DECISION | Canonical docs/instructions shape public Core boundary and may mention private systems. | review |
| `SRT1_FRONTIER.md` | untracked | REVIEW BEFORE DECISION | Canonical docs/instructions shape public Core boundary and may mention private systems. | review |
| `SRT1_Marketing_DevExperience.webp` | untracked | REVIEW BEFORE DECISION | Marketing/reference asset may be public, but needs founder review for private UI/data/IP. | review |
| `debug.log` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | ignore |
| `developer-pwa/Install-SRT1.ps1` | untracked | REVIEW BEFORE DECISION | PWA shell should remain available in Core, but page may mention Enterprise, SION, auth, or Seed Signature. | review |
| `developer-pwa/constellation.html` | untracked | REVIEW BEFORE DECISION | PWA shell should remain available in Core, but page may mention Enterprise, SION, auth, or Seed Signature. | review |
| `developer-pwa/health.html` | untracked | REVIEW BEFORE DECISION | PWA shell should remain available in Core, but page may mention Enterprise, SION, auth, or Seed Signature. | review |
| `developer-pwa/observatory.html` | untracked | PUBLIC CORE / PUSH | Public local dashboard/PWA shell asset or Core page. | push |
| `developer-pwa/srt1-core.html` | untracked | PUBLIC CORE / PUSH | Public local dashboard/PWA shell asset or Core page. | push |
| `docs/SRT1_Code_Indexer_Complete_Reference.docx` | untracked | REVIEW BEFORE DECISION | Marketing/reference asset may be public, but needs founder review for private UI/data/IP. | review |
| `docs/SRT1_ENTERPRISE_ARCHITECTURE.md` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `docs/marketing/SRT1_60_SECOND_HOOK.md` | untracked | REVIEW BEFORE DECISION | Marketing/reference asset may be public, but needs founder review for private UI/data/IP. | review |
| `docs/marketing/SRT1_Dashboard_Promo.webp` | untracked | REVIEW BEFORE DECISION | Marketing/reference asset may be public, but needs founder review for private UI/data/IP. | review |
| `docs/marketing/SRT1_MANIFESTO_VIDEO.md` | untracked | REVIEW BEFORE DECISION | Marketing/reference asset may be public, but needs founder review for private UI/data/IP. | review |
| `docs/marketing/SRT1_Screenshot_Video_Script.md` | untracked | REVIEW BEFORE DECISION | Marketing/reference asset may be public, but needs founder review for private UI/data/IP. | review |
| `docs/marketing/SRT1_Social_Media_Posts.md` | untracked | REVIEW BEFORE DECISION | Marketing/reference asset may be public, but needs founder review for private UI/data/IP. | review |
| `docs/marketing/SRT1_Video_Production_Brief.md` | untracked | REVIEW BEFORE DECISION | Marketing/reference asset may be public, but needs founder review for private UI/data/IP. | review |
| `docs/marketing/SRT1_Walkthrough_Script.md` | untracked | REVIEW BEFORE DECISION | Marketing/reference asset may be public, but needs founder review for private UI/data/IP. | review |
| `docs/marketing/screenshots/Slide2_Landing_Page.png` | untracked | REVIEW BEFORE DECISION | Marketing/reference asset may be public, but needs founder review for private UI/data/IP. | review |
| `docs/marketing/screenshots/Slide3_Dashboard_Stats.png` | untracked | REVIEW BEFORE DECISION | Marketing/reference asset may be public, but needs founder review for private UI/data/IP. | review |
| `docs/marketing/screenshots/Slide4_Risk_Profile_Violations.png` | untracked | REVIEW BEFORE DECISION | Marketing/reference asset may be public, but needs founder review for private UI/data/IP. | review |
| `docs/marketing/screenshots/Slide5_Seed_Farm_Timeline.png` | untracked | REVIEW BEFORE DECISION | Marketing/reference asset may be public, but needs founder review for private UI/data/IP. | review |
| `memory/frame_persistence.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `memory/memory_system.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `memory/orchestrator_api.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `memory/reflex_memory.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `memory/regenerative_memory.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `pytest_output.txt` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | ignore |
| `scia_memory/requirements.txt` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/__init__.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/frame_persistence.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/memory_system.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/memory_system_v2.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/orchestrator_api.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/reflex_memory.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/reflex_memory_redis.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/regenerative_memory.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/requirements.txt` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/scia_memory/__init__.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/scia_memory/frame_persistence.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/scia_memory/memory_system.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/scia_memory/memory_system_v2.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/scia_memory/orchestrator_api.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/scia_memory/reflex_memory.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/scia_memory/reflex_memory_redis.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/scia_memory/regenerative_memory.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_memory/setup.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_security/requirements.txt` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_security/scia_security/__init__.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_security/scia_security/execution_graph.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_security/scia_security/integrity.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/scia_security/setup.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_memory/setup.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_security/requirements.txt` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_security/scia_security/__init__.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_security/scia_security/execution_graph.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_security/scia_security/integrity.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_security/scia_security/seed_signature.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_security/scia_security/signing_client.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_security/setup.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scia_ui_system_skill_v_1.md` | untracked | REVIEW BEFORE DECISION | UI/design skill may be public documentation or internal method. | review |
| `scratch.html` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | archive |
| `scratch/adversarial_audit_suite.py` | untracked | REVIEW BEFORE DECISION | Scratch test/helper may be useful but should be promoted, archived, or kept private intentionally. | review |
| `scratch/check_packages.py` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | archive |
| `scratch/check_status.py` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | archive |
| `scratch/check_syntax.js` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | archive |
| `scratch/find_enterprise.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scratch/live_blackbox_validation.py` | untracked | REVIEW BEFORE DECISION | Scratch test/helper may be useful but should be promoted, archived, or kept private intentionally. | review |
| `scratch/live_probe.py` | untracked | REVIEW BEFORE DECISION | Scratch test/helper may be useful but should be promoted, archived, or kept private intentionally. | review |
| `scratch/overhaul_dashboard.py` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | archive |
| `scratch/patch_ports.py` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | archive |
| `scratch/patch_ports_to_8475.py` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | archive |
| `scratch/print_stats.py` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | archive |
| `scratch/reorder.py` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | archive |
| `scratch/reorder_enterprise.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scratch/run_auditor_live.py` | untracked | REVIEW BEFORE DECISION | Scratch test/helper may be useful but should be promoted, archived, or kept private intentionally. | review |
| `scratch/run_enterprise.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scratch/search_history.py` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | archive |
| `scratch/start_all.py` | untracked | REVIEW BEFORE DECISION | Scratch test/helper may be useful but should be promoted, archived, or kept private intentionally. | review |
| `scratch/sync_dashboard.py` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | archive |
| `scratch/test_adversarial_governance.py` | untracked | REVIEW BEFORE DECISION | Scratch test/helper may be useful but should be promoted, archived, or kept private intentionally. | review |
| `scratch/test_consistency_auditor.py` | untracked | REVIEW BEFORE DECISION | Scratch test/helper may be useful but should be promoted, archived, or kept private intentionally. | review |
| `scratch/test_core_boundary.py` | untracked | PUBLIC CORE / PUSH | Core boundary/no-mutation verification test candidate. | push |
| `scratch/test_enrichment_boundary.py` | untracked | PUBLIC CORE / PUSH | Core boundary/no-mutation verification test candidate. | push |
| `scratch/test_live_endpoint.py` | untracked | REVIEW BEFORE DECISION | Scratch test/helper may be useful but should be promoted, archived, or kept private intentionally. | review |
| `scratch/test_operational_registry.py` | untracked | REVIEW BEFORE DECISION | Scratch test/helper may be useful but should be promoted, archived, or kept private intentionally. | review |
| `scratch/test_phase_d_dashboard.py` | untracked | REVIEW BEFORE DECISION | Scratch test/helper may be useful but should be promoted, archived, or kept private intentionally. | review |
| `scratch/test_phase_e_sion_visibility.py` | untracked | PRIVATE / ENTERPRISE | Private memory/security/signing/Enterprise implementation or Enterprise-specific process must not ship in public Core. | keep private |
| `scratch/test_phase_f_stabilization.py` | untracked | REVIEW BEFORE DECISION | Scratch test/helper may be useful but should be promoted, archived, or kept private intentionally. | review |
| `scratch/verify_services.py` | untracked | REVIEW BEFORE DECISION | Scratch test/helper may be useful but should be promoted, archived, or kept private intentionally. | review |
| `srt1-contracts/SRT1_OPERATING_MAP.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/contracts/audit_event_contract.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/contracts/change_proposal_contract.md` | untracked | PUBLIC CORE / PUSH | Public interface contract for Core proposal, context, or sandbox behavior. | push |
| `srt1-contracts/contracts/context_injection_contract.md` | untracked | PUBLIC CORE / PUSH | Public interface contract for Core proposal, context, or sandbox behavior. | push |
| `srt1-contracts/contracts/execution_lease_contract.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/contracts/filecell_contract.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/contracts/post_execution_verification_contract.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/contracts/repo_sandbox_contract.md` | untracked | PUBLIC CORE / PUSH | Public interface contract for Core proposal, context, or sandbox behavior. | push |
| `srt1-contracts/srt1-skills/ast-analysis/SKILL.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/ast-analysis/activation.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/ast-analysis/events.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/ast-analysis/verification.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/audit-event-emission/SKILL.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/audit-event-emission/activation.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/audit-event-emission/events.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/audit-event-emission/verification.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/constellation-mapping/SKILL.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/constellation-mapping/activation.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/constellation-mapping/events.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/constellation-mapping/verification.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/context-injection/SKILL.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/context-injection/activation.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/context-injection/events.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/context-injection/verification.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/drift-detection/SKILL.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/drift-detection/activation.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/drift-detection/events.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/drift-detection/verification.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/filecell-manifest-derivation/SKILL.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/filecell-manifest-derivation/activation.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/filecell-manifest-derivation/events.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/filecell-manifest-derivation/verification.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/module-boundary-protection/SKILL.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/module-boundary-protection/activation.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/module-boundary-protection/events.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/module-boundary-protection/verification.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/post-execution-verification/SKILL.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/post-execution-verification/activation.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/post-execution-verification/events.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/post-execution-verification/verification.md` | untracked | REVIEW BEFORE DECISION | Public contract candidate, but audit/FileCell/execution/post-execution boundary needs founder review. | review |
| `srt1-contracts/srt1-skills/repo-indexing/SKILL.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/repo-indexing/activation.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/repo-indexing/events.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-contracts/srt1-skills/repo-indexing/verification.md` | untracked | PUBLIC CORE / PUSH | Public Core skill contract for AST, context, drift, boundary, or repo indexing. | push |
| `srt1-skills/ast-analysis/SKILL.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/ast-analysis/activation.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/ast-analysis/events.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/ast-analysis/governance.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/ast-analysis/inputs_outputs.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/ast-analysis/verification.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/audit-event-emission/SKILL.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/audit-event-emission/activation.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/audit-event-emission/events.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/audit-event-emission/governance.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/audit-event-emission/inputs_outputs.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/audit-event-emission/verification.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/constellation-mapping/SKILL.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/constellation-mapping/activation.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/constellation-mapping/events.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/constellation-mapping/governance.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/constellation-mapping/inputs_outputs.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/constellation-mapping/verification.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/context-injection/SKILL.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/context-injection/activation.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/context-injection/events.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/context-injection/governance.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/context-injection/inputs_outputs.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/context-injection/verification.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/drift-detection/SKILL.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/drift-detection/activation.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/drift-detection/events.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/drift-detection/governance.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/drift-detection/inputs_outputs.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/drift-detection/verification.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/filecell-manifest-derivation/SKILL.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/filecell-manifest-derivation/activation.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/filecell-manifest-derivation/events.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/filecell-manifest-derivation/governance.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/filecell-manifest-derivation/inputs_outputs.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/filecell-manifest-derivation/verification.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/module-boundary-protection/SKILL.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/module-boundary-protection/activation.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/module-boundary-protection/events.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/module-boundary-protection/governance.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/module-boundary-protection/inputs_outputs.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/module-boundary-protection/verification.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/post-execution-verification/SKILL.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/post-execution-verification/activation.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/post-execution-verification/events.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/post-execution-verification/governance.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/post-execution-verification/inputs_outputs.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/post-execution-verification/verification.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/repo-indexing/SKILL.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/repo-indexing/activation.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/repo-indexing/events.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/repo-indexing/governance.md` | untracked | REVIEW BEFORE DECISION | Skill documentation may mention governance, audit, FileCell, or post-execution authority. | review |
| `srt1-skills/repo-indexing/inputs_outputs.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1-skills/repo-indexing/verification.md` | untracked | PUBLIC CORE / PUSH | Public Core skill documentation. | push |
| `srt1.bat` | untracked | PUBLIC CORE / PUSH | Local Core launcher helper. | push |
| `srt1_audit_delta.json` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | ignore |
| `srt1_code_indexer/engine.py.bak` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | ignore |
| `srt1_code_indexer/language_parsers.py` | untracked | PUBLIC CORE / PUSH | Core public indexer, manifest, or parser capability. | push |
| `srt1_platform/audit_ledger.py` | untracked | REVIEW BEFORE DECISION | Platform file may be public hook/stub or private Enterprise coupling; must fail closed if private backend is unavailable. | review |
| `srt1_platform/change_proposal.py` | untracked | REVIEW BEFORE DECISION | No automatic safe classification; human review required before staging. | review |
| `srt1_platform/consistency_auditor.py` | untracked | PUBLIC CORE / PUSH | Read-only Core intelligence, consistency, doctrine, or taxonomy capability. | push |
| `srt1_platform/doctrine_scanner.py` | untracked | PUBLIC CORE / PUSH | Read-only Core intelligence, consistency, doctrine, or taxonomy capability. | push |
| `srt1_platform/execution_lease.py` | untracked | REVIEW BEFORE DECISION | Platform file may be public hook/stub or private Enterprise coupling; must fail closed if private backend is unavailable. | review |
| `srt1_platform/filecell.py` | untracked | REVIEW BEFORE DECISION | Platform file may be public hook/stub or private Enterprise coupling; must fail closed if private backend is unavailable. | review |
| `srt1_platform/governance_monitor.py` | untracked | REVIEW BEFORE DECISION | Platform file may be public hook/stub or private Enterprise coupling; must fail closed if private backend is unavailable. | review |
| `srt1_platform/intelligence_adapter.py` | untracked | PUBLIC CORE / PUSH | Read-only Core intelligence, consistency, doctrine, or taxonomy capability. | push |
| `srt1_platform/llm_adapter.py` | untracked | REVIEW BEFORE DECISION | Platform file may be public hook/stub or private Enterprise coupling; must fail closed if private backend is unavailable. | review |
| `srt1_platform/llm_providers.py` | untracked | REVIEW BEFORE DECISION | Platform file may be public hook/stub or private Enterprise coupling; must fail closed if private backend is unavailable. | review |
| `srt1_platform/manifest_deriver.py` | untracked | REVIEW BEFORE DECISION | Platform file may be public hook/stub or private Enterprise coupling; must fail closed if private backend is unavailable. | review |
| `srt1_platform/operational_registry.py` | untracked | REVIEW BEFORE DECISION | Platform file may be public hook/stub or private Enterprise coupling; must fail closed if private backend is unavailable. | review |
| `srt1_platform/pwa/Install-SRT1.ps1` | untracked | REVIEW BEFORE DECISION | Packaged PWA file may mention Enterprise, SION, Seed Signature, memory, security, auth, or pricing. | review |
| `srt1_platform/pwa/api/extract_seeds.py` | untracked | PUBLIC CORE / PUSH | Packaged public PWA shell/helper for local Core. | push |
| `srt1_platform/pwa/api/parse_export.py` | untracked | PUBLIC CORE / PUSH | Packaged public PWA shell/helper for local Core. | push |
| `srt1_platform/pwa/api/platform.js` | untracked | PUBLIC CORE / PUSH | Packaged public PWA shell/helper for local Core. | push |
| `srt1_platform/pwa/auth.html` | untracked | REVIEW BEFORE DECISION | Packaged PWA file may mention Enterprise, SION, Seed Signature, memory, security, auth, or pricing. | review |
| `srt1_platform/pwa/comparison.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA shell/helper for local Core. | push |
| `srt1_platform/pwa/constellation.html` | untracked | REVIEW BEFORE DECISION | Packaged PWA file may mention Enterprise, SION, Seed Signature, memory, security, auth, or pricing. | review |
| `srt1_platform/pwa/contact.html` | untracked | REVIEW BEFORE DECISION | Packaged PWA file may mention Enterprise, SION, Seed Signature, memory, security, auth, or pricing. | review |
| `srt1_platform/pwa/documentation.html` | untracked | REVIEW BEFORE DECISION | Packaged PWA file may mention Enterprise, SION, Seed Signature, memory, security, auth, or pricing. | review |
| `srt1_platform/pwa/health.html` | untracked | REVIEW BEFORE DECISION | Packaged PWA file may mention Enterprise, SION, Seed Signature, memory, security, auth, or pricing. | review |
| `srt1_platform/pwa/index.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA shell/helper for local Core. | push |
| `srt1_platform/pwa/observatory.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA shell/helper for local Core. | push |
| `srt1_platform/pwa/srt1-core.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA shell/helper for local Core. | push |
| `srt1_platform/pwa/templates/compare-table.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA template for local Core shell. | push |
| `srt1_platform/pwa/templates/dashboard-architecture.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA template for local Core shell. | push |
| `srt1_platform/pwa/templates/dashboard-enforcement.html` | untracked | REVIEW BEFORE DECISION | Packaged PWA file may mention Enterprise, SION, Seed Signature, memory, security, auth, or pricing. | review |
| `srt1_platform/pwa/templates/dashboard-sidebar.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA template for local Core shell. | push |
| `srt1_platform/pwa/templates/dashboard-telemetry.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA template for local Core shell. | push |
| `srt1_platform/pwa/templates/doc-content.html` | untracked | REVIEW BEFORE DECISION | Packaged PWA file may mention Enterprise, SION, Seed Signature, memory, security, auth, or pricing. | review |
| `srt1_platform/pwa/templates/doc-sidebar.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA template for local Core shell. | push |
| `srt1_platform/pwa/templates/footer.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA template for local Core shell. | push |
| `srt1_platform/pwa/templates/home-hero.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA template for local Core shell. | push |
| `srt1_platform/pwa/templates/home-pricing.html` | untracked | REVIEW BEFORE DECISION | Packaged PWA file may mention Enterprise, SION, Seed Signature, memory, security, auth, or pricing. | review |
| `srt1_platform/pwa/templates/home-stats.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA template for local Core shell. | push |
| `srt1_platform/pwa/templates/nav-header.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA template for local Core shell. | push |
| `srt1_platform/pwa/templates/sandbox-concept-grid.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA template for local Core shell. | push |
| `srt1_platform/pwa/templates/sandbox-terminal.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA template for local Core shell. | push |
| `srt1_platform/pwa/workspace-demo.html` | untracked | PUBLIC CORE / PUSH | Packaged public PWA shell/helper for local Core. | push |
| `srt1_platform/taxonomy_validator.py` | untracked | PUBLIC CORE / PUSH | Read-only Core intelligence, consistency, doctrine, or taxonomy capability. | push |
| `srt1_platform/verification.py` | untracked | REVIEW BEFORE DECISION | Platform file may be public hook/stub or private Enterprise coupling; must fail closed if private backend is unavailable. | review |
| `unknown_to_ast.py` | untracked | GENERATED / LOCAL IGNORE | Runtime output, scratch helper, backup, test output, or local artifact. | archive |

## Files Safe To Stage Now

These are low-risk public Core candidates, not approval to stage. They should still receive a quick sanity read before staging:

- `developer-pwa/assets/style.css`
- `developer-pwa/comparison.html`
- `developer-pwa/index.html`
- `developer-pwa/js/platform.js`
- `developer-pwa/manifest.json`
- `developer-pwa/observatory.html`
- `developer-pwa/srt1-core.html`
- `developer-pwa/sw.js`
- `developer-pwa/templates/compare-table.html`
- `developer-pwa/templates/footer.html`
- `developer-pwa/templates/nav-header.html`
- `developer-pwa/workspace-demo.html`
- `scratch/test_core_boundary.py`
- `scratch/test_enrichment_boundary.py`
- `srt1.bat`
- `srt1_code_indexer/indexer.py`
- `srt1_code_indexer/language_parsers.py`
- `srt1_platform/consistency_auditor.py`
- `srt1_platform/doctrine_scanner.py`
- `srt1_platform/intelligence_adapter.py`
- `srt1_platform/pwa/api/extract_seeds.py`
- `srt1_platform/pwa/api/parse_export.py`
- `srt1_platform/pwa/api/platform.js`
- `srt1_platform/pwa/assets/style.css`
- `srt1_platform/pwa/comparison.html`
- `srt1_platform/pwa/index.html`
- `srt1_platform/pwa/js/platform.js`
- `srt1_platform/pwa/manifest.json`
- `srt1_platform/pwa/observatory.html`
- `srt1_platform/pwa/srt1-core.html`
- `srt1_platform/pwa/sw.js`
- `srt1_platform/pwa/templates/compare-table.html`
- `srt1_platform/pwa/templates/dashboard-architecture.html`
- `srt1_platform/pwa/templates/dashboard-sidebar.html`
- `srt1_platform/pwa/templates/dashboard-telemetry.html`
- `srt1_platform/pwa/templates/doc-sidebar.html`
- `srt1_platform/pwa/templates/footer.html`
- `srt1_platform/pwa/templates/home-hero.html`
- `srt1_platform/pwa/templates/home-stats.html`
- `srt1_platform/pwa/templates/nav-header.html`
- `srt1_platform/pwa/templates/sandbox-concept-grid.html`
- `srt1_platform/pwa/templates/sandbox-terminal.html`
- `srt1_platform/pwa/workspace-demo.html`
- `srt1_platform/taxonomy_validator.py`
- `srt1_pro/context_bundler.py`
- `srt1_pro/workspace_connector.py`
- `srt1-contracts/contracts/change_proposal_contract.md`
- `srt1-contracts/contracts/context_injection_contract.md`
- `srt1-contracts/contracts/repo_sandbox_contract.md`
- `srt1-contracts/srt1-skills/ast-analysis/activation.md`
- `srt1-contracts/srt1-skills/ast-analysis/events.md`
- `srt1-contracts/srt1-skills/ast-analysis/SKILL.md`
- `srt1-contracts/srt1-skills/ast-analysis/verification.md`
- `srt1-contracts/srt1-skills/context-injection/activation.md`
- `srt1-contracts/srt1-skills/context-injection/events.md`
- `srt1-contracts/srt1-skills/context-injection/SKILL.md`
- `srt1-contracts/srt1-skills/context-injection/verification.md`
- `srt1-contracts/srt1-skills/drift-detection/activation.md`
- `srt1-contracts/srt1-skills/drift-detection/events.md`
- `srt1-contracts/srt1-skills/drift-detection/SKILL.md`
- `srt1-contracts/srt1-skills/drift-detection/verification.md`
- `srt1-contracts/srt1-skills/module-boundary-protection/activation.md`
- `srt1-contracts/srt1-skills/module-boundary-protection/events.md`
- `srt1-contracts/srt1-skills/module-boundary-protection/SKILL.md`
- `srt1-contracts/srt1-skills/module-boundary-protection/verification.md`
- `srt1-contracts/srt1-skills/repo-indexing/activation.md`
- `srt1-contracts/srt1-skills/repo-indexing/events.md`
- `srt1-contracts/srt1-skills/repo-indexing/SKILL.md`
- `srt1-contracts/srt1-skills/repo-indexing/verification.md`
- `srt1-skills/ast-analysis/activation.md`
- `srt1-skills/ast-analysis/events.md`
- `srt1-skills/ast-analysis/inputs_outputs.md`
- `srt1-skills/ast-analysis/SKILL.md`
- `srt1-skills/ast-analysis/verification.md`
- `srt1-skills/context-injection/activation.md`
- `srt1-skills/context-injection/events.md`
- `srt1-skills/context-injection/inputs_outputs.md`
- `srt1-skills/context-injection/SKILL.md`
- `srt1-skills/context-injection/verification.md`
- `srt1-skills/drift-detection/activation.md`
- `srt1-skills/drift-detection/events.md`
- `srt1-skills/drift-detection/inputs_outputs.md`
- `srt1-skills/drift-detection/SKILL.md`
- `srt1-skills/drift-detection/verification.md`
- `srt1-skills/module-boundary-protection/activation.md`
- `srt1-skills/module-boundary-protection/events.md`
- `srt1-skills/module-boundary-protection/inputs_outputs.md`
- `srt1-skills/module-boundary-protection/SKILL.md`
- `srt1-skills/module-boundary-protection/verification.md`
- `srt1-skills/repo-indexing/activation.md`
- `srt1-skills/repo-indexing/events.md`
- `srt1-skills/repo-indexing/inputs_outputs.md`
- `srt1-skills/repo-indexing/SKILL.md`
- `srt1-skills/repo-indexing/verification.md`
- `START_SRT1.bat`

## Files That Must Remain Private

- `docs/SRT1_ENTERPRISE_ARCHITECTURE.md`
- `memory/frame_persistence.py`
- `memory/memory_system.py`
- `memory/orchestrator_api.py`
- `memory/reflex_memory.py`
- `memory/regenerative_memory.py`
- `packages/scia_memory/requirements.txt`
- `packages/scia_memory/scia_memory/__init__.py`
- `packages/scia_memory/scia_memory/frame_persistence.py`
- `packages/scia_memory/scia_memory/memory_system.py`
- `packages/scia_memory/scia_memory/memory_system_v2.py`
- `packages/scia_memory/scia_memory/orchestrator_api.py`
- `packages/scia_memory/scia_memory/reflex_memory.py`
- `packages/scia_memory/scia_memory/reflex_memory_redis.py`
- `packages/scia_memory/scia_memory/regenerative_memory.py`
- `packages/scia_memory/setup.py`
- `packages/scia_security/requirements.txt`
- `packages/scia_security/scia_security/__init__.py`
- `packages/scia_security/scia_security/audit_log.py`
- `packages/scia_security/scia_security/db_utils.py`
- `packages/scia_security/scia_security/encryption.py`
- `packages/scia_security/scia_security/execution_graph.py`
- `packages/scia_security/scia_security/integrity.py`
- `packages/scia_security/scia_security/signing_client.py`
- `packages/scia_security/setup.py`
- `scia_memory/requirements.txt`
- `scia_memory/scia_memory/__init__.py`
- `scia_memory/scia_memory/frame_persistence.py`
- `scia_memory/scia_memory/memory_system.py`
- `scia_memory/scia_memory/memory_system_v2.py`
- `scia_memory/scia_memory/orchestrator_api.py`
- `scia_memory/scia_memory/reflex_memory.py`
- `scia_memory/scia_memory/reflex_memory_redis.py`
- `scia_memory/scia_memory/regenerative_memory.py`
- `scia_memory/scia_memory/requirements.txt`
- `scia_memory/scia_memory/scia_memory/__init__.py`
- `scia_memory/scia_memory/scia_memory/frame_persistence.py`
- `scia_memory/scia_memory/scia_memory/memory_system.py`
- `scia_memory/scia_memory/scia_memory/memory_system_v2.py`
- `scia_memory/scia_memory/scia_memory/orchestrator_api.py`
- `scia_memory/scia_memory/scia_memory/reflex_memory.py`
- `scia_memory/scia_memory/scia_memory/reflex_memory_redis.py`
- `scia_memory/scia_memory/scia_memory/regenerative_memory.py`
- `scia_memory/scia_memory/setup.py`
- `scia_memory/scia_security/requirements.txt`
- `scia_memory/scia_security/scia_security/__init__.py`
- `scia_memory/scia_security/scia_security/execution_graph.py`
- `scia_memory/scia_security/scia_security/integrity.py`
- `scia_memory/scia_security/setup.py`
- `scia_memory/setup.py`
- `scia_security/requirements.txt`
- `scia_security/scia_security/__init__.py`
- `scia_security/scia_security/execution_graph.py`
- `scia_security/scia_security/integrity.py`
- `scia_security/scia_security/seed_signature.py`
- `scia_security/scia_security/signing_client.py`
- `scia_security/setup.py`
- `scratch/find_enterprise.py`
- `scratch/reorder_enterprise.py`
- `scratch/run_enterprise.py`
- `scratch/test_phase_e_sion_visibility.py`

## Files To Add To `.gitignore`

- Fix the malformed literal `\n` before the Enterprise ignore section in `.gitignore`.
- `memory/`
- `scia_memory/`
- `scia_security/`
- `docs/SRT1_ENTERPRISE_ARCHITECTURE.md`
- `PHASE_*_WALKTHROUGH.md` unless approved as sanitized public docs.
- `debug.log`
- `pytest_output.txt`
- `scratch.html`
- `scratch/` unless selected tests are promoted into a proper public test location.
- `*.bak`
- `srt1_audit_delta.json`
- `unknown_to_ast.py`

Existing ignore rules already cover `.srt1/`, generated code manifests, DBs, nested `SRT1-CORE/`, and `seed-reflection/`.

## Files To Archive Later

- `scratch.html`
- `scratch/check_packages.py`
- `scratch/check_status.py`
- `scratch/check_syntax.js`
- `scratch/overhaul_dashboard.py`
- `scratch/patch_ports.py`
- `scratch/patch_ports_to_8475.py`
- `scratch/print_stats.py`
- `scratch/reorder.py`
- `scratch/search_history.py`
- `scratch/sync_dashboard.py`
- `unknown_to_ast.py`

Archive means preserve outside the public publish set or convert into intentional tests/scripts after review.

## Files Needing Founder Decision

- `.cursorrules`
- `AGENTS.md`
- `BUILD.md`
- `CLAUDE.md`
- `CTO_HANDOVER_TO_CLAUDE.md`
- `developer-pwa/auth.html`
- `developer-pwa/constellation.html`
- `developer-pwa/contact.html`
- `developer-pwa/dashboard.html`
- `developer-pwa/documentation.html`
- `developer-pwa/health.html`
- `developer-pwa/Install-SRT1.ps1`
- `developer-pwa/mobile.html`
- `docs/marketing/screenshots/Slide2_Landing_Page.png`
- `docs/marketing/screenshots/Slide3_Dashboard_Stats.png`
- `docs/marketing/screenshots/Slide4_Risk_Profile_Violations.png`
- `docs/marketing/screenshots/Slide5_Seed_Farm_Timeline.png`
- `docs/marketing/SRT1_60_SECOND_HOOK.md`
- `docs/marketing/SRT1_Dashboard_Promo.webp`
- `docs/marketing/SRT1_MANIFESTO_VIDEO.md`
- `docs/marketing/SRT1_Screenshot_Video_Script.md`
- `docs/marketing/SRT1_Social_Media_Posts.md`
- `docs/marketing/SRT1_Video_Production_Brief.md`
- `docs/marketing/SRT1_Walkthrough_Script.md`
- `docs/SRT1_Code_Indexer_Complete_Reference.docx`
- `Install-SRT1.ps1`
- `PHASE_AB_WALKTHROUGH.md`
- `PHASE_C_WALKTHROUGH.md`
- `PHASE_D_WALKTHROUGH.md`
- `PHASE_E_WALKTHROUGH.md`
- `PHASE_F_WALKTHROUGH.md`
- `PHASE_F2_WALKTHROUGH.md`
- `PRODUCT_ARCHITECTURE.md`
- `README.md`
- `scia_ui_system_skill_v_1.md`
- `scratch/adversarial_audit_suite.py`
- `scratch/live_blackbox_validation.py`
- `scratch/live_probe.py`
- `scratch/run_auditor_live.py`
- `scratch/start_all.py`
- `scratch/test_adversarial_governance.py`
- `scratch/test_consistency_auditor.py`
- `scratch/test_live_endpoint.py`
- `scratch/test_operational_registry.py`
- `scratch/test_phase_d_dashboard.py`
- `scratch/test_phase_f_stabilization.py`
- `scratch/verify_services.py`
- `srt1_code_indexer/engine.py`
- `SRT1_CONSTITUTION.md`
- `SRT1_CONTEXT_INDEX.md`
- `SRT1_CURRENT_STATE.md`
- `SRT1_DECISIONS.md`
- `SRT1_ENFORCEMENT_MODE.md`
- `SRT1_FRONTIER.md`
- `SRT1_Marketing_DevExperience.webp`
- `srt1_platform/__init__.py`
- `srt1_platform/audit_ledger.py`
- `srt1_platform/change_proposal.py`
- `srt1_platform/execution_bridge.py`
- `srt1_platform/execution_lease.py`
- `srt1_platform/filecell.py`
- `srt1_platform/governance_monitor.py`
- `srt1_platform/llm_adapter.py`
- `srt1_platform/llm_providers.py`
- `srt1_platform/manifest_deriver.py`
- `srt1_platform/operational_registry.py`
- `srt1_platform/pwa/auth.html`
- `srt1_platform/pwa/constellation.html`
- `srt1_platform/pwa/contact.html`
- `srt1_platform/pwa/dashboard.html`
- `srt1_platform/pwa/documentation.html`
- `srt1_platform/pwa/health.html`
- `srt1_platform/pwa/Install-SRT1.ps1`
- `srt1_platform/pwa/mobile.html`
- `srt1_platform/pwa/templates/dashboard-enforcement.html`
- `srt1_platform/pwa/templates/doc-content.html`
- `srt1_platform/pwa/templates/home-pricing.html`
- `srt1_platform/tracing_system.py`
- `srt1_platform/verification.py`
- `srt1_pro/__init__.py`
- `srt1_pro/self_heal.py`
- `srt1-contracts/contracts/audit_event_contract.md`
- `srt1-contracts/contracts/execution_lease_contract.md`
- `srt1-contracts/contracts/filecell_contract.md`
- `srt1-contracts/contracts/post_execution_verification_contract.md`
- `srt1-contracts/SRT1_OPERATING_MAP.md`
- `srt1-contracts/srt1-skills/audit-event-emission/activation.md`
- `srt1-contracts/srt1-skills/audit-event-emission/events.md`
- `srt1-contracts/srt1-skills/audit-event-emission/SKILL.md`
- `srt1-contracts/srt1-skills/audit-event-emission/verification.md`
- `srt1-contracts/srt1-skills/constellation-mapping/activation.md`
- `srt1-contracts/srt1-skills/constellation-mapping/events.md`
- `srt1-contracts/srt1-skills/constellation-mapping/SKILL.md`
- `srt1-contracts/srt1-skills/constellation-mapping/verification.md`
- `srt1-contracts/srt1-skills/filecell-manifest-derivation/activation.md`
- `srt1-contracts/srt1-skills/filecell-manifest-derivation/events.md`
- `srt1-contracts/srt1-skills/filecell-manifest-derivation/SKILL.md`
- `srt1-contracts/srt1-skills/filecell-manifest-derivation/verification.md`
- `srt1-contracts/srt1-skills/post-execution-verification/activation.md`
- `srt1-contracts/srt1-skills/post-execution-verification/events.md`
- `srt1-contracts/srt1-skills/post-execution-verification/SKILL.md`
- `srt1-contracts/srt1-skills/post-execution-verification/verification.md`
- `srt1-skills/ast-analysis/governance.md`
- `srt1-skills/audit-event-emission/activation.md`
- `srt1-skills/audit-event-emission/events.md`
- `srt1-skills/audit-event-emission/governance.md`
- `srt1-skills/audit-event-emission/inputs_outputs.md`
- `srt1-skills/audit-event-emission/SKILL.md`
- `srt1-skills/audit-event-emission/verification.md`
- `srt1-skills/constellation-mapping/activation.md`
- `srt1-skills/constellation-mapping/events.md`
- `srt1-skills/constellation-mapping/governance.md`
- `srt1-skills/constellation-mapping/inputs_outputs.md`
- `srt1-skills/constellation-mapping/SKILL.md`
- `srt1-skills/constellation-mapping/verification.md`
- `srt1-skills/context-injection/governance.md`
- `srt1-skills/drift-detection/governance.md`
- `srt1-skills/filecell-manifest-derivation/activation.md`
- `srt1-skills/filecell-manifest-derivation/events.md`
- `srt1-skills/filecell-manifest-derivation/governance.md`
- `srt1-skills/filecell-manifest-derivation/inputs_outputs.md`
- `srt1-skills/filecell-manifest-derivation/SKILL.md`
- `srt1-skills/filecell-manifest-derivation/verification.md`
- `srt1-skills/module-boundary-protection/governance.md`
- `srt1-skills/post-execution-verification/activation.md`
- `srt1-skills/post-execution-verification/events.md`
- `srt1-skills/post-execution-verification/governance.md`
- `srt1-skills/post-execution-verification/inputs_outputs.md`
- `srt1-skills/post-execution-verification/SKILL.md`
- `srt1-skills/post-execution-verification/verification.md`
- `srt1-skills/repo-indexing/governance.md`

## Proposed First Commit Contents

First commit should be a boundary and inventory commit only:

- `docs/recovery/SRT1_PUBLISH_INVENTORY.md`
- `.gitignore` repair/additions after approval.
- No private implementation files.
- No PWA/engine feature changes yet.
- No deletions staged yet except approved removal of public-Core references to private packages.

Suggested commit message after approval:

`docs: add SRT1 publish inventory and recovery boundary`
