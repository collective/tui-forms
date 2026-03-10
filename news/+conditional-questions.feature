Added conditional question support via JSONSchema `allOf` / `if` / `then` blocks.
A question defined inside a `then` block is only shown when its `if` condition matches the current answers, following the pattern `{properties: {key: {const: value}}}`. @ericof
