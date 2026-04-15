# SRT1 Enforcement Mode Spec

## Purpose

SRT1 Enforcement Mode exists to close the gap between:

* detection
* interpretation
* enforcement

SRT1 is not fully protective if it can detect a violation but cannot prevent unauthorized progression.

Advisory truth alone is insufficient.
SCIA requires enforceable boundaries.

---

## 1. Core Principle

**Detection without enforcement is not protection.**

SRT1 must support two modes:

### Advisory Mode

* observe
* index
* reflect
* warn
* recommend

### Enforcement Mode

* observe
* validate
* block
* require remediation or override
* log the event and its resolution path

---

## 2. What Enforcement Mode Is

SRT1 Enforcement Mode is a control layer that can:

* halt build progression
* block unauthorized section advancement
* stop execution of invalid next steps
* require explicit override
* preserve a signed violation trail

It is not:

* a builder
* an executor
* a substitute for doctrine
* a replacement for section ownership

---

## 3. Enforcement Targets

SRT1 Enforcement Mode may block progression when any of the following is detected.

### 3.1 Boundary violation

Examples:

* PACE performing alignment
* SeedLink performing activation
* PersonaSwarm performing staffing
* SRT1 performing mutation

### 3.2 False completion claim

Examples:

* scaffold described as complete
* placeholder logic described as real cognition
* unbuilt section described as operational

### 3.3 Unauthorized progression

Examples:

* moving to next section without halt review
* continuing after a doctrine-defined stop point
* building downstream while upstream remains incomplete

### 3.4 Missing substrate treated as available

Examples:

* partial registry treated as full registry
* stub constructor treated as real constructor
* metadata-only source treated as concrete data

### 3.5 Signature / lineage violation

Examples:

* missing required signature reference
* broken provenance chain
* override with no trace record
* section-local signature misrepresented as Sig-0

### 3.6 Duplicate or conflicting execution path

Examples:

* parallel logic path introduced without authorization
* same responsibility implemented in multiple organs
* silent fallback that bypasses canonical path

### 3.7 Doctrine conflict

Examples:

* current action contradicts CLAUDE.md
* current action contradicts BUILD.md
* locked section touched without explicit authorization

---

## 4. Enforcement Levels

### Level 0 — Informational

* record only
* no block

Used for:

* low-risk notes
* early observations
* weak anomaly signals

### Level 1 — Warning

* visible warning
* progression still allowed

Used for:

* non-critical drift
* incomplete reporting
* unclear phrasing

### Level 2 — Soft Stop

* progression paused
* acknowledgment required

Used for:

* unresolved ambiguity
* questionable substrate
* incomplete verification

### Level 3 — Hard Stop

* action blocked
* remediation or override required

Used for:

* boundary violation
* false completion
* unauthorized progression
* signature/lineage break
* missing critical dependency treated as real

### Level 4 — Lockout

* progression blocked
* privileged override only
* event marked critical

Used for:

* repeated hard-stop bypass attempts
* doctrine breach affecting multiple sections
* integrity or provenance compromise

---

## 5. Required Enforcement Actions

When SRT1 enters Enforcement Mode, it must do all of the following:

### 5.1 Name the violation

State:

* what rule was violated
* where it occurred
* why it matters

### 5.2 Classify severity

Assign:

* informational
* warning
* soft stop
* hard stop
* lockout

### 5.3 Identify blocked action

State exactly what cannot continue.

Example:

* "Section 7 cannot begin"
* "Commit cannot proceed"
* "Code generation must halt"
* "Section completion claim is invalid"

### 5.4 Define valid exits

State the only lawful next moves:

* remediate
* explicitly override
* defer
* re-scope

### 5.5 Log lineage

Write a violation record containing:

* timestamp
* active section
* triggering artifact or action
* violated rule
* severity
* proposed resolution
* override status if any

---

## 6. Override Model

Overrides must exist, but they must be hard and explicit.

### 6.1 Override is not silent

An override must never be implicit.

### 6.2 Override requires reason

The actor must state:

* why the block is being overridden
* why proceeding is still justified
* what risk is being accepted

### 6.3 Override must be logged

Every override must produce:

* override record
* linked violation record
* actor identity
* scope of override
* expiration or review condition if applicable

### 6.4 Override does not erase violation

The original violation remains in history.

### 6.5 Some classes may be non-overridable

Examples:

* corrupted lineage
* invalid signature chain
* locked section modification without authorization
* fabricated completion in a high-stakes section

---

## 7. Enforcement Surfaces

SRT1 Enforcement Mode should be able to hook into the following surfaces.

### 7.1 Build progression

Block:

* next section pass
* downstream progression
* unauthorized reopening

### 7.2 Generation / mutation actions

Block:

* file write
* code rewrite
* doc regeneration
* AST mutation

### 7.3 Commit / release surfaces

Block:

* commit
* push
* release marking
* "complete" status claims

### 7.4 Runtime progression

Block:

* invalid orchestration steps
* execution attempts under unresolved violation
* invalid state advancement

---

## 8. Minimum Viable Enforcement Rules for SCIA

These should be hard-stop by default.

### Rule A

No section progression when the current section is incomplete within lawful scope.

### Rule B

No scaffold may be reported as complete cognition.

### Rule C

No downstream organ may absorb upstream authority.

### Rule D

No missing substrate may be treated as present.

### Rule E

No raw input may bypass SION as root entry.

### Rule F

No signature terminology may be falsified or collapsed.

### Rule G

No locked surface may be modified without explicit authorization.

---

## 9. Reporting Format

Every enforcement event should report in this shape:

### SRT1 Enforcement Event

* Mode:
* Severity:
* Active Section:
* Violated Rule:
* Blocked Action:
* Reason:
* Required Resolution:
* Override Allowed:
* Lineage Record ID:

---

## 10. Relationship to Standalone SRT1

In standalone mode, SRT1 Enforcement Mode operates over the Declared System Model.

That means it may block based on:

* declared rules
* visible artifacts
* visible implementation state
* visible absence of required substrate

It does not require the full target system to exist in order to enforce truth against what is declared.

---

## 11. Relationship to SCIA

Inside SCIA, SRT1 Enforcement Mode acts as the system's immune boundary.

It does not replace:

* SION
* SeedFlow
* SeedLink
* PACE
* PersonaSwarm

It ensures those organs do not drift out of law.

---

## 12. Final Rule

**SRT1 is incomplete if it can detect violation but cannot prevent unauthorized progression.**

And:

**SCIA requires both advisory truth and enforceable boundaries.**

---

## Document Relationships

| Document | Purpose |
|----------|---------|
| `OPERATING_LAW_SRT1_STANDALONE.md` | WHAT SRT-1 is (doctrine) |
| `SCIA_BUILD_PROTOCOL.md` | HOW SRT-1 is used (procedure) |
| `PUBLIC_BOUNDARY.md` | WHAT is included and excluded (boundary) |
| `TIER_BOUNDARY_LAW.md` | WHO can access what (access control) |
| `SRT1_ENFORCEMENT_MODE.md` | HOW SRT-1 enforces truth (this document) |

---

*SRT-1 Enforcement Mode Spec v1.0 — SCIA v4.0*
