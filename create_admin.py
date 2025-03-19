import sys
import os
from getpass import getpass
from app import app, db
from models import User, UserRole

def create_admin():
    print("Admin felhasználó létrehozása")
    print("-" * 30)
    
    username = input("Felhasználónév: ").strip()
    if not username:
        print("A felhasználónév megadása kötelező!")
        return

    

    password = getpass("Jelszó: ")
    confirm_password = getpass("Jelszó megerősítése: ")

    if password != confirm_password:
        print("A jelszavak nem egyeznek!")
        return

    if len(password) < 4:
        print("A jelszónak legalább 6 karakter hosszúnak kell lennie!")
        return

    try:
        with app.app_context():
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                print("A felhasználónév már foglalt!")
                return
            
           

            user = User(username=username, role=UserRole.ADMIN.value)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"\nAdmin felhasználó sikeresen létrehozva: {username}")

    except Exception as e:
        print(f"Hiba történt: {str(e)}")
        return

if __name__ == "__main__":
    create_admin()
