from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=512,
    backend=default_backend())


print("Your private key is: ", private_key.private_bytes(encoding=Encoding.PEM, encryption_algorithm=NoEncryption(), format=PrivateFormat.TraditionalOpenSSL))
print("Your public key is: ", private_key.public_key().public_bytes(encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo))

# print(len(private_key.private_bytes(encoding=Encoding.PEM, encryption_algorithm=NoEncryption(), format=PrivateFormat.TraditionalOpenSSL)))

# ## If you want to make sure the keys work, uncomment the following code blocks:

# message = b"A message I want to sign"


# signature = private_key.sign(
#     message,
#     padding.PSS(
#         mgf=padding.MGF1(hashes.SHA256()),
#         salt_length=padding.PSS.MAX_LENGTH
#     ),
#     hashes.SHA256()
# )

# print(message)
# print(signature)

# ######################### Uncomment the following line to change the message and invalidate the signature
# #message= b"I changed the message"
# #########################

# public_key = private_key.public_key()

# print(public_key.verify(
#     signature,
#     message,
#     padding.PSS(
#         mgf=padding.MGF1(hashes.SHA256()),
#         salt_length=padding.PSS.MAX_LENGTH
#     ),
#     hashes.SHA256()
# ))