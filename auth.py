import webbrowser
import urllib.parse
import http.server
import threading
import requests
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback"
SCOPE = "openid profile email w_member_social"

auth_url = (
    "https://www.linkedin.com/oauth/v2/authorization?"
    + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    })
)

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        code = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("code", [None])[0]
        if code:
            res = requests.post("https://www.linkedin.com/oauth/v2/accessToken", data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            })
            token = res.json().get("access_token")
            with open(os.path.expanduser("~/.env"), "a") as f:
                f.write(f"\nLINKEDIN_ACCESS_TOKEN={token}")
            print(f"\nNew token: {token}")
            print("Access token saved!")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Done! You can close this tab.")
        threading.Thread(target=server.shutdown).start()

    def log_message(self, format, *args):
        pass

server = http.server.HTTPServer(("localhost", 8000), CallbackHandler)
print("Opening LinkedIn login in browser...")
webbrowser.open(auth_url)
server.serve_forever()
