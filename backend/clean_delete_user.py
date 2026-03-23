from sqlalchemy import create_engine, text
import sys

def delete_user(email):
    # postgresql+psycopg://saas_user:Roldan210605@localhost:5432/saas_web
    db_url = "postgresql+psycopg://saas_user:Roldan210605@localhost:5432/saas_web"
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print(f"Checking for user {email}...")
        # Check if user exists
        result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email}).fetchone()
        if result:
            user_id = result[0]
            print(f"Found user {email} (ID: {user_id}), deleting dependencies...")
            
            # Delete memberships
            conn.execute(text("DELETE FROM memberships WHERE user_id = :user_id"), {"user_id": user_id})
            
            # Delete user
            conn.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id})
            
            conn.commit()
            print(f"User {email} and their memberships deleted successfully.")
        else:
            print(f"User {email} not found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_delete_user.py email")
    else:
        delete_user(sys.argv[1])
