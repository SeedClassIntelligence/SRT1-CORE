# SRT1 Seed Signature Widget Integration

Purpose: define the public Core-safe integration boundary between SRT-1 and the
standalone Seed Signature platform.

SRT-1 may let a developer create or attach a Seed Signature from inside the
SRT-1 dashboard. The signing authority, keys, certificate generation, and
private signing records remain owned by the standalone Seed Signature platform.

## Integration Model

Seed Signature is integrated as an external widget flow:

1. SRT-1 backend requests a signing session token.
2. SRT-1 frontend loads the Seed Signature JavaScript SDK.
3. A dashboard trigger opens the signing modal.
4. Seed Signature completes signing externally.
5. SRT-1 stores returned trust metadata.

No Seed Signature private platform code ships in SRT-1 Core.

## Attribution Enforcement Promise

The product promise is not merely that a developer can view or attach a Seed
Signature. Once a repository, WorkCell, seed, or artifact is covered by a Seed
Signature, SRT-1 must treat that signature as required attribution metadata for
the work it governs.

SRT-1 should propagate attached Seed Signature metadata through:

- generated code artifacts
- WorkCell packages
- seed lifecycle records
- recall and reinjection packets
- verification records
- completion records
- generated manifests where relevant
- commit/push preparation metadata where SRT-1 controls the workflow

The signature represents attribution and lineage for the developer/company
operating SRT-1. If signature enforcement is enabled for a repository or
WorkCell, SRT-1 should not silently produce unsigned governed outputs.

Core rule:

```text
If Seed Signature is required and no valid signature metadata is present,
SRT-1 must fail closed or mark the artifact as unsigned/unverified.
```

This does not mean public Core performs private signing. Public Core enforces
the requirement, carries returned signature metadata, and blocks or labels
governed outputs when required attribution is missing. The standalone Seed
Signature platform performs signing and issues the signature/certificate.

## Backend Contract

SRT-1 needs one server-side route that exchanges SRT-1's configured platform API
key for a short-lived Seed Signature widget session.

Example route shape:

```text
POST /api/v1/seed-signature/session
```

Runtime behavior:

```text
SRT-1 backend
-> Seed Signature session endpoint
-> returns sessionToken + widgetUrl
```

Rules:

- The platform API key is used only server-side.
- The platform API key is never sent to the browser.
- If the Seed Signature service is unavailable, SRT-1 fails closed.
- SRT-1 may return a disabled/unavailable state to the dashboard.
- SRT-1 stores only returned public trust metadata.

Expected response to frontend:

```json
{
  "sessionToken": "short_lived_widget_token",
  "widgetUrl": "https://seed-signature.example/widget",
  "expiresAt": "2026-07-05T12:00:00Z"
}
```

## Frontend Contract

The SRT-1 dashboard may load the Seed Signature SDK globally:

```html
<script src="https://your-domain.com/sdk/seed-signature-widget.js"></script>
```

Any eligible SRT-1 surface can then open the signing flow:

```javascript
SeedSignature.openSignModal({
  sessionToken,
  onComplete(result) {
    // result.signatureId
    // result.certificateUrl
  },
  onError(error) {
    // show fail-closed unavailable/error state
  }
});
```

## SRT-1 Trigger Points

Valid trigger points:

- Repository activation.
- WorkCell package readiness.
- Seed planting.
- Completion review.
- Verification accepted.
- Manual "Create/Attach Seed Signature" dashboard action.

The trigger opens the external signing modal. It does not give SRT-1 private
signing authority.

## Metadata Stored By SRT-1

SRT-1 may store:

- `signature_id`
- `certificate_url`
- `signature_status`
- `signed_at`
- `lineage_present`
- `trust_state`
- `queue_seed_id`
- `srt_anchor_id`
- `manifest_hash`
- `workcell_id`
- attribution owner / organization label
- enforcement mode: optional, required, or disabled
- governed artifact IDs
- commit or push correlation ID, when SRT-1 controls the workflow

SRT-1 must not store:

- private keys
- signing secrets
- private signing records
- private audit chain internals
- Seed Signature platform implementation code

## Trust Language

SRT-1 Core may say:

```text
This artifact has an attached Seed Signature.
```

SRT-1 Core must not say:

```text
SRT-1 Core performs private Seed Signature signing.
```

Correct product boundary:

```text
Create or attach from SRT-1.
Sign through Seed Signature.
Store returned trust metadata in SRT-1.
Propagate signature attribution through governed SRT-1 outputs.
Fail closed or label unsigned when required attribution is missing.
Keep Seed Signature authority external.
```

## Implementation Scope

For SRT-1 Core, the future implementation should be small:

- one backend session-token route
- one frontend SDK script tag
- one dashboard trigger/action
- one metadata persistence/update path
- fail-closed unavailable state
- one enforcement check before governed output/commit/push preparation
- one visible dashboard state for signed, unsigned, required, and unavailable

No new framework is required.
No private Seed Signature code belongs in public Core.
