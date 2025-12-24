# Core Utilities

Utility modules for Chrome Profile Manager

## proxy_utils.py

Proxy utilities for parsing, validating and cleaning proxy strings.

### Functions

#### `parse_proxy_string(proxy_string)`
Parse proxy string into components.

**Supported formats:**
- `http://server:port:username:password`
- `socks4://server:port:username:password`
- `socks5://server:port:username:password`
- `server:port:username:password` (defaults to http)
- `http://server:port` (no auth)
- `server:port` (no auth, defaults to http)

**Returns:** `dict` with keys: `protocol`, `server`, `port`, `username`, `password`

**Example:**
```python
from core.utils.proxy_utils import parse_proxy_string

proxy = parse_proxy_string("http://27.79.170.112:10009:user:pass")
# Returns: {
#     'protocol': 'http',
#     'server': '27.79.170.112',
#     'port': '10009',
#     'username': 'user',
#     'password': 'pass'
# }
```

#### `parse_proxy_list(proxy_text)`
Parse multi-line proxy text into list of cleaned proxy strings.

**Features:**
- Strips whitespace
- Removes empty lines
- Removes 'null' entries
- Auto-fixes duplicate protocols

**Example:**
```python
from core.utils.proxy_utils import parse_proxy_list

text = """
http://http://27.79.170.112:10009:user:pass
socks5://172.16.0.3:10001:user:pass

null
"""

proxies = parse_proxy_list(text)
# Returns: [
#     'http://27.79.170.112:10009:user:pass',
#     'socks5://172.16.0.3:10001:user:pass'
# ]
```

#### `fix_duplicate_protocol(proxy_string)`
Fix duplicate protocol in proxy string.

**Example:**
```python
from core.utils.proxy_utils import fix_duplicate_protocol

fixed = fix_duplicate_protocol("http://http://server:port")
# Returns: "http://server:port"
```

#### `format_proxy_string(protocol, server, port, username='', password='')`
Format proxy components into standard string.

**Example:**
```python
from core.utils.proxy_utils import format_proxy_string

proxy = format_proxy_string('http', '27.79.170.112', '10009', 'user', 'pass')
# Returns: "http://27.79.170.112:10009:user:pass"
```

#### `format_proxy_url(protocol, server, port, username='', password='')`
Format proxy components into URL format (for Chrome).

**Example:**
```python
from core.utils.proxy_utils import format_proxy_url

url = format_proxy_url('http', '27.79.170.112', '10009', 'user', 'pass')
# Returns: "http://user:pass@27.79.170.112:10009"
```

#### `validate_proxy_format(proxy_string)`
Validate proxy string format.

**Returns:** `tuple` of `(is_valid: bool, error_message: str)`

**Example:**
```python
from core.utils.proxy_utils import validate_proxy_format

is_valid, message = validate_proxy_format("http://27.79.170.112:10009")
# Returns: (True, "Valid proxy format")

is_valid, message = validate_proxy_format("invalid")
# Returns: (False, "Failed to parse proxy 'invalid': ...")
```

#### `normalize_proxy_string(proxy_string)`
Normalize proxy string to standard format.

**Example:**
```python
from core.utils.proxy_utils import normalize_proxy_string

normalized = normalize_proxy_string("http://http://27.79.170.112:10009:user:pass")
# Returns: "http://27.79.170.112:10009:user:pass"

normalized = normalize_proxy_string("27.79.170.112:10009:user:pass")
# Returns: "http://27.79.170.112:10009:user:pass"
```

#### `extract_proxy_info(proxy_string)`
Extract human-readable proxy information.

**Example:**
```python
from core.utils.proxy_utils import extract_proxy_info

info = extract_proxy_info("http://27.79.170.112:10009:user:pass")
# Returns: "HTTP 27.79.170.112:10009 (auth: user)"
```

## Usage in Code

### In GUI (core/gui_manager_modern.py)
```python
from core.utils.proxy_utils import parse_proxy_list

# Parse proxy list from text box
proxy_text = bulk_proxy_text.get('1.0', tk.END).strip()
proxy_list = parse_proxy_list(proxy_text) if proxy_text else []
```

### In Tiles (core/tiles/tile_profile_management.py)
```python
from core.utils.proxy_utils import parse_proxy_string

# Parse proxy for profile creation
proxy_config = parse_proxy_string(proxy_string)
```

### In Proxy Management (core/tiles/tile_proxy_management.py)
```python
from core.utils.proxy_utils import fix_duplicate_protocol

# Fix duplicate protocol before setting
proxy_string = fix_duplicate_protocol(proxy_string)
```
