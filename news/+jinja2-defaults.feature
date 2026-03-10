Added Jinja2 template rendering for `default` values.
Any `default` field may reference previously collected answers using `{{ answer_key }}` syntax.
Defaults are rendered just before presenting each question, so later fields can derive their initial value from earlier answers. @ericof
