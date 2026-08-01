from pwdlib import PasswordHash
import hashlib

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_pass: str):
    return password_hash.verify(password, hashed_pass)

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def verify_token(token: str, hashed_token: str) -> bool:
    return hash_token(token) == hashed_token