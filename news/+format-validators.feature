Added built-in input validators for standard JSONSchema format values: `email`, `idn-email`, `date` (YYYY-MM-DD), `date-time` (ISO 8601), and `data-url` (path to an existing file).
When a field carries one of these formats, the renderer automatically re-prompts on invalid input without any extra code in the schema or renderer. @ericof
