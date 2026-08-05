# ATLAS evaluation harness

`datasets/rag-v1.jsonl` is the Plan Maestro dataset. It contains 60 versioned
cases covering in-scope answers, Spanish/English parity, temporal context,
multi-hop questions, abstention, contradiction and prompt-injection safety.

## Safe local run

From the repository root, this command uses deterministic fixtures only. It
does not contact the ATLAS API, OpenAI or LangSmith:

```powershell
apps/backend/.venv/Scripts/python.exe evals/run_offline.py --output artifacts/eval-report.json
```

To evaluate a running local API, explicitly add `--http --api-origin
http://127.0.0.1:8000`. The HTTP mode still does not call a model itself; it
only sends requests to the origin supplied on the command line.

## LangSmith linkage (opt-in)

Keep credentials in `.env.local` or the process environment; never commit them.
The dry run is safe and does not require a key:

```powershell
apps/backend/.venv/Scripts/python.exe evals/run_langsmith.py
```

The execute mode creates or reuses the versioned dataset, uploads case inputs,
and runs the HTTP target through LangSmith. It requires
`LANGSMITH_API_KEY` and only performs network work after the explicit flag:

```powershell
apps/backend/.venv/Scripts/python.exe evals/run_langsmith.py --execute --corpus-snapshot verified-YYYY-MM-DD
```

The report metadata records dataset version, application commit and corpus
snapshot. Inputs and outputs are hidden in the LangSmith client configuration;
the script never prints the key.
