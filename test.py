import ecdsa
import hashlib
from ecdsa import SigningKey, VerifyingKey

# Generate a new private key
private_key = SigningKey.generate()

# Derive the public key from the private key
public_key = private_key.get_verifying_key()

print(private_key)
print(public_key)