# Project Structure Overview

## 📁 Directory Organization

### Core Application (`core/`)
- `chrome_manager.py` - Main Chrome profile manager
- `gui_manager_modern.py` - Modern GUI interface
- `requirements.txt` - Python dependencies
- `config.ini` - Main configuration file

### Configuration (`config/`)
- `auto_2fa_config.json` - 2FA automation settings
- `gpm_config.json` - GPM Login configuration
- `bulk_run_data.json` - Bulk run data storage
- `ms_token_*.json` - Microsoft Graph tokens

### Documentation (`docs/`)
- `README.md` - Main project documentation
- `CHROME_OPTIMIZATION_GUIDE.md` - Chrome optimization guide
- `MICROSOFT_GRAPH_2FA_GUIDE.md` - 2FA setup guide
- `PROXY_INPUT_GUIDE.md` - Proxy configuration guide

### Tools (`tools/`)
- `convert_gpm_to_nkt.py` - GPM to NKT conversion tool
- `fix_syntax.py` - Syntax fix utility
- `gpm_profile_manager.py` - GPM-style profile manager
- `chrome_manager_backup.py` - Backup of chrome manager

### Data Storage (`data/`)
- `chrome_profiles/` - Chrome browser profiles
- `chrome_binaries/` - Chrome browser binaries
- `chrome_data/` - Chrome data directory
- `sessions/` - Session storage
- `logs/` - Application logs

### Extensions (`extensions/`)
- `extensions/` - Browser extensions and add-ons
  - `NKT_Branding/` - NKT browser branding
  - `ProfileTitle_*/` - Profile title extensions
  - `SwitchyOmega3_Real/` - Proxy switching extension

### Network (`network/`)
- `pac_files/` - Proxy Auto-Configuration files
  - `advanced_proxy.pac` - Advanced proxy configuration

### Authentication (`auth/`)
- `get2fa/` - 2FA and authentication modules
  - `msgraph_reader.py` - Microsoft Graph API reader
  - `requirements.txt` - 2FA module dependencies

### Backups (`backups/`)
- `backups/` - Backup files and archives
  - Various backup files with timestamps

## 🔧 Usage

### Running the Application
```bash
# From project root
python core/gui_manager_modern.py

# Or if you want to run from core directory
cd core
python gui_manager_modern.py
```

### Converting GPM Profiles
```bash
python tools/convert_gpm_to_nkt.py <gpm_path> <nkt_path>
```

### Configuration
- Main config: `core/config.ini`
- 2FA config: `config/auto_2fa_config.json`
- GPM config: `config/gpm_config.json`

## 📋 File Locations

- **Chrome Profiles**: `data/chrome_profiles/`
- **Chrome Binaries**: `data/chrome_binaries/`
- **Extensions**: `extensions/`
- **Logs**: `data/logs/`
- **Sessions**: `data/sessions/`
- **Proxy Files**: `network/pac_files/`

## 🚀 Quick Start

1. Install dependencies: `pip install -r core/requirements.txt`
2. Configure settings: Edit `core/config.ini`
3. Run application: `python core/gui_manager_modern.py`
4. Create profiles: Use GUI to create Chrome profiles
5. Convert GPM: Use `tools/convert_gpm_to_nkt.py` if needed

## 📝 Notes

- All paths in configuration files may need updating after reorganization
- Chrome profiles will continue to work from their new location
- Extensions will be automatically detected in their new location
- Backup files are preserved in `backups/` directory
