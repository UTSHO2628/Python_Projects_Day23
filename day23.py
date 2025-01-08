# Password management system with passwrord Generator 
import sqlite3
from cryptography.fernet import Fernet

# databasesetup
conn = sqlite3.connect('password_manager.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.commit()

# Encryption key
def load_or_generate_key():
    try:
        with open("key.key", "rb") as file:
            return file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open("key.key", "wb") as file:
            file.write(key)
        return key

key = load_or_generate_key()
cipher = Fernet(key)

def generate_password(length=12):
    import random
    import string
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

# save password
def save_password(service, username, password):
    encrypted_password = cipher.encrypt(password.encode())
    cursor.execute('INSERT INTO passwords (service, username, password) VALUES (?, ?, ?)',
                   (service, username, encrypted_password))
    conn.commit()
    print("Password saved successfully!")
    
def retrieve_password(service):
    cursor.execute('SELECT username, password FROM passwords WHERE service = ?', (service,))
    result = cursor.fetchone()
    if result:
        username, encrypted_password = result
        password = cipher.decrypt(encrypted_password).decode()
        print(f"Service: {service}\nUsername: {username}\nPassword: {password}")
    else:
        print("No password found for this service.")

def menu():
    while True:
        print("\nPassword Manager")
        print("1. Save a new password")
        print("2. Retrieve a password")
        print("3. Generate a random password")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            service = input("Enter the service name: ")
            username = input("Enter the username: ")
            password = input("Enter the password: ")
            save_password(service, username, password)
        elif choice == '2':
            service = input("Enter the service name to retrieve: ")
            retrieve_password(service)
        elif choice == '3':
            length = int(input("Enter the desired password length: "))
            print(f"Generated Password: {generate_password(length)}")
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Try again.")

menu()
