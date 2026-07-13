from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

AUDIT_LOG_FILE = LOG_DIR / "audit_log.csv"

# if score >= this, we send it to the LLM stage
RISK_THRESHOLD = 40

OLLAMA_URL = "http://localhost:11434/api/generate"
PRODUCTION_MODEL = "mistral:7b"
DEMO_MODEL = "llama3.2:3b"
MODEL_NAME = DEMO_MODEL
DEFAULT_CLASSIFICATION_REPEATS = 1
