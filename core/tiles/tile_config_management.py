import os
import configparser

# --- Config functions tách ra từ chrome_manager.py ---
def load_config(manager):
    """Load configuration from file"""
    try:
        if os.path.exists(manager.config_file):
            try:
                manager.config = configparser.ConfigParser()
                manager.config.read(manager.config_file)
                return manager.config
            except:
                pass
            try:
                import json
                with open(manager.config_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content.startswith('{'):
                        json_data = json.loads(content)
                        manager.config = configparser.ConfigParser()
                        for section, values in json_data.items():
                            manager.config[section] = values
                        return manager.config
            except:
                pass
            manager.config = create_default_config(manager)
            return manager.config
        else:
            manager.config = create_default_config(manager)
            return manager.config
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        manager.config = create_default_config(manager)
        return manager.config

def create_default_config(manager):
    """Create default configuration file"""
    manager.config = configparser.ConfigParser()
    manager.config['SETTINGS'] = {
        'auto_start': 'false',
        'hidden_mode': 'true',
        'max_profiles': '10',
        'startup_delay': '5'
    }
    manager.config['PROFILES'] = {}
    save_config(manager)
    return manager.config

def save_config(manager):
    """Save configuration to file"""
    try:
        if isinstance(manager.config, dict):
            import json
            with open(manager.config_file, 'w', encoding='utf-8') as f:
                json.dump(manager.config, f, indent=2, ensure_ascii=False)
        else:
            with open(manager.config_file, 'w', encoding='utf-8') as f:
                manager.config.write(f)
    except Exception as e:
        print(f"Error saving config: {str(e)}")
