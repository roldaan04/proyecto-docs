import psycopg2
from app.core.config import settings

def check_user():
    try:
        # Extract connection details from DATABASE_URL
        # postgresql+psycopg://saas_user:Roldan210605@localhost:5432/saas_web
        conn = psycopg2.connect("dbname='saas_web' user='saas_user' password='Roldan210605' host='localhost'")
        cur = conn.cursor()
        
        cur.execute("SELECT id, email, password_hash FROM users WHERE email = 'javirol2005@gmail.com';")
        user = cur.fetchone()
        
        if user:
            print(f"ID: {user[0]}")
            print(f"Email: {user[1]}")
            print(f"Hash: {user[2]}")
        else:
            print("User not found.")
            # List all users to see what's there
            cur.execute("SELECT email FROM users LIMIT 10;")
            users = cur.fetchall()
            print(f"Other users: {users}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_user()
