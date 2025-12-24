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


def fetch_hotmail_code_graph(email_addr: str, refresh_token: str, client_id: str = None, timeout_sec: int = 120, poll_interval: float = 4.0, initial_delay: float = 10.0, allow_old_codes: bool = False) -> Optional[str]:
    """
    Đọc mã qua Microsoft Graph API.
    Nếu có client_id, sẽ dùng refresh_token để lấy access_token trước.
    Nếu không có client_id, giả định refresh_token thực ra là access_token.
    
    Args:
        email_addr: Email address
        refresh_token: OAuth2 refresh token hoặc access token
        client_id: OAuth2 client ID (optional)
        timeout_sec: Timeout tổng (giây)
        poll_interval: Khoảng thời gian giữa các lần check (giây)
        initial_delay: Delay trước khi bắt đầu check (giây) - tránh lấy code cũ khi có captcha
        allow_old_codes: Cho phép lấy code cũ nếu không có code mới (dùng cho test)
    
    Returns:
        6-digit code hoặc None
    """
    if not REQUESTS_AVAILABLE:
        return None
    
    # ✅ DELAY 10s trước khi bắt đầu - tránh lấy code cũ khi giải captcha
    if initial_delay > 0:
        print(f"[HOTMAIL-GRAPH] Waiting {initial_delay}s before checking (avoid old codes)...")
        time.sleep(initial_delay)
    
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
    
    # ✅ Lưu thời gian bắt đầu để chỉ lấy email mới hơn thời điểm này
    check_start_time = time.time()
    
    # ✅ SMART LOGIC: 
    # - Lần đầu check: Lấy email trong 5 PHÚT gần đây (tránh code cũ)
    # - Các lần sau: Chờ email MỚI HƠN lần check trước
    first_check_threshold = 300  # 5 phút
    min_email_time_first_check = check_start_time - first_check_threshold
    
    print(f"[HOTMAIL-GRAPH] Mode: Get LATEST TikTok email (within {first_check_threshold}s on first check)")
    
    # API: List messages (top mới nhất) - thêm receivedDateTime để sort
    url = f"https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages?$top=25&$select=subject,from,receivedDateTime,bodyPreview&$orderby=receivedDateTime DESC"
    
    attempt = 0
    last_checked_email_time = None  # Track email đã check để tránh lấy lại
    while time.time() - start < timeout_sec:
        attempt += 1
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 401:
                # Token hết hạn/không hợp lệ
                print(f"[HOTMAIL-GRAPH] Token expired or invalid (401)")
                return None
            if resp.status_code >= 400:
                print(f"[HOTMAIL-GRAPH] API error {resp.status_code}, retrying...")
                time.sleep(poll_interval)
                continue
            
            data = resp.json()
            items = data.get("value", []) if isinstance(data, dict) else []
            
            # ✅ SIMPLIFIED: Tìm email TikTok MỚI NHẤT (không filter thời gian)
            tiktok_emails = []
            
            for it in items:
                subject = (it.get("subject") or "")
                from_addr = (((it.get("from") or {}).get("emailAddress") or {}).get("address") or "")
                body_preview = (it.get("bodyPreview") or "")
                received_time_str = it.get("receivedDateTime", "")
                
                subj_lower = subject.lower()
                from_lower = str(from_addr).lower()
                
                # Check if TikTok email
                if any(h in subj_lower for h in TIKTOK_SUBJECT_HINTS) or any(h in from_lower for h in TIKTOK_SENDER_HINTS):
                    # Extract code (không cần parse time)
                    for rx in CODE_REGEX_LIST:
                        m = rx.search(subject) or rx.search(body_preview)
                        if m:
                            code = m.group(1)
                            # Parse time - IMPORTANT: Email time is UTC, convert properly
                            try:
                                from datetime import datetime, timezone
                                # Parse as UTC time (email has 'Z' suffix = UTC)
                                received_dt_str = received_time_str.replace('Z', '+00:00').split('+')[0]
                                received_dt = datetime.strptime(received_dt_str, '%Y-%m-%dT%H:%M:%S')
                                # Mark as UTC timezone
                                received_dt_utc = received_dt.replace(tzinfo=timezone.utc)
                                # Convert to timestamp (always UTC-based)
                                received_timestamp = received_dt_utc.timestamp()
                            except Exception as e:
                                # Fallback: use current time
                                received_timestamp = time.time()
                            
                            tiktok_emails.append({
                                'code': code,
                                'time': received_timestamp,
                                'subject': subject,
                                'received_str': received_time_str
                            })
                            break
            
            # ✅ Nếu có email TikTok, lấy email MỚI NHẤT (time lớn nhất)
            if tiktok_emails:
                # Sort by time descending (mới nhất lên đầu)
                tiktok_emails.sort(key=lambda x: x['time'], reverse=True)
                newest = tiktok_emails[0]
                
                from datetime import datetime
                age_seconds = int(time.time() - newest['time'])
                received_dt = datetime.fromtimestamp(newest['time'])
                
                # ✅ SMART CHECK:
                # - Lần đầu (attempt 1): Chỉ lấy email trong 5 phút gần đây
                # - Các lần sau: Lấy email mới hơn lần check trước
                if attempt == 1:
                    # Lần đầu: Check threshold
                    if newest['time'] >= min_email_time_first_check:
                        print(f"[HOTMAIL-GRAPH] ✅ Found {len(tiktok_emails)} TikTok email(s)")
                        print(f"[HOTMAIL-GRAPH] Using NEWEST: {newest['subject'][:60]}...")
                        print(f"[HOTMAIL-GRAPH] Received: {received_dt.strftime('%Y-%m-%d %H:%M:%S')} ({age_seconds}s ago)")
                        print(f"[HOTMAIL-GRAPH] Code: {newest['code']}")
                        return newest['code']
                    else:
                        # Email quá cũ, chờ email mới
                        print(f"[HOTMAIL-GRAPH] Found email but too old ({age_seconds}s > {first_check_threshold}s), waiting for new email...")
                        last_checked_email_time = newest['time']
                else:
                    # Các lần sau: Chỉ lấy email mới hơn lần check trước
                    if last_checked_email_time is None or newest['time'] > last_checked_email_time:
                        print(f"[HOTMAIL-GRAPH] ✅ Found NEW email!")
                        print(f"[HOTMAIL-GRAPH] Subject: {newest['subject'][:60]}...")
                        print(f"[HOTMAIL-GRAPH] Received: {received_dt.strftime('%Y-%m-%d %H:%M:%S')} ({age_seconds}s ago)")
                        print(f"[HOTMAIL-GRAPH] Code: {newest['code']}")
                        return newest['code']
                    else:
                        # Vẫn là email cũ
                        pass
            else:
                # ✅ Log progress
                elapsed = int(time.time() - start)
                remaining = timeout_sec - elapsed
                print(f"[HOTMAIL-GRAPH] Attempt {attempt}: No TikTok emails found (elapsed: {elapsed}s, remaining: {remaining}s)")
            
        except Exception as e:
            print(f"[HOTMAIL-GRAPH] Error: {e}")
            pass
        
        time.sleep(poll_interval)
    
    print(f"[HOTMAIL-GRAPH] Timeout after {timeout_sec}s - no new TikTok email received")
    
    # ✅ Fallback: Nếu allow_old_codes=True và có email TikTok cũ, lấy email mới nhất
    if allow_old_codes and latest_tiktok_email_time:
        print(f"[HOTMAIL-GRAPH] Fallback: Trying to get latest old code (allow_old_codes=True)...")
        try:
            # Fetch lại để lấy code từ email cũ nhất
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("value", [])
                
                for it in items:
                    subject = (it.get("subject") or "")
                    from_addr = (((it.get("from") or {}).get("emailAddress") or {}).get("address") or "")
                    body_preview = (it.get("bodyPreview") or "")
                    
                    subj_lower = subject.lower()
                    from_lower = str(from_addr).lower()
                    
                    if any(h in subj_lower for h in TIKTOK_SUBJECT_HINTS) or any(h in from_lower for h in TIKTOK_SENDER_HINTS):
                        for rx in CODE_REGEX_LIST:
                            m = rx.search(subject) or rx.search(body_preview)
                            if m:
                                code = m.group(1)
                                print(f"[HOTMAIL-GRAPH] Found old code: {code} (from: {subject[:50]}...)")
                                return code
        except Exception as e:
            print(f"[HOTMAIL-GRAPH] Fallback failed: {e}")
    
    print(f"[HOTMAIL-GRAPH] Possible reasons:")
    print(f"  1. TikTok hasn't sent the email yet (check spam folder)")
    print(f"  2. Email was sent before we started checking")
    print(f"  3. Email address is incorrect")
    return None


def fetch_code_from_unlimitmail(email_password: str, code_type: str = "tiktok", timeout_sec: int = 120, poll_interval: float = 5.0) -> Optional[str]:
    """
    Lấy mã xác thực từ API unlimitmail.com
    
    Args:
        email_password: Chuỗi "email|password"
        code_type: Loại mã cần lấy (mặc định: "tiktok")
        timeout_sec: Thời gian chờ tối đa (giây)
        poll_interval: Khoảng thời gian giữa các lần thử (giây)
    
    Returns:
        Mã xác thực (6 chữ số) hoặc None nếu không lấy được
    """
    if not REQUESTS_AVAILABLE:
        print("[UNLIMITMAIL] requests library not available")
        return None
    
    api_url = "https://unlimitmail.com/api/email/get-email-code"
    
    start = time.time()
    attempt = 0
    
    while time.time() - start < timeout_sec:
        attempt += 1
        try:
            print(f"[UNLIMITMAIL] Attempt {attempt}: Fetching {code_type} code for {email_password.split('|')[0]}...")
            
            payload = {
                "email_password": email_password,
                "type": code_type
            }
            
            response = requests.post(api_url, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                
                # API có thể trả về nhiều định dạng khác nhau
                # Thử các trường phổ biến
                code = None
                if isinstance(result, dict):
                    code = result.get('code') or result.get('verification_code') or result.get('otp')
                    
                    # ✅ FIX: Nếu có 'data' field
                    if not code and 'data' in result:
                        data = result['data']
                        # Nếu data là dict, tìm code trong đó
                        if isinstance(data, dict):
                            code = data.get('code') or data.get('verification_code') or data.get('otp')
                        # ✅ FIX: Nếu data là string/number, dùng trực tiếp
                        elif data:
                            code = data
                
                if code:
                    # Đảm bảo code là string và chỉ lấy số
                    code_str = str(code).strip()
                    # Tìm 6 chữ số
                    for rx in CODE_REGEX_LIST:
                        m = rx.search(code_str)
                        if m:
                            print(f"[UNLIMITMAIL] Success! Code: {m.group(1)}")
                            return m.group(1)
                    
                    # Nếu không match regex nhưng có code, trả về luôn
                    if code_str.isdigit() and len(code_str) == 6:
                        print(f"[UNLIMITMAIL] Success! Code: {code_str}")
                        return code_str
                
                print(f"[UNLIMITMAIL] Response received but no valid code found: {result}")
            else:
                print(f"[UNLIMITMAIL] API returned status {response.status_code}: {response.text}")
        
        except requests.exceptions.Timeout:
            print(f"[UNLIMITMAIL] Request timeout")
        except Exception as e:
            print(f"[UNLIMITMAIL] Error: {type(e).__name__}: {e}")
        
        # Chờ trước khi thử lại
        if time.time() - start < timeout_sec:
            print(f"[UNLIMITMAIL] Waiting {poll_interval}s before retry...")
            time.sleep(poll_interval)
    
    print(f"[UNLIMITMAIL] Timeout after {timeout_sec}s, no code found.")
    return None


def get_login_otp_from_hotmail(account_line: str, prefer_graph: bool = True, timeout_sec: int = 150, code_type: str = "tiktok", has_captcha: bool = None) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Tổng hợp lấy OTP từ Hotmail hoặc UnlimitMail API dựa trên format tài khoản.
    
    Args:
        account_line: Account string
        prefer_graph: Prefer Graph API over IMAP
        timeout_sec: Timeout in seconds
        code_type: Type of code (tiktok, facebook, etc.)
        has_captcha: True if captcha detected, False if no captcha, None if unknown (auto-detect)
    
    Hỗ trợ 4 biến thể:
      1) username|password - Kiểm tra email domain để quyết định phương thức
      2) username|password|hotmail_username|hotmail_password - Hotmail IMAP
      3) username|password|hotmail_username|hotmail_password|session_token|token_id - Hotmail Graph API
      4) email@hlongmail.com|password - Sử dụng UnlimitMail API (tự động phát hiện)
    
    Trả về: (ok, code, info_dict)
      - ok: True/False
      - code: chuỗi 6 số hoặc None
      - info_dict: thông tin đã parse + nguồn (imap/graph/unlimitmail_api)
    """
    info = parse_account_line(account_line)
    info_out = dict(info)
    info_out["source"] = None
    code: Optional[str] = None

    # Kiểm tra nếu email có đuôi @hlongmail.com -> dùng UnlimitMail API
    username = info.get("username", "")
    is_hlongmail = "@hlongmail.com" in username.lower() if username else False
    
    # Kiểm tra nếu là format đơn giản email|password (variant 1)
    # hoặc nếu không có hotmail_user
    if info.get("variant") == 1 or not info.get("hotmail_user"):
        # Nếu là @hlongmail.com -> dùng UnlimitMail API
        if is_hlongmail and info.get("username") and info.get("password"):
            email_password = f"{info['username']}|{info['password']}"
            print(f"[OTP] Detected @hlongmail.com email, using UnlimitMail API for {info['username']} (type: {code_type})...")
            try:
                code = fetch_code_from_unlimitmail(email_password, code_type=code_type, timeout_sec=timeout_sec)
                if code:
                    info_out["source"] = "unlimitmail_api"
                    info_out["code_type"] = code_type
                    return True, code, info_out
                else:
                    print(f"[OTP] UnlimitMail API failed or no code found.")
            except Exception as e:
                print(f"[OTP] UnlimitMail API error: {e}")
        
        # Nếu không có hotmail_user và không phải @hlongmail.com thì không thể lấy OTP
        if not info.get("hotmail_user"):
            if not is_hlongmail:
                print(f"[OTP] Email {username} is not @hlongmail.com and no hotmail credentials provided.")
            return False, None, info_out

    # ============================================================================
    # LOGIC MỚI: 3 LOẠI RÕ RÀNG
    # ============================================================================
    # Loại 1 (Variant 1): username|password
    #   → KHÔNG lấy OTP (return False ngay)
    # 
    # Loại 2 (Variant 2): username|password|email|email_password
    #   → Dùng UnlimitMail API (@hlongmail.com)
    # 
    # Loại 3 (Variant 3): username|password|email|email_password|session_token|token_id
    #   → Dùng Graph API
    # 
    # ⚠️ ƯU TIÊN: Nếu email là @hlongmail.com → LUÔN dùng UnlimitMail API (bất kể variant)
    # ============================================================================
    
    variant = info.get("variant")
    hotmail_user = info.get("hotmail_user", "")
    is_hlongmail = "@hlongmail.com" in hotmail_user.lower() if hotmail_user else False
    
    # ✅ LOẠI 1: Không có email OTP → KHÔNG lấy mã
    if variant == 1:
        print(f"[OTP] Variant 1 (no OTP email) - skipping OTP fetch")
        return False, None, info_out
    
    # ✅ ƯU TIÊN: Email @hlongmail.com → LUÔN dùng UnlimitMail API (bất kể variant 2 hay 3)
    if is_hlongmail and info.get("hotmail_user") and info.get("hotmail_pass"):
        email_password = f"{info['hotmail_user']}|{info['hotmail_pass']}"
        print(f"[OTP] Detected @hlongmail.com email (variant {variant}) → Using UnlimitMail API for {info['hotmail_user']} (type: {code_type})...")
        try:
            code = fetch_code_from_unlimitmail(email_password, code_type=code_type, timeout_sec=timeout_sec)
            if code:
                info_out["source"] = "unlimitmail_api"
                info_out["code_type"] = code_type
                print(f"[OTP] ✅ UnlimitMail API success: {code}")
                return True, code, info_out
            else:
                print(f"[OTP] ❌ UnlimitMail API failed or no code found.")
                return False, None, info_out
        except Exception as e:
            print(f"[OTP] ❌ UnlimitMail API error: {e}")
            import traceback
            traceback.print_exc()
            return False, None, info_out
    
    # ✅ LOẠI 2: Variant 2 (không phải @hlongmail.com) → Dùng UnlimitMail API
    # Format: username|password|email|email_password
    if variant == 2 and info.get("hotmail_user") and info.get("hotmail_pass"):
        email_password = f"{info['hotmail_user']}|{info['hotmail_pass']}"
        print(f"[OTP] Variant 2 detected → Using UnlimitMail API for {info['hotmail_user']} (type: {code_type})...")
        try:
            code = fetch_code_from_unlimitmail(email_password, code_type=code_type, timeout_sec=timeout_sec)
            if code:
                info_out["source"] = "unlimitmail_api"
                info_out["code_type"] = code_type
                print(f"[OTP] ✅ UnlimitMail API success: {code}")
                return True, code, info_out
            else:
                print(f"[OTP] ❌ UnlimitMail API failed or no code found.")
                return False, None, info_out
        except Exception as e:
            print(f"[OTP] ❌ UnlimitMail API error: {e}")
            import traceback
            traceback.print_exc()
            return False, None, info_out
    
    # ✅ LOẠI 3: Variant 3 → Dùng Graph API
    # Format: username|password|email|email_password|session_token|token_id
    if variant == 3 and prefer_graph and info.get("session_token"):
        client_id = info.get("token_id")  # token_id trong format là client_id
        print(f"[OTP] Trying Graph API for {info['hotmail_user']}...")
        
        # ✅ Smart delay based on captcha detection
        if has_captcha is None:
            # Auto-detect: Always delay 10s to be safe
            delay = 10.0
            print(f"[OTP] Captcha status unknown, using safe delay: {delay}s")
        elif has_captcha:
            # Captcha detected: Delay 10s to avoid old codes
            delay = 10.0
            print(f"[OTP] Captcha detected, delaying {delay}s to avoid old codes")
        else:
            # No captcha: No delay needed
            delay = 0.0
            print(f"[OTP] No captcha detected, checking immediately")
        
        code = fetch_hotmail_code_graph(
            info["hotmail_user"], 
            info["session_token"], 
            client_id=client_id, 
            timeout_sec=timeout_sec,
            initial_delay=delay  # ✅ Dynamic delay based on captcha
        )
        if code:
            info_out["source"] = "graph"
            return True, code, info_out

    # Fallback sang IMAP nếu có mật khẩu (variant 2)
    if info.get("hotmail_user") and info.get("hotmail_pass"):
        print(f"[OTP] Trying IMAP method for {info['hotmail_user']}...")
        code = fetch_hotmail_code_imap(info["hotmail_user"], info["hotmail_pass"], timeout_sec=timeout_sec)
        if code:
            info_out["source"] = "imap"
            return True, code, info_out
        else:
            print(f"[OTP] IMAP method failed or no code found.")

    return False, None, info_out




def get_otp_from_unlimitmail_api(email_password: str, code_type: str = "tiktok", timeout_sec: int = 120) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Lấy OTP từ unlimitmail.com API
    
    Args:
        email_password: Chuỗi "email|password"
        code_type: Loại mã cần lấy (mặc định: "tiktok")
        timeout_sec: Thời gian chờ tối đa
    
    Returns:
        (ok, code, info_dict)
        - ok: True/False
        - code: chuỗi 6 số hoặc None
        - info_dict: thông tin về request
    """
    info_out = {
        "email_password": email_password,
        "code_type": code_type,
        "source": "unlimitmail_api"
    }
    
    try:
        code = fetch_code_from_unlimitmail(email_password, code_type, timeout_sec)
        if code:
            return True, code, info_out
    except Exception as e:
        print(f"[UNLIMITMAIL] Error getting OTP: {e}")
        info_out["error"] = str(e)
    
    return False, None, info_out
