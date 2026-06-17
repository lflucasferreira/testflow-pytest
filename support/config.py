import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:5050")
DEMO_EMAIL = os.getenv("DEMO_EMAIL", "demo@automation.io")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "Demo123!")
SERVICE_CLIENT_ID = os.getenv("SERVICE_CLIENT_ID", "testflow-service")
SERVICE_CLIENT_SECRET = os.getenv("SERVICE_CLIENT_SECRET", "service-secret")
