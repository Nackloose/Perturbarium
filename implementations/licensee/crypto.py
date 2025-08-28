from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from typing import Optional
import os

# In a real application, you would securely load your private and public keys.
# For demonstration, we'll define placeholders for key loading functions.


def load_private_key():
    """Loads the private key for signing (should be securely stored)."""
    # This is a placeholder. In a real application, load from a secure file or environment variable.
    # Example: return serialization.load_pem_private_key(pem_data, password=None, backend=default_backend())
    raise NotImplementedError("Private key loading not implemented.")


def load_public_key():
    """Loads the public key for verification (bundled with the application)."""
    # This is a placeholder. In a real application, load from a file bundled with the app.
    # Example: return serialization.load_pem_public_key(pem_data, backend=default_backend())
    # For testing, we can generate a key pair and use the public key from that.
    # In a real scenario, the public key is separate and only the private key is used for signing.

    # For demonstration purposes, let's create a dummy key pair.
    # IMPORTANT: Replace this with actual secure public key loading in production!
    # This function is still needed for the main app's validation logic.
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    return private_key.public_key()


# --- Key Loading from Path ---
def load_private_key_from_path(file_path: str, password: Optional[bytes] = None):
    """Loads a private key from a file path."""
    try:
        with open(file_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(), password, backend=default_backend()
            )
        return private_key
    except FileNotFoundError:
        raise FileNotFoundError(f"Private key file not found at: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error loading private key from {file_path}: {e}")


def load_public_key_from_path(file_path: str):
    """Loads a public key from a file path."""
    try:
        with open(file_path, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(), backend=default_backend()
            )
        return public_key
    except FileNotFoundError:
        raise FileNotFoundError(f"Public key file not found at: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error loading public key from {file_path}: {e}")


# --- Key Generation ---
def generate_rsa_key_pair(key_size: int = 2048):
    """Generates a new RSA public and private key pair."""
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=key_size, backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


# --- Key Saving ---
def save_private_key_to_file(
    private_key, file_path: str, password: Optional[bytes] = None
):
    """Saves a private key to a file in PEM format."""
    try:
        # Use BestAvailableEncryption if password is provided, NoEncryption otherwise
        encryption_algorithm = (
            serialization.BestAvailableEncryption(password)
            if password
            else serialization.NoEncryption()
        )
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm,
        )
        with open(file_path, "wb") as f:
            f.write(pem)
    except Exception as e:
        raise RuntimeError(f"Error saving private key to {file_path}: {e}")


def save_public_key_to_file(public_key, file_path: str):
    """Saves a public key to a file in PEM format."""
    try:
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        with open(file_path, "wb") as f:
            f.write(pem)
    except Exception as e:
        raise RuntimeError(f"Error saving public key to {file_path}: {e}")


# --- Signing and Verification ---
def sign_data(data: bytes, private_key) -> bytes:
    """Signs data using the provided private key."""
    # Use OAEP padding for encryption, PSS for signing (recommended)
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )
    return signature


def verify_signature(data: bytes, signature: bytes, public_key) -> bool:
    """Verifies a signature using the provided public key."""
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        return True  # Signature is valid
    except InvalidSignature:
        return False  # Signature is invalid
    except Exception as e:
        print(f"An error occurred during signature verification: {e}")
        return False


# Example Usage (within crypto.py) - Update to test new functions
if __name__ == "__main__":
    print("--- Testing Crypto Functions ---")

    # Test Key Generation and Saving
    print("\nGenerating and saving a test key pair...")
    test_private_key, test_public_key = generate_rsa_key_pair()
    test_private_key_path = "test_private_key.pem"
    test_public_key_path = "test_public_key.pem"

    try:
        save_private_key_to_file(test_private_key, test_private_key_path)
        save_public_key_to_file(test_public_key, test_public_key_path)
        print(f"Test keys saved to {test_private_key_path} and {test_public_key_path}.")

        # Test Key Loading from File
        print("\nLoading test key pair from files...")
        loaded_private_key = load_private_key_from_path(test_private_key_path)
        loaded_public_key = load_public_key_from_path(test_public_key_path)
        print("Test keys loaded successfully from files.")

        # Test Signing and Verification with Loaded Keys
        print("\nTesting signing and verification with loaded keys...")
        test_data = b"This is the data to be signed and verified."
        test_signature = sign_data(test_data, loaded_private_key)
        is_valid = verify_signature(test_data, test_signature, loaded_public_key)
        print(f"Is signature valid with loaded keys? {is_valid}")
        assert is_valid, "Signing/Verification with loaded keys failed!"
        print("Signing/Verification with loaded keys successful.")

    except Exception as e:
        print(f"Error during crypto test: {e}")

    finally:
        # Clean up test files
        if os.path.exists(test_private_key_path):
            os.remove(test_private_key_path)
        if os.path.exists(test_public_key_path):
            os.remove(test_public_key_path)
        print("\nCleaned up test key files.")
