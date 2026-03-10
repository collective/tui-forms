Added automatic progress tracking for all renderers.
Each user-facing question is prefixed with `[current/total]` (e.g. `[3/9]`).
The prefix format can be overridden per renderer by implementing `_format_prefix`, or suppressed entirely by returning an empty string. @ericof
