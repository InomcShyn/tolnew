import os
import time
import json
from typing import List, Optional, Dict, Any

import requests
import msal


MICROSOFT_GRAPH_SCOPE = ["https://graph.microsoft.com/.default"]
USER_READ_SCOPE = ["User.Read", "Mail.Read"]
GRAPH_BASE = "https://graph.microsoft.com/v1.0"


class GraphEmailClient:
    """Minimal Microsoft Graph email client for Outlook/Hotmail.

    Supports three auth paths:
    1) Direct access token (bearer)
    2) Refresh token (using MSAL confidential client)
    3) Device code flow (interactive, no client secret) for developer use
    """

    def __init__(
        self,
        tenant_id: str = "common",
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> None:
        self.tenant_id = tenant_id
        self.client_id = client_id or os.getenv("MS_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("MS_CLIENT_SECRET")
        self.access_token = access_token
        self.refresh_token = refresh_token

        self._confidential_app = None
        if self.client_id and self.client_secret:
            self._confidential_app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            )

    def _get_token(self) -> Optional[str]:
        # Priority: direct access token → refresh token → device code (unsupported here)
        if self.access_token:
            return self.access_token

        if self.refresh_token and self._confidential_app:
            result = self._confidential_app.acquire_token_by_refresh_token(
                refresh_token=self.refresh_token,
                scopes=USER_READ_SCOPE,
            )
            if "access_token" in result:
                self.access_token = result["access_token"]
                return self.access_token
            raise RuntimeError(f"Failed to refresh token: {result.get('error_description', result)}")

        raise RuntimeError("No access_token or refresh_token available. Provide one.")

    def _auth_headers(self) -> Dict[str, str]:
        token = self._get_token()
        return {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    def me_messages(
        self,
        top: int = 20,
        select: Optional[List[str]] = None,
        folder: Optional[str] = None,
        search: Optional[str] = None,
        orderby: str = "receivedDateTime desc",
    ) -> Dict[str, Any]:
        params = {"$top": str(top), "$orderby": orderby}
        if select:
            params["$select"] = ",".join(select)
        if search:
            # Use OData search; requires header ConsistencyLevel
            params["$search"] = search

        headers = self._auth_headers()
        if search:
            headers["ConsistencyLevel"] = "eventual"

        if folder:
            url = f"{GRAPH_BASE}/me/mailFolders/{folder}/messages"
        else:
            url = f"{GRAPH_BASE}/me/messages"

        resp = requests.get(url, headers=headers, params=params, timeout=30)
        if resp.status_code == 401:
            # attempt one refresh
            self.access_token = None
            headers = self._auth_headers()
            if search:
                headers["ConsistencyLevel"] = "eventual"
            resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_message(self, message_id: str, select: Optional[List[str]] = None) -> Dict[str, Any]:
        params = {}
        if select:
            params["$select"] = ",".join(select)
        url = f"{GRAPH_BASE}/me/messages/{message_id}"
        resp = requests.get(url, headers=self._auth_headers(), params=params, timeout=30)
        if resp.status_code == 401:
            self.access_token = None
            resp = requests.get(url, headers=self._auth_headers(), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_message_body_text(self, message_id: str) -> str:
        msg = self.get_message(message_id, select=["id", "body", "subject", "from", "receivedDateTime"])
        body = msg.get("body", {})
        content = body.get("content", "")
        return content


def load_tokens_from_env() -> Dict[str, Optional[str]]:
    return {
        "tenant_id": os.getenv("MS_TENANT_ID", "common"),
        "client_id": os.getenv("MS_CLIENT_ID"),
        "client_secret": os.getenv("MS_CLIENT_SECRET"),
        "access_token": os.getenv("MS_ACCESS_TOKEN"),
        "refresh_token": os.getenv("MS_REFRESH_TOKEN"),
    }


def get_refresh_token_interactive(client_id: str, tenant_id: str = "consumers") -> Dict[str, str]:
    """Interactive method to get refresh token for personal Microsoft accounts.
    
    This opens a browser for user to authenticate and returns tokens.
    """
    app = msal.PublicClientApplication(
        client_id=client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
    )
    
    # Try to get token silently first
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(USER_READ_SCOPE, account=accounts[0])
        if result and "access_token" in result:
            return {
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token", ""),
                "expires_in": result.get("expires_in", 0)
            }
    
    # Interactive authentication
    print(f"🌐 Mở trình duyệt để xác thực...")
    print(f"🔗 Client ID: {client_id}")
    
    result = app.acquire_token_interactive(
        scopes=USER_READ_SCOPE,
        prompt="select_account"
    )
    
    if "error" in result:
        raise RuntimeError(f"Authentication failed: {result.get('error_description', result)}")
    
    return {
        "access_token": result["access_token"],
        "refresh_token": result.get("refresh_token", ""),
        "expires_in": result.get("expires_in", 0)
    }


def example_list_latest(top: int = 10, search: Optional[str] = None) -> None:
    cfg = load_tokens_from_env()
    client = GraphEmailClient(
        tenant_id=cfg["tenant_id"],
        client_id=cfg["client_id"],
        client_secret=cfg["client_secret"],
        access_token=cfg["access_token"],
        refresh_token=cfg["refresh_token"],
    )

    data = client.me_messages(
        top=top,
        select=["id", "subject", "from", "receivedDateTime"],
        search=search,
    )
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    # Minimal CLI: set env vars and run
    import argparse
    parser = argparse.ArgumentParser(description="Read Outlook/Hotmail emails via Microsoft Graph")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--search", type=str, default=None, help="Search query, e.g. from:security@outlook.com")
    parser.add_argument("--get-refresh-token", action="store_true", help="Get refresh token interactively")
    parser.add_argument("--client-id", type=str, help="Client ID for refresh token flow")
    args = parser.parse_args()
    
    if args.get_refresh_token:
        if not args.client_id:
            print("❌ Error: --client-id required for --get-refresh-token")
            exit(1)
        
        try:
            tokens = get_refresh_token_interactive(args.client_id)
            print("\n✅ Authentication successful!")
            print(f"🔑 Access Token: {tokens['access_token'][:50]}...")
            print(f"🔄 Refresh Token: {tokens['refresh_token']}")
            print(f"⏰ Expires In: {tokens['expires_in']} seconds")
            print("\n💡 Set these environment variables:")
            print(f"set MS_ACCESS_TOKEN={tokens['access_token']}")
            print(f"set MS_REFRESH_TOKEN={tokens['refresh_token']}")
            print(f"set MS_CLIENT_ID={args.client_id}")
        except Exception as e:
            print(f"❌ Error: {e}")
            exit(1)
    else:
        example_list_latest(top=args.top, search=args.search)


