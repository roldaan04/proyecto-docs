import sys
import os

# Add current directory to path so app can be imported
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User

def delete_user(email):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"Found user {email}, deleting...")
            # We also need to delete dependencies if any (memberships etc)
            # But let's start with user
            db.delete(user)
            db.commit()
            print(f"User {email} deleted successfully.")
        else:
            print(f"User {email} not found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_user.py email")
    else:
        delete_user(sys.argv[1])
