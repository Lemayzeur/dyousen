import hashlib

def hash_password(password):
    # A simple hashing function (you should use a secure hashing method in production)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password