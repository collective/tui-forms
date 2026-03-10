Added full `$ref` and `$defs` / `definitions` resolution.
Schema fragments can be defined once and referenced in multiple properties, array `items`, and `allOf` / `then` blocks.
Inline keys placed alongside `$ref` override the referenced definition. @ericof
