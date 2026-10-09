# Draft walkthrough: Ask Socrates

A tiny quote search has a bug: `know` finds a quote, but `KNOW` does not. This example follows the fix through all four phases, including a new session picking up the work from the task records.

The record excerpts below are illustrative and shortened for readability.

## The starting point

Use Python 3 and a separate example repository. Save this program as `socrates.py`. The two quotations are excerpts of Socrates' speech in Plato's [*Apology*, translated by Benjamin Jowett](https://classics.mit.edu/Plato/apology.html).

```python
import sys

QUOTES = (
    "I neither know nor think that I know.",
    "the life which is unexamined is not worth living",
)


def find_quotes(query):
    return [quote for quote in QUOTES if query in quote]


if __name__ == "__main__":
    for quote in find_quotes(" ".join(sys.argv[1:])):
        print(quote)
```

Follow the README's [Setup](../README.md#setup) and [Getting Started](../README.md#getting-started) instructions for this example repository. Use `README.md` for reusable project notes, and complete the bootstrap task's closeout before starting the task below.

For this example, the README's `Usage` section initially says: “Search matches capitalization exactly.” It owns current search behavior; the task archive owns the history of changing that behavior. No separate architecture or operations document is needed.

## 1. Plan

Give your agent this task:

> Fix the quote search so it ignores capitalization. Keep the original quote text and order. With no query, print both quotes; with no match, print nothing. Follow `AGENTS.md`: reproduce the problem, write the plan in `.agent/TASK_BRIEF.md`, and stop for approval.

The agent compares `python3 socrates.py know` with `python3 socrates.py KNOW` and records the difference. Its task brief should make the intended behavior inspectable:

```markdown
## Task
- Make quote search ignore capitalization.

## Status
- **Phase:** Phase 1
- **State:** planned
- **Last updated:** <current date and time>

## Fixed invariants (do not change)
- Preserve the original quote text and order.

## Documentation impact
- README.md#usage — replace the case-sensitive matching instruction.

## Milestones
- [ ] Fix matching and verify all five checks.
- [ ] Review the output and complete closeout.

## Implementation plan
1. Add checks for lowercase, uppercase, and mixed-case matching,
   an empty query, and an unmatched query.
2. Normalize query and quote text for comparison.
3. Run the checks and inspect the command-line output.

## Next steps
1. Await approval to implement.
```

In the *Apology*, Socrates describes testing the oracle's claim about his wisdom by questioning people reputed to be wise. Here, the claim that search works also gets a concrete test. [Source: Plato's *Apology*.](https://classics.mit.edu/Plato/apology.html)

## 2. Implement and verify

After inspecting the plan, reply:

> Approved. Implement the plan, run the checks, and update the task records. Stop for review.

A minimal regression check, saved as `check_socrates.py`, captures the five expected results:

```python
from socrates import QUOTES, find_quotes

for query in ("know", "KNOW", "i NeItHeR"):
    assert find_quotes(query) == [QUOTES[0]], query
assert find_quotes("") == list(QUOTES)
assert find_quotes("hemlock") == []
print("5 checks passed")
```

Running `python3 check_socrates.py` against the starting program fails on `KNOW`. The fix changes only the comparison in `find_quotes`:

```python
def find_quotes(query):
    needle = query.casefold()
    return [quote for quote in QUOTES if needle in quote.casefold()]
```

Run the checks again. The expected result is `5 checks passed`. Also run `python3 socrates.py KNOW` and confirm that the first quote retains its original capitalization.

The investigation belongs in `.agent/MEMORY.md`. An excerpt after successful verification would be:

```markdown
## Bug impact traceability

### BUG-001 — Search misses matches with different capitalization
- Impact: KNOW finds nothing even though know finds the first quote.
- Root cause: substring matching compares the original strings directly.
- Fix location: socrates.py, find_quotes.
- Regression evidence: python3 check_socrates.py — 5 checks passed;
  python3 socrates.py KNOW — first quote, original capitalization.
- Affected versions/artifacts: the starting program in this walkthrough;
  no earlier history examined.
- Follow-up: none.

## Gotchas discovered (reconcile with maintained owners)
- Normalize text for comparison; return the original quote for display.
```

Before handing back, the agent replaces the obsolete sentence in `README.md#usage` with: “Search ignores capitalization and preserves the original quote text and order. With no query it prints both quotes; with no match it prints nothing.” It keeps failure evidence in memory rather than appending a second, conflicting usage rule. It updates the task brief: the first milestone is complete, **Phase** is `Phase 3`, **State** is `awaiting review`, and **Next steps** identifies review and closeout. It updates **Last updated** to match.

## 3. Review in a new session

Open a fresh agent session in the same repository. You can use a different model with access to the same files. Give it this prompt:

> Read `AGENTS.md`, `.agent/TASK_BRIEF.md`, and `.agent/MEMORY.md`. Resume the existing task at its recorded phase. Summarize what has been verified and what remains. Re-run `python3 check_socrates.py` and show the output of `python3 socrates.py KNOW` for review.

The agent has enough information to locate the fix, understand the display constraint, and repeat the verification. You can review its result without reconstructing the previous conversation.

If a check fails, remain in review: reproduce the failure, test a hypothesis, make a targeted correction, and update the evidence before requesting approval again.

## 4. Close out

Once you are satisfied, reply:

> Approved. Complete Phase 4 closeout.

The agent enters Phase 4 with the task still in progress. It checks the updated `README.md#usage` against the verified behavior, confirms no working-agreement change is needed, and preserves the old failure evidence in the task records. It archives those records according to `AGENTS.md`:

```text
docs/agent/tasks/<task_slug>/
  TASK_BRIEF.md
  MEMORY.md
  CLOSEOUT.md
```

After verifying the archive, the agent marks the archived task brief complete. The closeout should give a future planning agent enough context to identify applicable decisions without reading the full investigation. A shortened example:

```markdown
# Closeout: quote search

- Outcome: search ignores capitalization and preserves quote text/order.
- BUG-001: direct, case-sensitive comparison caused missed matches;
  fixed in socrates.py, find_quotes. The starting program was affected;
  no earlier history examined.
- Decision: casefold only for comparison; display the original strings.
- Verification: python3 check_socrates.py — 5 checks passed;
  python3 socrates.py KNOW — first quote, original capitalization.
- Documentation reconciliation: replaced the obsolete case-sensitive rule
  in README.md#usage; confirmed matching, display, empty-query and no-match
  instructions agree with verification. AGENTS.md needs no change because
  the working agreement and essential invariants are unchanged. Historical
  failure evidence remains in this closeout and MEMORY.md.
- Follow-ups: none required for this fix.
- Context lineage: no epoch; no prior closeouts reviewed.
- Suggested successor: display the source alongside each quote.
```

For that next task, replace `<task_slug>` with the actual archive folder and ask:

> Add the source alongside each quote. Follow `AGENTS.md`. In Phase 1, read `README.md#usage` and `docs/agent/tasks/<task_slug>/CLOSEOUT.md`, reconcile them with the current code, and construct `.agent/TASK_BRIEF.md`. Preserve the search behavior established by that task. Stop for plan approval.

The new brief records the closeout path and carries forward the still-applicable matching and display constraints, linking to the earlier verification evidence. It identifies `README.md#usage` as the owner affected by the new output format. The agent opens the old memory or task brief only if the closeout leaves a question material to the plan unanswered. Implementation then uses the new task brief alongside maintained guidance.
