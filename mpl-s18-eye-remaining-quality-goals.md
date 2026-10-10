# MPL S18 Eye — Remaining Quality Goals

> Repository: `berliandro/berliandros-eye-mpl-s18`  
> Baseline reported by the previous implementation: commit `5086f80` on `origin/main`  
> Purpose: close remaining release-verification gaps and address demonstrated quality issues without repeating completed work.

## How to use this file

- Work in priority order: `P0` → `P1` → `P2`.
- Pick one focused goal at a time. Split larger work into small, verifiable sub-goals before implementation.
- Inspect the current repository and working tree first. The baseline above is historical context, not proof that the current checkout is unchanged.
- Reuse existing verification commands and tests. Do not create duplicate test infrastructure just to satisfy a checklist item.
- Mark a goal `[x]` only after running the relevant check and recording evidence.
- Do not weaken or delete meaningful tests to make a change pass.
- Preserve MPL ID Season 18 behavior, existing UI functionality, and offline behavior unless a verified defect requires a fix.
- Do not invent Season 19 data, rules, teams, or assumptions.
- Keep changes scoped to the goal being addressed. Avoid broad refactors or new dependencies without a clear, demonstrated benefit.
- Never force-push, overwrite unrelated work, or discard user changes.

## P0 — Release Verification and Correctness

- [ ] **GitHub Actions CI:** Inspect the current workflow and its latest run for the current `origin/main` commit. Confirm that the workflow actually passes. If no run exists, trigger one through the established repository workflow if permitted. Fix only reproducible workflow or code failures; do not report an inspected workflow as an executed pass.
- [ ] **XSS audit:** Trace all DOM insertion sinks in the frontend that receive external API, cached, or generated data. Identify whether values are inserted as HTML, attributes, URLs, or plain text. Prefer safe DOM APIs such as `textContent` where HTML is not required; where HTML is required, apply context-appropriate sanitization. Fix confirmed vulnerabilities and add regression tests for each relevant exploit path. Do not blindly sanitize or transform every value without understanding its rendering context.
- [ ] **Controlled ETL release validation:** Run a controlled end-to-end database rebuild using the intended source data and existing documented workflow, where access and runtime permit. Verify that the final match block is included, expected match counts and required fields are valid, and the database/CSV outputs are mutually consistent. Exercise or test the failure path and confirm that a failed build preserves the last known-good outputs. Avoid publishing unintended data changes.
- [ ] **Regression-coverage audit:** Review the current tests for sorting, filtering, data transformations, empty or malformed input, and API failure handling. Add tests only for concrete gaps that are not already covered by the existing verification suites. Keep tests deterministic and independent of live external services where practical.
- [ ] **External-request and scraping review:** Inspect actual scripts and request destinations, User-Agent configuration, request frequency, retries, and relevant source access policies (including `robots.txt` and applicable terms). Establish the current behavior before changing it. Make only evidence-based changes, and document any unresolved access-policy uncertainty rather than claiming compliance without verification.

## P1 — Maintainability

- [ ] **Complexity review:** Identify remaining high-complexity or fragile functions in the frontend and ETL. Extract helpers only when this improves testability, correctness, or comprehension. Avoid large architectural rewrites without a concrete maintenance problem.
- [ ] **Python linting:** Evaluate whether Ruff would provide useful linting and formatting checks for this repository. If adopted, configure a focused rule set, integrate it into the existing verification flow, and fix resulting issues without changing behavior. Do not add a tool solely for checklist completion.
- [ ] **Error-handling review:** Look for swallowed exceptions, misleading user-facing status, lost diagnostic context, and failures that can leave state partially updated. Replace broad exception handling only where a narrower handler is safe and meaningful. Add tests for any corrected failure behavior.
- [ ] **Build and recovery documentation:** Confirm that README documentation accurately describes the authoritative build, verification, data-refresh, and recovery commands, including what each command does and whether it needs network access. Update it only where it is inaccurate or incomplete.

## P2 — Optional Improvements

- [ ] **JavaScript linting:** Evaluate a JavaScript linter only if it addresses demonstrated consistency or correctness needs. Avoid introducing overlapping formatting/style tools or disruptive mass reformatting.
- [ ] **Repository hygiene:** Review `.gitignore` against actual generated outputs and local-only files. Keep required source assets and intentional build artifacts tracked; do not ignore files solely because they are generated.
- [ ] **License decision:** If the repository has no license, ask the repository owner to select the intended license and terms before adding a `LICENSE` file. Do not choose legal terms on the owner's behalf.
- [ ] **Static analysis and dependency monitoring:** Consider Python type checking or dependency vulnerability scanning only after reviewing the project's dependency footprint and maintenance needs. Document the rationale before introducing new configuration or CI cost.

## Completion and reporting requirements

At the end of the run:

1. Report each goal as completed, not needed (with evidence), blocked, or deferred.
2. Distinguish executed checks from code inspection and checks that could not be run.
3. Report actual test counts/results, CI run status and commit association if available, ETL validation scope, and any known limitations.
4. Summarize files changed and why each change was necessary.
5. Review the full diff for accidental data churn, generated-file noise, unrelated changes, and weakened tests.
6. Run the authoritative verification command and rebuild/parity checks when applicable.
7. Commit only when changes are coherent and required local checks pass. Use a descriptive commit message. Push only if the repository workflow permits it and the push can be performed safely as a fast-forward.
8. Report the final commit SHA and whether the working tree is clean. Never claim a check passed unless it actually ran and passed.

## Initial instructions

Start by checking the current branch, working-tree status, current `HEAD`, and relationship to `origin/main`. Read the existing README and verification entry point, then inspect the current CI workflow and recent run status. Compare the current implementation with the goals above before editing anything. The earlier implementation report says commit `5086f80` passed nine local suites, but CI and full live ETL validation were not executed at that time; independently verify the present state rather than treating that report as proof.
