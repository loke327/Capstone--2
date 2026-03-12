import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

# Generate keys (one-time)
def generate_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

# SHA-256 hashing
def sha256_hash(data: bytes):
    return hashlib.sha256(data).hexdigest()

# Sign hash
def sign_hash(private_key, hash_value):
    signature = private_key.sign(
        hash_value.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
            ),
        hashes.SHA256()
    )
    return signature

# Verify signature
def verify_signature(public_key, hash_value, signature):
    try:
        public_key.verify(
            signature,
            hash_value.encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return True
    except:
        return False
