import sys
import os

# Add current directory to path so app can be imported
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def reset_password(email, new_password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"Found user {email}, current hash: {user.password_hash}")
            user.password_hash = get_password_hash(new_password)
            db.commit()
            print(f"Password reset successful for {email}. New hash: {user.password_hash}")
        else:
            print(f"User {email} not found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python reset_password.py email new_password")
    else:
        reset_password(sys.argv[1], sys.argv[2])
