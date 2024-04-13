from odbms import Model
from enum import Enum
from typing import Optional, Literal
from pathlib import Path
import datetime

class Category(Enum):
    """
    Category Enum

    Represents a category of plugins
    """
    LANGUAGE = 'language'
    UTILITY = 'utility'
    VISUALIZATION = 'visualization'
    SECURITY = 'security'
    
    @classmethod
    def get_all_categories(cls):
        return list(cls)
    
    def __str__(self):
        return self.value
    

class Plugin(Model):
    """
    Plugin Model
    
    Represents a plugin that can be installed_at and used to extend functionality.

    Attributes:
        name: Name of the plugin
        category: Category of the plugin
        author: Author/publisher of the plugin
        description: Short description of what the plugin does
        version: Plugin version string 
        url: URL to get more info about the plugin
        license: Software license of the plugin
        tags: List of tags to aid with searching/filtering
        icon: Icon image file for the plugin
        path: Local filesystem path where plugin is installed
        enabled: Flag indicating if plugin is enabled
        active: Flag indicating if plugin is active
        config: Configuration settings for the plugin
        installed_at: Timestamp when plugin was installed
        created_at: Timestamp when plugin record was created
        updated_at: Timestamp when plugin record was last updated
        deleted_at: Timestamp when plugin record was soft deleted
    """
    
    def __init__(self, name: str, category: Literal['language', 'utility', 'visualization', 'security'],
                 author: str, description: Optional[str] = None, 
                 version: str = "0.1.0", url: Optional[str] = None, 
                 license: str = 'MIT', tags: Optional[str] = None, 
                 icon: Optional[str] = None, path: Optional[str | Path]= None, 
                 enabled: bool = False, active: bool = False, config: dict = {}, 
                 installed_at: Optional[str] = None,
                 created_at: Optional[str] = None, 
                 updated_at: Optional[str] = None, 
                 deleted_at: Optional[str] = None, 
                 id: Optional[str] = None):
        super().__init__(created_at, updated_at, id)
        self.name = name
        self.category = category
        self.description = description
        self.author = author 
        self.version = version
        self.url = url or ""
        self.license = license or ""
        self.tags = tags or []
        self.icon = icon or ""
        self.path = str(path) if isinstance(path, Path) else path
        self.enabled = enabled
        self.active = active 
        self.config = config or {}
        self.installed_at = installed_at
        self.deleted_at = deleted_at
    
    def enable(self) -> None:
        self.enabled = True
        
    def disable(self) -> None:
        self.enabled = False
        
    def activate(self) -> None:
        self.active = True
        
    def deactivate(self) -> None:
        self.active = False
        
    def install(self, path) -> None:
        self.path = path
        self.installed_at = (datetime.datetime.utcnow()).strftime("%a %b %d %Y %H:%M:%S")
        
    def uninstall(self) -> None:
        self.path = None
        self.installed_at = None
        
    def update(self, version=None) -> None:
        if version:
            self.version = version
        self.updated_at = (datetime.datetime.utcnow()).strftime("%a %b %d %Y %H:%M:%S")
        
    def delete(self) -> None:
        self.deleted_at = (datetime.datetime.utcnow()).strftime("%a %b %d %Y %H:%M:%S")
