"""
Data persistence manager for LightBerry OS
"""

import json
import os
from datetime import datetime

class DataManager:
    def __init__(self, data_file="lightberry_data.json"):
        self.data_file = data_file
        self.data = {}
        self.load_data()
    
    def load_data(self):
        """Load data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            else:
                self.data = {}
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data = {}
        
        return self.data
    
    def save_data(self, data=None):
        """Save data to JSON file"""
        try:
            if data is not None:
                self.data = data
            
            # Add timestamp
            self.data['last_saved'] = datetime.now().isoformat()
            
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def get_module_data(self, module_name):
        """Get data for specific module"""
        return self.data.get(module_name, {})
    
    def set_module_data(self, module_name, data):
        """Set data for specific module"""
        self.data[module_name] = data
        self.save_data()
    
    def clear_data(self):
        """Clear all data"""
        self.data = {}
        self.save_data()
    
    def backup_data(self, backup_file=None):
        """Create backup of current data"""
        if backup_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"lightberry_backup_{timestamp}.json"
        
        try:
            with open(backup_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            return backup_file
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    def restore_data(self, backup_file):
        """Restore data from backup"""
        try:
            with open(backup_file, 'r') as f:
                self.data = json.load(f)
            self.save_data()
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
