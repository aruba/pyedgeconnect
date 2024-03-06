import getpass
import os

import requests
from dotenv import load_dotenv

load_dotenv()

SSE_ADMIN_BASE_URL = "https://admin-api.axissecurity.com/api/v1"

if os.getenv("SSE_ADMIN_TOKEN") is not None:
    sse_admin_token = os.getenv("SSE_ADMIN_TOKEN")
else:
    sse_admin_token = getpass.getpass("Enter SSE Admin Token: ")

sse_admin_session = requests.Session()
sse_admin_session.headers["Authorization"] = f"Bearer {sse_admin_token}"

apply_sse_updates = sse_admin_session.post(
    f"{SSE_ADMIN_BASE_URL}/Commit",
    allow_redirects=False,
    data={},
)

if apply_sse_updates.status_code == 204:
    print("Changes successfully committed in SSE")
else:
    print("Changes failed to be committed in SSE")
