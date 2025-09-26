# Agente Astrolaboral (completo)

Asistente conversacional para **Astrolaboral**. Guarda leads en `data/leads.csv` o en Google Sheets (si configurás).

## Inicio rápido local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --reload --port 7860
```
Abrí: http://localhost:7860/widget

## Google Sheets
- Configurá `GOOGLE_SHEETS_ID` y `GOOGLE_SERVICE_ACCOUNT_JSON` para guardar leads en tu hoja.

## Render deploy
- Subí este repo a GitHub.
- En Render: New → Blueprint → seleccioná tu repo.
- Variables de entorno: `OPENAI_API_KEY`, `GOOGLE_SHEETS_ID`, `GOOGLE_SERVICE_ACCOUNT_JSON`.
