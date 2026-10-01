# Credential Exposure Record (m7)

**Recorded:** 2026-10-01
**Scope:** the Delta repository (`CyBreach-Validator/verdict-platform`), `main`
**Status of rotation:** outstanding — see "Required action" below.

This file exists so the m7 exposure is written down with its date, scope and
owner rather than living only as a line in the integration register. Removing a
literal from a file does not remove it from any existing clone, and rotating a
secret does not un-expose the old one, so the exposure is recorded here
independently of whether the history is ever rewritten.

## Exposed credentials

The values are deliberately **not** reproduced here. A record of an exposure
that reprints the secret re-publishes it — which is the mistake this file exists
to prevent, and one that was made in this repository already: the two
occurrences removed from `alembic.ini`/`env.py` in this pass sat inside comments
that quoted the old value while explaining the fix. Each credential is therefore
identified by its role, its locations and a fingerprint, which is enough to find
and rotate it without handing it to the next reader.

| # | Role / account | Kind | Fingerprint (SHA-256, first 12 hex) | Where it appeared |
| --- | --- | --- | --- | --- |
| 1 | PostgreSQL superuser `postgres` | password | `66e7ee708f37` | earlier working-tree revisions and git history |
| 2 | PostgreSQL role `validator` | password | `5935579649b2` | `backend/alembic.ini`, `backend/alembic/env.py`, and git history |

Recompute a fingerprint before rotating, to confirm you have the right value:

```bash
printf '%s' '<the-password>' | sha256sum | cut -c1-12
```

Both were development credentials for the local integration database
(`module2_validator` on localhost). Neither is used by the code as it now
stands: `backend/alembic/env.py` resolves `DATABASE_URL` from the environment and
raises when it is unset, and the `sqlalchemy.url` value in `alembic.ini` is an
empty placeholder kept only to satisfy the ini parser.

## Exposure window

The literals are present in commits `f2ab344` (2026-09-25) and `0a2abf0`
(2026-09-28), and both are reachable from `origin/main`. The remote is a public
GitHub repository, so the exposure is not confined to this team's clones: anyone
who cloned or forked the repository in that window can read them.

## What was done

- The credential literals were removed from the current working tree. The two
  occurrences that survived the earlier pass were inside *comments* that quoted
  the old value while explaining what had been fixed — functionally inert, but
  they still published the secret in a tracked file and would have made rotation
  pointless. They now read `<redacted>`.
- Every working tree in all four pods is clean of credential literals; Alpha's
  two instances were closed earlier.

## Required action

1. **Rotate both credentials at the database.** Treat both as compromised: the
   values were published to a public remote, so "it is only a dev database" is
   not a reason to keep them. This step is not a code change and is not recorded
   anywhere in the repository — it has to be done in the environment.
2. **Update the deployment environment** to match, and confirm nothing still
   expects the old values. `DATABASE_URL` is the single source of truth for
   migrations, so the new value is injected rather than edited into a file.
3. **Decide on history rewriting.** Because the remote is public, a rewrite
   (`git filter-repo`, or BFG) plus a force-push would remove the literals from
   history — but it is destructive and irreversible for anyone who has already
   cloned, it rewrites commit hashes for every collaborator, and it does **not**
   help on its own: GitHub keeps unreachable objects accessible through cached
   views and forks until the credentials are rotated. Rotation is the part that
   actually removes risk; the rewrite is optional hygiene. This is deliberately
   left as the team's decision rather than done unilaterally.

## Verifying

From the repository root, the literals should not appear in the working tree.
The patterns are deliberately partial, so this document never spells a complete
credential:

```bash
# should print nothing
git grep -nE 'validator_(dev_)?pw|postgres:vy[a-z]+' -- .
```

No output means the tree is clean. History is expected to still contain them
until either a rewrite is performed or item 3 above is decided and recorded
here.