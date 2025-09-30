import json
import os

ALLOWED_ORIGINS = json.loads(
    os.getenv
        ("ALLOWED_ORIGINS", ' ["http://0.0.0.0:5173", "http://localhost:5173", "http://127.0.0.1:5173"]')
)


