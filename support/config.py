import os

BASE_URL = os.getenv("BASE_URL") or "http://localhost:5050"
DEMO_EMAIL = os.getenv("DEMO_EMAIL") or "demo@automation.io"
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD") or "Demo123!"
SERVICE_CLIENT_ID = os.getenv("SERVICE_CLIENT_ID") or "testflow-service"
SERVICE_CLIENT_SECRET = os.getenv("SERVICE_CLIENT_SECRET") or "service-secret"
