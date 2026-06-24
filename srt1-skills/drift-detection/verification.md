# Drift Detection — Verification

## Success Criteria

| Check | Condition |
|-------|-----------|
| Checkpoint Generation | A `ReflectionCheckpoint` is successfully created every `reflection_interval` (default 3) operations. |
| Score Boundedness | Calculated `coherence_score` is strictly between `0.0` and `1.0` inclusive. |
| Drift Triggers Correctly | Generating operations unrelated to the seed keywords drops the coherence score and changes status to `MAJOR_DRIFT` or `SEED_LOST`. |

## Failure Indicators

| Indicator | Meaning |
|-----------|---------|
| No checkpoints fired | Traced operations are registered but check fails to fire. |
| Coherence score is 0.0 with keywords present | Intersection calculation failed or recent history buffer cleared incorrectly. |
| Drift status doesn't match score | Scale threshold bug in `_generate_reflection_checkpoint`. |
