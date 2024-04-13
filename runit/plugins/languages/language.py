from pathlib import Path
from shutil import which
from ..base import Category
from ..base import Plugin
from typing import Literal

class LanguagePlugin(Plugin):
    def __init__(self, name: str, category: Literal['language', 'utility', 'visualization', 'security'], 
                 executable: str, loader: str, runner: str, author: str, description: str | None = None, 
                 version: str = "0.1.0", url: str | None = None, license: str = 'MIT', tags: str | None = None, 
                 icon: str | None = None, path: str | Path | None = None, enabled: bool = False, active: bool = False, 
                 config: dict = {}, installed_at: str | None = None, created_at: str | None = None, updated_at: str | None = None, deleted_at: str | None = None, id: str | None = None):
        super().__init__(name, category, author, description, version, url, license, tags, icon, path, enabled, active, config, installed_at, created_at, updated_at, deleted_at, id)
        self.executable = executable
        for key, value in config.items():
            self.__setattr__(key, value)
    
    def exists(self) -> bool:
        return bool(which(self.executable))