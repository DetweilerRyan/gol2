# Docs

Human-reviewed project knowledge that agents can't infer from the code. `CLAUDE.md` points here.

- [`decisions/`](decisions/): architecture decision records (ADRs), one file per decision, numbered and never
  renumbered. To reverse a decision, add a new ADR that supersedes the old one.

Add a folder only when a document needs it. If the code can answer a question, don't write a doc for it.

## ADR status

Each ADR has a `Status:` line with a date:

- `proposed`: drafted, not yet decided. tech drafts ADRs on stack, architecture, and build-vs-buy as `proposed`.
- `accepted`: the user decided. Only the user marks an ADR `accepted`, by editing it or by telling an agent to
  record the acceptance; no agent marks one `accepted` on its own judgment.

## Who owns which doc

Each doc has one owner. Either role may flag problems in the other's docs; the owner fixes them.

- tech: product and technical docs (architecture, dev setup, devops, `README.md`) and ADRs on stack, architecture,
  and build-vs-buy.
- coach: this file, docs about how agents work (agent and process docs), and ADRs on agent or process decisions.
