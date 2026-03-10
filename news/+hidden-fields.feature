Added hidden field support via the `format` keyword.
`format: constant` returns the raw `default` value without rendering; `format: computed` evaluates `default` as a Jinja2 template against the collected answers.
Hidden fields are resolved automatically after all user-facing questions have been answered. @ericof
