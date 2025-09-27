import argparse
import os
import sys
from chrome_manager import ChromeProfileManager


def main():
    parser = argparse.ArgumentParser(
        description="Test fetch TikTok 2FA code via Microsoft Graph from a single account line"
    )
    parser.add_argument(
        "--line",
        help=(
            "Account line (formats supported by the app, including the Hotmail Graph variant: "
            "username|password|hotmail_email|hotmail_password|ms_refresh_token|ms_client_id"
        ),
    )
    parser.add_argument(
        "--file",
        help="Path to a text file containing a single account line (first non-empty line will be used)",
    )
    parser.add_argument(
        "--refresh-token",
        dest="refresh_token",
        help="Microsoft Graph refresh token (alternative to --line/--file)",
    )
    parser.add_argument(
        "--client-id",
        dest="client_id",
        help="Microsoft app client ID (used with --refresh-token)",
    )
    parser.add_argument(
        "--email",
        help="Optional Hotmail address used when constructing a minimal account line",
    )
    parser.add_argument(
        "--device-login",
        action="store_true",
        help="Use Microsoft device code flow to get an access token (no refresh token needed)",
    )
    parser.add_argument(
        "--refresh-token-file",
        help="Path to JSON file containing saved Microsoft Graph tokens",
    )

    args = parser.parse_args()

    account_line = None
    
    # Load saved refresh token first (nếu có)
    if args.refresh_token_file:
        try:
            import json
            with open(args.refresh_token_file, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
            
            refresh_token = token_data.get("refresh_token")
            client_id = token_data.get("client_id", "9e5f94bc-e8a4-4e73-b8be-63364c29d753")
            email = token_data.get("email", "placeholder@example.com")
            
            if refresh_token:
                print(f"✅ Đã tải refresh token từ file: {args.refresh_token_file}")
                account_line = f"u|p|{email}|ep|{refresh_token}|{client_id}"
            else:
                print(f"❌ Không tìm thấy refresh_token trong file: {args.refresh_token_file}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Lỗi đọc file token: {e}")
            sys.exit(1)
    
    # Optional device login first
    elif args.device_login:
        try:
            import msal  # type: ignore
            client_id = args.client_id or "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
            app = msal.PublicClientApplication(client_id, authority="https://login.microsoftonline.com/consumers")
            flow = app.initiate_device_flow(scopes=["Mail.Read","User.Read"])
            print(flow.get("message", "Open browser and complete the device code flow"))
            result = app.acquire_token_by_device_flow(flow)
            token = result.get("access_token")
            if not token:
                print(f"FAIL - Device login failed: {result}")
                sys.exit(1)
            os.environ["MS_ACCESS_TOKEN"] = token
            # Build minimal line for parser
            email = args.email or "placeholder@example.com"
            account_line = f"u|p|{email}|ep||{client_id}"
        except Exception as e:
            print(f"FAIL - Device login error: {e}")
            sys.exit(1)
    if args.line:
        account_line = args.line.strip()
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                for ln in f:
                    ln = ln.strip()
                    if ln:
                        account_line = ln
                        break
        except Exception as e:
            print(f"FAIL - Cannot read file: {e}")
            sys.exit(1)
    elif args.refresh_token and args.client_id:
        # Build a minimal compatible line for the parser (placeholders for fields not needed)
        email = args.email or "placeholder@example.com"
        account_line = f"u|p|{email}|ep|{args.refresh_token}|{args.client_id}"
    else:
        print("Usage: python test_tiktok_code.py --line \"<account_line>\" | --file <path> | --refresh-token <rt> --client-id <cid> [--email you@outlook.com] | --refresh-token-file <token.json>")
        sys.exit(2)

    if not account_line:
        print("FAIL - No account line provided")
        sys.exit(2)

    manager = ChromeProfileManager()
    ok, msg = manager.test_graph_mail_fetch(account_line)
    print(("OK - " if ok else "FAIL - ") + msg)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()


