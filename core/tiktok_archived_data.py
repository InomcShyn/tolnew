#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Archived Data Manager

PURPOSE:
Separate "TikTok account data" from "profiles" and keep old/used data 
even when profiles are deleted.

CONCEPT:
- Profile: Chrome browser profile (can be deleted/recreated)
- TikTok Data: Account credentials and session (persists independently)
- Archived Data: TikTok data from deleted/unused profiles

WHY ARCHIVED DATA EXISTS:
When a profile is deleted, we don't want to lose the TikTok account data.
The account might be reused later or we want to keep history of used accounts.

DIFFERENCE:
- Profile: Browser state, extensions, cookies (temporary)
- TikTok Data: Username, password, session (permanent)
- Archived Data: Historical TikTok data (read-only by default)
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class TikTokArchivedDataManager:
    """
    Manager for archived TikTok account data
    
    Data is stored separately from active profiles to preserve
    account information even when profiles are deleted.
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialize archived data manager
        
        Args:
            base_dir: Base directory for data storage
        """
        if base_dir is None:
            base_dir = os.getcwd()
        
        self.base_dir = base_dir
        self.config_dir = os.path.join(base_dir, 'config')
        
        # Active TikTok data (linked to current profiles)
        self.active_data_file = os.path.join(self.config_dir, 'tiktok_accounts.json')
        
        # Archived TikTok data (from deleted/unused profiles)
        self.archived_data_file = os.path.join(self.config_dir, 'tiktok_archived.json')
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
    
    # ========================================================================
    # ACTIVE DATA MANAGEMENT
    # ========================================================================
    
    def get_active_data(self) -> List[Dict]:
        """
        Get all active TikTok account data
        
        Returns:
            List of active account data dicts
        """
        if not os.path.exists(self.active_data_file):
            return []
        
        try:
            with open(self.active_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            print(f"[ARCHIVED] Error loading active data: {e}")
            return []
    
    def save_active_data(self, data: List[Dict]) -> bool:
        """
        Save active TikTok account data
        
        Args:
            data: List of account data dicts
        
        Returns:
            True if successful
        """
        try:
            with open(self.active_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ARCHIVED] Error saving active data: {e}")
            return False
    
    # ========================================================================
    # ARCHIVED DATA MANAGEMENT
    # ========================================================================
    
    def get_archived_data(self) -> List[Dict]:
        """
        Get all archived TikTok account data
        
        Returns:
            List of archived account data dicts
        """
        if not os.path.exists(self.archived_data_file):
            return []
        
        try:
            with open(self.archived_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            print(f"[ARCHIVED] Error loading archived data: {e}")
            return []
    
    def save_archived_data(self, data: List[Dict]) -> bool:
        """
        Save archived TikTok account data
        
        Args:
            data: List of archived account data dicts
        
        Returns:
            True if successful
        """
        try:
            with open(self.archived_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ARCHIVED] Error saving archived data: {e}")
            return False
    
    # ========================================================================
    # ARCHIVE OPERATIONS
    # ========================================================================
    
    def archive_account(self, profile_name: str) -> Tuple[bool, str]:
        """
        Archive TikTok account data when profile is deleted
        
        This moves the account data from active to archived storage,
        preserving credentials and session for potential future use.
        
        Args:
            profile_name: Profile name to archive
        
        Returns:
            (success, message)
        """
        try:
            # Get active data
            active_data = self.get_active_data()
            
            # Find account for this profile
            account_to_archive = None
            remaining_active = []
            
            for account in active_data:
                if account.get('profile_name') == profile_name:
                    account_to_archive = account.copy()
                else:
                    remaining_active.append(account)
            
            if not account_to_archive:
                return False, f"No TikTok data found for profile {profile_name}"
            
            # Clean account data (remove runtime info)
            archived_account = self._clean_for_archive(account_to_archive)
            
            # Add to archived data
            archived_data = self.get_archived_data()
            archived_data.append(archived_account)
            
            # Save both files
            if not self.save_archived_data(archived_data):
                return False, "Failed to save archived data"
            
            if not self.save_active_data(remaining_active):
                return False, "Failed to update active data"
            
            print(f"[ARCHIVED] ✅ Archived account for profile {profile_name}")
            return True, f"Account archived successfully"
        
        except Exception as e:
            print(f"[ARCHIVED] Error archiving account: {e}")
            return False, str(e)
    
    def _clean_for_archive(self, account: Dict) -> Dict:
        """
        Clean account data for archiving
        
        Removes runtime info and adds archive metadata.
        
        Args:
            account: Account data dict
        
        Returns:
            Cleaned account data
        """
        # Fields to keep (credentials and session only)
        keep_fields = [
            'profile_name',
            'username',
            'email',
            'password',
            'cookies',
            'session',
            'proxy',
            'note',
            'tag',
            'created_at',
            'last_used_at',
        ]
        
        # Create cleaned copy
        cleaned = {}
        for field in keep_fields:
            if field in account:
                cleaned[field] = account[field]
        
        # Add archive metadata
        cleaned['archived_at'] = datetime.now().isoformat()
        cleaned['original_profile'] = account.get('profile_name')
        
        return cleaned
    
    # ========================================================================
    # RESTORE OPERATIONS
    # ========================================================================
    
    def restore_account(self, archived_index: int, new_profile_name: str = None) -> Tuple[bool, str]:
        """
        Restore archived account to active data
        
        Args:
            archived_index: Index in archived data list
            new_profile_name: New profile name (optional, uses original if None)
        
        Returns:
            (success, message)
        """
        try:
            # Get archived data
            archived_data = self.get_archived_data()
            
            if archived_index < 0 or archived_index >= len(archived_data):
                return False, "Invalid archived index"
            
            # Get account to restore
            account_to_restore = archived_data[archived_index].copy()
            
            # Remove from archived
            archived_data.pop(archived_index)
            
            # Clean restore data (remove archive metadata)
            restored_account = self._clean_for_restore(account_to_restore, new_profile_name)
            
            # Add to active data
            active_data = self.get_active_data()
            active_data.append(restored_account)
            
            # Save both files
            if not self.save_archived_data(archived_data):
                return False, "Failed to save archived data"
            
            if not self.save_active_data(active_data):
                return False, "Failed to save active data"
            
            profile_name = restored_account.get('profile_name')
            print(f"[ARCHIVED] ✅ Restored account to profile {profile_name}")
            return True, f"Account restored to {profile_name}"
        
        except Exception as e:
            print(f"[ARCHIVED] Error restoring account: {e}")
            return False, str(e)
    
    def _clean_for_restore(self, account: Dict, new_profile_name: str = None) -> Dict:
        """
        Clean account data for restoration
        
        Args:
            account: Archived account data
            new_profile_name: New profile name (optional)
        
        Returns:
            Cleaned account data
        """
        # Remove archive metadata
        cleaned = account.copy()
        cleaned.pop('archived_at', None)
        cleaned.pop('original_profile', None)
        
        # Update profile name if provided
        if new_profile_name:
            cleaned['profile_name'] = new_profile_name
        
        # Update last_used_at
        cleaned['last_used_at'] = datetime.now().isoformat()
        
        return cleaned
    
    # ========================================================================
    # DELETE OPERATIONS
    # ========================================================================
    
    def delete_archived(self, archived_index: int) -> Tuple[bool, str]:
        """
        Permanently delete archived account data
        
        Args:
            archived_index: Index in archived data list
        
        Returns:
            (success, message)
        """
        try:
            # Get archived data
            archived_data = self.get_archived_data()
            
            if archived_index < 0 or archived_index >= len(archived_data):
                return False, "Invalid archived index"
            
            # Get account info for logging
            account = archived_data[archived_index]
            username = account.get('username', 'unknown')
            
            # Remove from archived
            archived_data.pop(archived_index)
            
            # Save
            if not self.save_archived_data(archived_data):
                return False, "Failed to save archived data"
            
            print(f"[ARCHIVED] ✅ Permanently deleted archived account: {username}")
            return True, f"Archived account deleted: {username}"
        
        except Exception as e:
            print(f"[ARCHIVED] Error deleting archived account: {e}")
            return False, str(e)
    
    # ========================================================================
    # UTILITY OPERATIONS
    # ========================================================================
    
    def get_account_credentials(self, archived_index: int) -> Optional[Dict]:
        """
        Get credentials from archived account (for copying)
        
        Args:
            archived_index: Index in archived data list
        
        Returns:
            Dict with username, email, password or None
        """
        try:
            archived_data = self.get_archived_data()
            
            if archived_index < 0 or archived_index >= len(archived_data):
                return None
            
            account = archived_data[archived_index]
            
            return {
                'username': account.get('username', ''),
                'email': account.get('email', ''),
                'password': account.get('password', ''),
            }
        
        except Exception as e:
            print(f"[ARCHIVED] Error getting credentials: {e}")
            return None
