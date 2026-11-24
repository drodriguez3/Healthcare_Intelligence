# IronGate Healthcare Enterprise Intelligence V3
Independent concept for Prisma Health. Synthetic data and fictional policies. No live Snowflake connection. Local rule-based analytics, TF-IDF lexical retrieval (not semantic embeddings), and template-based investigation combining both. Free text is supported only for recognized analytical intents. No LLM or autonomous agent.

Run in VS Code PowerShell:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Deploy app.py, engine.py, requirements.txt and data/ to Streamlit Community Cloud. Never commit credentials. Live Cortex Analyst, Search and Agents require separately configured Snowflake services, authentication and integration; not included here.
