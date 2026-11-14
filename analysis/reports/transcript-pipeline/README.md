# Transcript pipeline reports

One run report per source: `<source_id>.md`.

Include:

- source and alignment status;
- model/provider/prompt version;
- observations accepted / needs-review / rejected / duplicate;
- unresolved references and proposed categories;
- database references used;
- elapsed time and token usage;
- validation command and result;
- files created or updated.

Do not report a percentage as coverage. Report completed source counts and
explicit statuses (`pending`, `in_progress`, `complete`, `partial`, `blocked`).
