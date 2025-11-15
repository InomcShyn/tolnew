import os
import sys

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from core.tiles.tile_email_otp import parse_account_line, get_login_otp_from_hotmail


def main() -> int:
    """
    Quick helper to fetch the latest TikTok OTP from a Hotmail/Outlook inbox.

    Usage:
        set ACCOUNT_LINE=username|password|hotmail|hotmail_password[|refresh_token|client_id]
        python tools/test_hotmail_otp.py
    """
    account_line = os.environ.get("ACCOUNT_LINE")

    if len(sys.argv) > 1:
        account_line = sys.argv[1]

    if not account_line:
        print(
            "[WARN] Missing account line.\n"
            "Please provide one of the following ways:\n"
            "  - export ACCOUNT_LINE=\"username|password|hotmail|hotmail_pass\"\n"
            "  - python tools/test_hotmail_otp.py \"username|password|hotmail|hotmail_pass\"\n"
            "The line must match account type 2 or 3 (includes Hotmail credentials)."
        )
        return 1

    parsed = parse_account_line(account_line)
    variant = parsed.get("variant")
    if variant not in (2, 3):
        print(
            "[ERROR] Account line must be type 2 or 3:\n"
            "  type 2: username|password|hotmail|hotmail_pass\n"
            "  type 3: username|password|hotmail|hotmail_pass|refresh_token|client_id"
        )
        return 2

    prefer_graph = variant == 3
    timeout_sec = 120
    print(f"[INFO] Fetching OTP (prefer_graph={prefer_graph}, timeout={timeout_sec}s)")

    success, code, info = get_login_otp_from_hotmail(
        account_line,
        prefer_graph=prefer_graph,
        timeout_sec=timeout_sec
    )

    if success and code:
        print(f"[OK] OTP: {code}")
        if info:
            print(f"[INFO] Details: {info}")
        return 0

    print("[ERROR] Failed to retrieve OTP.")
    if info:
        print(f"[INFO] Details: {info}")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())

