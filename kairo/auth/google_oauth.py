"""Google OAuth helper: performs auth code flow and token refresh.

This module opens the browser, starts a temporary HTTP server to receive
the redirect with the authorization code, exchanges the code for tokens,
and persists tokens via the TokenStore.
"""

from __future__ import annotations

import json
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from typing import Dict, Optional

import requests

from kairo.config.settings import settings
from kairo.storage.oauth_store import TokenStore


class _CodeHandler(BaseHTTPRequestHandler):
    server_version = "KairoOAuth/0.1"

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        code = qs.get("code", [None])[0]
        state = qs.get("state", [None])[0]
        self.server.code = code
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>You may now close this window.</h1></body></html>")


def _start_local_server(port: int = 0, timeout: int = 120) -> tuple[HTTPServer, str]:
    server = HTTPServer(("", port), _CodeHandler)
    # Run server in separate thread
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    return server, f"http://localhost:{server.server_port}/"


def run_oauth_flow(provider_name: str = "google") -> Dict[str, str]:
    """Perform OAuth Authorization Code flow for Google and persist tokens.

    Returns the token dict saved.
    """
    client_id = settings.google_client_id
    client_secret = settings.google_client_secret
    redirect = settings.google_redirect_uri or "http://localhost:8080/"
    scopes = settings.google_scopes or "openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/calendar.events https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/documents.readonly"

    if not client_id or not client_secret:
        raise RuntimeError("Google client_id/client_secret not configured in settings")

    # Build authorization URL
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&scope={requests.utils.requote_uri(scopes)}"
        f"&redirect_uri={requests.utils.requote_uri(redirect)}"
        f"&access_type=offline&prompt=consent"
    )

    # Start local server
    server = HTTPServer(("", 0), _CodeHandler)
    port = server.server_port
    redirect_uri = f"http://localhost:{port}/"

    # Rebuild auth_url with the actual random port redirect
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&scope={requests.utils.requote_uri(scopes)}"
        f"&redirect_uri={requests.utils.requote_uri(redirect_uri)}"
        f"&access_type=offline&prompt=consent"
    )

    webbrowser.open(auth_url)

    # Serve single request for the code
    server.handle_request()
    code = getattr(server, "code", None)
    if not code:
        raise RuntimeError("Authorization code not received")

    # Exchange code for tokens
    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
        timeout=15,
    )
    token_resp.raise_for_status()
    token_json = token_resp.json()

    # Compute expires_at (epoch)
    expires_in = token_json.get("expires_in")
    if expires_in:
        token_json["expires_at"] = int(time.time()) + int(expires_in)

    # Persist token
    store = TokenStore()
    store.save_token(provider_name, token_json)
    return token_json


def refresh_token(provider_name: str = "google") -> Dict[str, str]:
    """Refresh OAuth access token using refresh_token stored in TokenStore."""
    store = TokenStore()
    token = store.get_token(provider_name)
    if not token or "refresh_token" not in token:
        raise RuntimeError("No refresh token available")

    client_id = settings.google_client_id
    client_secret = settings.google_client_secret
    if not client_id or not client_secret:
        raise RuntimeError("Google client_id/client_secret not configured in settings")

    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": token["refresh_token"],
            "grant_type": "refresh_token",
        },
        timeout=15,
    )
    resp.raise_for_status()
    new_token = resp.json()
    expires_in = new_token.get("expires_in")
    if expires_in:
        new_token["expires_at"] = int(time.time()) + int(expires_in)

    # preserve refresh_token
    if "refresh_token" not in new_token and "refresh_token" in token:
        new_token["refresh_token"] = token["refresh_token"]

    store.save_token(provider_name, new_token)
    return new_token
