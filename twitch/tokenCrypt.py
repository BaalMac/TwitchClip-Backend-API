from cryptography.fernet import Fernet
from config import Config

fernet = Fernet(Config.ENCRYPTION_KEY)

def encrypt_token(token: str):
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str):
    return fernet.decrypt(encrypted_token.encode()).decode()