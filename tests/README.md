# Tests

No framework and no network: everything here runs with plain `python3` from the repo root,
with `PYTHONPATH=.` so `app` imports.

```
PYTHONPATH=. python3 tests/test_intake.py      # the pipeline, against a fake provider
PYTHONPATH=. python3 tests/test_prompts.py     # the prompt contract
PYTHONPATH=. python3 tests/dryrun_intake.py prosperity /tmp/dry [synthesis|revision]
```

**`test_intake.py`** builds a throwaway campaign in a temp directory, replaces `llm.chat` with
a fake that answers by destination, and runs intake end to end: the three parallel synthesis
calls on one snapshot, the identical cacheable prefix, per-destination guides, formatting
repair, the one failure condition, preservation telemetry that warns and keeps, the human gate,
pass 4 in parallel and pass 5. It writes nothing outside the temp directory.

**`test_prompts.py`** asserts that the rules the showrunner asked for are in the text the model
actually receives — prior items survive, `[established]` is strict, the least-supported
consequential claim sets an option's label, pass 3 runs the research challenge, and so on. It
checks prompts, never model output, and adds no gates: an unlabelled option still does not fail
a call.

**`dryrun_intake.py`** builds every prompt of a real round and stops before the model. Nothing
is sent and nothing is written to the campaign. Use it to see sizes, what each pass is given,
and the preservation numbers for the files currently on the desk.

`mock_openai.py` is the older fake provider for `docker compose --profile mock`.
