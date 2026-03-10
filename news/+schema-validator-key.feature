Added support for a `validator` key in form schema properties.
Setting `"validator": "mypackage.validators.is_valid"` on any user-facing field loads the callable at parse time and applies it as the answer validator, re-prompting on failure.
An empty string is treated as no validator; the key is silently ignored on hidden fields (`format: constant` or `format: computed`).
When both `format` and `validator` are present, the explicit `validator` key takes precedence. @ericof
