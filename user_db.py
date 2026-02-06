import sqlite3
import hashlib
import secrets
from datetime import datetime
import os

class UserDatabase:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create the users table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                is_verified INTEGER DEFAULT 0,
                verification_token TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                account_type TEXT DEFAULT 'quick'
            )
        """)
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_token(self):
        """Generate a random verification token"""
        return secrets.token_urlsafe(32)
    
    def create_user(self, username, password, email=None, account_type="quick"):
        """Create a new user (Full signup includes email)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            verification_token = self.generate_token() if account_type == "full" else None
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, verification_token, account_type)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password_hash, email, verification_token, account_type))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "token": verification_token}
        except sqlite3.IntegrityError:
            return {"success": False, "error": "Username already exists"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute("""
            SELECT id, username, email, is_verified, account_type 
            FROM users 
            WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "success": True,
                "user": {
                    "id": result[0],
                    "username": result[1],
                    "email": result[2],
                    "is_verified": bool(result[3]),
                    "account_type": result[4]
                }
            }
        return {"success": False}
    
    def verify_email(self, token):
        """Mark user as verified using token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET is_verified = 1 
                WHERE verification_token = ?
            """, (token,))
            
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            
            return {"success": success}
        except Exception as e:
            return {"success": False, "error": str(e)}
