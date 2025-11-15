import re
import time
import json
import imaplib
import email
import os
from typing import Optional, Tuple, Dict, Any, List

try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    REQUESTS_AVAILABLE = False


TIKTOK_SUBJECT_HINTS = [
    "verification code",
    "mã xác minh",
    "verification",
    "security code",
    "verification for tiktok",
    "xác minh tiktok",
    "tiktok code",
    "mã tiktok",
]

TIKTOK_SENDER_HINTS = [
    "no-reply@account.tiktok.com",
    "no-reply@tiktok.com",
    "account@tiktok.com",
    "security@tiktok.com",
]

CODE_REGEX_LIST = [
    re.compile(r"\b(\d{6})\b"),  # 6-digit code
    re.compile(r"code[:\s]+(\d{6})", re.IGNORECASE),
    re.compile(r"verification\s*code[:\s]+(\d{6})", re.IGNORECASE),
]


def parse_account_line(line: str) -> Dict[str, Any]:
    """
    Parse 3 biến thể tài khoản:
      1) username|password
      2) username|password|hotmail_username|hotmail_password
      3) username|password|hotmail_username|hotmail_password|session_token|token_id(optional)
    Trả về dict chuẩn hoá.
    """
    if not line:
        return {}
    parts = [p.strip() for p in str(line).strip().split("|")]
    result = {
        "username": None,
        "password": None,
        "login": None,
        "hotmail_user": None,
        "hotmail_pass": None,
        "session_token": None,
        "token_id": None,
        "raw": line,
        "otp_email": None,
        "variant": None,
    }
    if len(parts) >= 2:
        result["username"] = parts[0]
        result["password"] = parts[1]
        result["login"] = parts[0]
        result["email"] = parts[0]
    if len(parts) == 2:
        result["variant"] = 1
        return result
    if len(parts) == 4:
        result["variant"] = 2
        result["hotmail_user"] = parts[2]
        result["hotmail_pass"] = parts[3]
        result["otp_email"] = parts[2]
        result["email"] = parts[0]
        return result
    if 5 <= len(parts) <= 6:
        result["variant"] = 3
        result["hotmail_user"] = parts[2]
        result["hotmail_pass"] = parts[3]
        result["session_token"] = parts[4]
        if len(parts) >= 6:
            result["token_id"] = parts[5]
        result["otp_email"] = parts[2]
        result["email"] = parts[0]
        return result
    # Fallback
    result["variant"] = 0
    return result


def _match_tiktok_email(msg: email.message.Message) -> bool:
    try:
        subject = msg.get("Subject", "") or ""
        from_ = msg.get("From", "") or ""
        subj_lower = subject.lower()
        from_lower = from_.lower()
        if any(h in subj_lower for h in TIKTOK_SUBJECT_HINTS):
            return True
        if any(h in from_lower for h in TIKTOK_SENDER_HINTS):
            return True
        return False
    except Exception:
        return False


def _extract_code_from_message(msg: email.message.Message) -> Optional[str]:
    # Try subject first
    subject = msg.get("Subject", "") or ""
    for rx in CODE_REGEX_LIST:
        m = rx.search(subject)
        if m:
            return m.group(1)
    # Then body
    try:
        payload_texts: List[str] = []
        if msg.is_multipart():
            for part in msg.walk():
                ctype = (part.get_content_type() or "").lower()
                if ctype in ("text/plain", "text/html"):
                    try:
                        payload_texts.append(part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore"))
                    except Exception:
                        try:
                            payload_texts.append(part.get_payload(decode=True).decode("utf-8", errors="ignore"))
                        except Exception:
                            pass
        else:
            payload_texts.append(msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="ignore"))
        body = "\n".join(payload_texts)
        for rx in CODE_REGEX_LIST:
            m = rx.search(body)
            if m:
                return m.group(1)
    except Exception:
        pass
    return None


def fetch_hotmail_code_imap(email_addr: str, password: str, timeout_sec: int = 120, poll_interval: float = 4.0) -> Optional[str]:
    """
    Đọc mã từ Hotmail/Outlook qua IMAP (outlook.office365.com).
    Cần bật IMAP cho tài khoản. Đợi tối đa timeout_sec.
    """
    start = time.time()
    host = "outlook.office365.com"
    mailbox = "INBOX"
    attempt = 0
    while time.time() - start < timeout_sec:
        attempt += 1
        try:
            print(f"[IMAP] Attempt {attempt}: Connecting to {host}...")
            M = imaplib.IMAP4_SSL(host)
            print(f"[IMAP] Logging in as {email_addr}...")
            M.login(email_addr, password)
            print(f"[IMAP] Selecting mailbox {mailbox}...")
            M.select(mailbox)
            typ, data = M.search(None, "ALL")
            if typ == "OK":
                ids = data[0].split()
                print(f"[IMAP] Found {len(ids)} emails, checking last 50 for TikTok codes...")
                checked = 0
                for msg_id in reversed(ids[-50:]):  # chỉ quét gần đây để nhanh
                    typ, msg_data = M.fetch(msg_id, "(RFC822)")
                    if typ != "OK" or not msg_data:
                        continue
                    try:
                        raw = msg_data[0][1]
                        msg = email.message_from_bytes(raw)
                        checked += 1
                        if not _match_tiktok_email(msg):
                            continue
                        print(f"[IMAP] Found TikTok email! Extracting code...")
                        code = _extract_code_from_message(msg)
                        if code:
                            print(f"[IMAP] Success! Code: {code}")
                            M.logout()
                            return code
                    except Exception as e:
                        print(f"[IMAP] Error processing email: {e}")
                        continue
                print(f"[IMAP] Checked {checked} emails, no TikTok code found. Waiting {poll_interval}s...")
            else:
                print(f"[IMAP] Search failed: {typ}")
            M.logout()
        except imaplib.IMAP4.error as e:
            print(f"[IMAP] IMAP error: {e}")
            if "AUTHENTICATE" in str(e) or "LOGIN" in str(e):
                print(f"[IMAP] Authentication failed. Check email/password or enable IMAP in account settings.")
                return None
        except Exception as e:
            print(f"[IMAP] Error: {type(e).__name__}: {e}")
        time.sleep(poll_interval)
    print(f"[IMAP] Timeout after {timeout_sec}s, no code found.")
    return None


def fetch_hotmail_code_graph(email_addr: str, refresh_token: str, client_id: str = None, timeout_sec: int = 120, poll_interval: float = 4.0) -> Optional[str]:
    """
    Đọc mã qua Microsoft Graph API.
    Nếu có client_id, sẽ dùng refresh_token để lấy access_token trước.
    Nếu không có client_id, giả định refresh_token thực ra là access_token.
    """
    if not REQUESTS_AVAILABLE:
        return None
    
    access_token = refresh_token  # Mặc định coi như access token
    
    # Nếu có client_id, refresh token để lấy access token
    if client_id and refresh_token:
        try:
            token_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
            token_data = {
                'client_id': client_id,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token',
                'scope': 'Mail.Read'
            }
            token_resp = requests.post(token_url, data=token_data, timeout=10)
            if token_resp.status_code == 200:
                token_result = token_resp.json()
                access_token = token_result.get('access_token')
                if not access_token:
                    return None
            else:
                # Refresh token thất bại, có thể đã là access token hoặc token không hợp lệ
                pass
        except Exception:
            # Nếu refresh thất bại, thử dùng trực tiếp như access token
            pass
    
    if not access_token:
        return None
    
    start = time.time()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    # API: List messages (top mới nhất)
    url = f"https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages?$top=25&$select=subject,from,receivedDateTime,bodyPreview"
    while time.time() - start < timeout_sec:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 401:
                # Token hết hạn/không hợp lệ
                return None
            if resp.status_code >= 400:
                time.sleep(poll_interval)
                continue
            data = resp.json()
            items = data.get("value", []) if isinstance(data, dict) else []
            for it in items:
                subject = (it.get("subject") or "")
                from_addr = (((it.get("from") or {}).get("emailAddress") or {}).get("address") or "")
                body_preview = (it.get("bodyPreview") or "")
                subj_lower = subject.lower()
                from_lower = str(from_addr).lower()
                if any(h in subj_lower for h in TIKTOK_SUBJECT_HINTS) or any(h in from_lower for h in TIKTOK_SENDER_HINTS):
                    # Tìm code trong subject trước, rồi body preview
                    for rx in CODE_REGEX_LIST:
                        m = rx.search(subject) or rx.search(body_preview)
                        if m:
                            return m.group(1)
        except Exception:
            pass
        time.sleep(poll_interval)
    return None


def get_login_otp_from_hotmail(account_line: str, prefer_graph: bool = True, timeout_sec: int = 150) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Tổng hợp lấy OTP từ Hotmail dựa trên 3 biến thể tài khoản.
    Trả về: (ok, code, info_dict)
      - ok: True/False
      - code: chuỗi 6 số hoặc None
      - info_dict: thông tin đã parse + nguồn (imap/graph)
    """
    info = parse_account_line(account_line)
    info_out = dict(info)
    info_out["source"] = None
    code: Optional[str] = None

    # Không có thông tin hotmail thì không thể lấy OTP
    if not info.get("hotmail_user"):
        return False, None, info_out

    # Ưu tiên Graph nếu có token và được chọn
    if prefer_graph and info.get("session_token"):
        client_id = info.get("token_id")  # token_id trong format là client_id
        code = fetch_hotmail_code_graph(info["hotmail_user"], info["session_token"], client_id=client_id, timeout_sec=timeout_sec)
        if code:
            info_out["source"] = "graph"
            return True, code, info_out

    # Fallback sang IMAP nếu có mật khẩu
    if info.get("hotmail_user") and info.get("hotmail_pass"):
        print(f"[OTP] Trying IMAP method for {info['hotmail_user']}...")
        code = fetch_hotmail_code_imap(info["hotmail_user"], info["hotmail_pass"], timeout_sec=timeout_sec)
        if code:
            info_out["source"] = "imap"
            return True, code, info_out
        else:
            print(f"[OTP] IMAP method failed or no code found.")

    return False, None, info_out


