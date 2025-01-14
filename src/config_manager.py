import json
import os
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ConnectionConfig:
    name: str
    host: str
    port: int
    password: str
    db: int
    last_used: str

class ConfigManager:
    def __init__(self):
        self.config_file = os.path.join(os.path.expanduser("~"), ".redis-gui", "config.json")
        self._ensure_config_dir()
        self.connections: Dict[str, ConnectionConfig] = {}
        self.load_config()

    def _ensure_config_dir(self):
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                for conn in data.get('connections', []):
                    self.connections[conn['name']] = ConnectionConfig(**conn)

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({
                'connections': [vars(conn) for conn in self.connections.values()]
            }, f, indent=2)

    def add_connection(self, name: str, host: str, port: int, password: str, db: int):
        self.connections[name] = ConnectionConfig(
            name=name,
            host=host,
            port=port,
            password=password,
            db=db,
            last_used=datetime.now().isoformat()
        )
        self.save_config()

    def remove_connection(self, name: str):
        if name in self.connections:
            del self.connections[name]
            self.save_config() 