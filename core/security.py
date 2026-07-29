from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_pass: str):
    return password_hash.verify(password, hashed_pass)