#!/usr/bin/env python3
"""
SineScramble Standalone Demo

A standalone demonstration script showcasing SineScramble cipher capabilities.
Can be run independently to explore the cipher's features.
"""

import sys
import time
import os
try:
    # Try package imports first
    from sinescramble import SineScrambleCipher, OperationMode
    from sinescramble.utils import (
        generate_random_key, key_from_password, key_to_string,
        estimate_security_level, recommend_mode_for_use_case
    )
except ImportError:
    # Fall back to direct imports
    from cipher import SineScrambleCipher, OperationMode
    from utils import (
        generate_random_key, key_from_password, key_to_string,
        estimate_security_level, recommend_mode_for_use_case
    )


def print_header():
    """Print demo header"""
    print("🔐 SineScramble Cipher Demo")
    print("=" * 50)
    print("A novel symmetric cipher with dual operational modes")
    print("Version 2.1.0 by N Lisowski")
    print("=" * 50)


def basic_demo():
    """Basic encryption/decryption demonstration"""
    print("\n📋 Basic Encryption Demo")
    print("-" * 30)
    
    message = "The quick brown fox jumps over the lazy dog! 🦊"
    key = generate_random_key(6, seed=42)
    
    print(f"Message: {message}")
    print(f"Key dimension: {len(key)}")
    print(f"Security level: {estimate_security_level(len(key))}")
    
    # Multi-Round Mode
    print(f"\n🔒 Multi-Round Mode (High Security)")
    cipher_mr = SineScrambleCipher(key, OperationMode.MULTI_ROUND)
    
    start_time = time.time()
    encrypted_mr = cipher_mr.encrypt(message)
    encrypt_time = time.time() - start_time
    
    start_time = time.time()
    decrypted_mr = cipher_mr.decrypt(encrypted_mr).decode('utf-8')
    decrypt_time = time.time() - start_time
    
    print(f"Encrypted: {encrypted_mr.hex()[:60]}...")
    print(f"Decrypted: {decrypted_mr}")
    print(f"Success: {message == decrypted_mr}")
    print(f"Time: {encrypt_time:.4f}s encrypt, {decrypt_time:.4f}s decrypt")
    
    # Segmented Mode
    print(f"\n⚡ Segmented Mode (High Performance)")
    cipher_seg = SineScrambleCipher(key, OperationMode.SEGMENTED)
    
    start_time = time.time()
    encrypted_seg = cipher_seg.encrypt(message)
    encrypt_time = time.time() - start_time
    
    start_time = time.time()
    decrypted_seg = cipher_seg.decrypt(encrypted_seg).decode('utf-8')
    decrypt_time = time.time() - start_time
    
    print(f"Encrypted: {encrypted_seg.hex()[:60]}...")
    print(f"Decrypted: {decrypted_seg}")
    print(f"Success: {message == decrypted_seg}")
    print(f"Time: {encrypt_time:.4f}s encrypt, {decrypt_time:.4f}s decrypt")


def password_demo():
    """Password-based key demonstration"""
    print("\n🔑 Password-based Keys Demo")
    print("-" * 30)
    
    password = "MySecretPassword123!"
    message = "Confidential document contents"
    
    print(f"Password: {password}")
    print(f"Message: {message}")
    
    # Generate key from password
    key = key_from_password(password, 8)
    print(f"Generated key (first 3 components): {key[:3]}")
    
    # Encrypt with derived key
    cipher = SineScrambleCipher(key, OperationMode.MULTI_ROUND)
    encrypted = cipher.encrypt(message)
    decrypted = cipher.decrypt(encrypted).decode('utf-8')
    
    print(f"Encrypted: {encrypted.hex()}")
    print(f"Decrypted: {decrypted}")
    print(f"Success: {message == decrypted}")
    
    # Show deterministic nature
    key2 = key_from_password(password, 8)
    print(f"Same password generates identical key: {key == key2}")


def avalanche_demo():
    """Demonstrate avalanche effect"""
    print("\n🌊 Avalanche Effect Demo")
    print("-" * 30)
    
    key = generate_random_key(5, seed=123)
    cipher = SineScrambleCipher(key, OperationMode.MULTI_ROUND)
    
    # Two messages differing by one bit
    message1 = "Hello World"
    message2 = "Hello world"  # Different case
    
    encrypted1 = cipher.encrypt(message1)
    encrypted2 = cipher.encrypt(message2)
    
    # Calculate differences
    min_len = min(len(encrypted1), len(encrypted2))
    different_bytes = sum(a != b for a, b in zip(encrypted1[:min_len], encrypted2[:min_len]))
    
    print(f"Message 1: '{message1}'")
    print(f"Message 2: '{message2}'")
    print(f"Difference: 1 character (W vs w)")
    print(f"Encrypted 1: {encrypted1.hex()}")
    print(f"Encrypted 2: {encrypted2.hex()}")
    print(f"Changed bytes: {different_bytes}/{min_len} ({different_bytes/min_len*100:.1f}%)")
    print("✅ Small input changes cause large output changes (good avalanche effect)")


def file_demo():
    """File encryption demonstration"""
    print("\n📁 File Encryption Demo")
    print("-" * 30)
    
    # Create sample file
    filename = "demo_sample.txt"
    encrypted_filename = "demo_sample.encrypted"
    decrypted_filename = "demo_sample_decrypted.txt"
    
    sample_content = """This is a sample file for SineScramble encryption demo.
It contains multiple lines of text.
Special characters: !@#$%^&*()
Unicode: αβγδ 中文 🚀

SineScramble can encrypt files of any size efficiently!
"""
    
    try:
        # Write sample file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        print(f"Created sample file: {filename}")
        print(f"Original size: {len(sample_content)} characters")
        
        # Encrypt file
        key = generate_random_key(4, seed=456)
        cipher = SineScrambleCipher(key, OperationMode.SEGMENTED)
        
        print(f"Encrypting with {len(key)}-dimensional key...")
        cipher.encrypt_file(filename, encrypted_filename)
        
        encrypted_size = os.path.getsize(encrypted_filename)
        print(f"Encrypted file: {encrypted_filename} ({encrypted_size} bytes)")
        
        # Decrypt file
        print("Decrypting...")
        cipher.decrypt_file(encrypted_filename, decrypted_filename)
        
        # Verify
        with open(decrypted_filename, 'r', encoding='utf-8') as f:
            decrypted_content = f.read()
        
        success = sample_content == decrypted_content
        print(f"Decrypted file: {decrypted_filename}")
        print(f"Content matches: {success}")
        
        if success:
            print("✅ File encryption/decryption successful!")
        else:
            print("❌ File encryption/decryption failed!")
        
    finally:
        # Clean up demo files
        for file in [filename, encrypted_filename, decrypted_filename]:
            if os.path.exists(file):
                os.remove(file)
                print(f"Cleaned up: {file}")


def performance_demo():
    """Performance comparison demonstration"""
    print("\n⚡ Performance Comparison Demo")
    print("-" * 30)
    
    # Test different data sizes
    sizes = [1024, 10240]  # 1KB, 10KB
    key = generate_random_key(6, seed=789)
    
    print(f"Testing with {len(key)}-dimensional key")
    
    for size in sizes:
        print(f"\n--- {size} bytes ({size//1024}KB) ---")
        test_data = os.urandom(size)
        
        # Multi-Round Mode
        cipher_mr = SineScrambleCipher(key, OperationMode.MULTI_ROUND)
        start_time = time.time()
        encrypted_mr = cipher_mr.encrypt(test_data)
        mr_time = time.time() - start_time
        
        start_time = time.time()
        decrypted_mr = cipher_mr.decrypt(encrypted_mr)
        mr_decrypt_time = time.time() - start_time
        
        # Segmented Mode
        cipher_seg = SineScrambleCipher(key, OperationMode.SEGMENTED)
        start_time = time.time()
        encrypted_seg = cipher_seg.encrypt(test_data)
        seg_time = time.time() - start_time
        
        start_time = time.time()
        decrypted_seg = cipher_seg.decrypt(encrypted_seg)
        seg_decrypt_time = time.time() - start_time
        
        # Results
        speedup = mr_time / seg_time if seg_time > 0 else float('inf')
        decrypt_speedup = mr_decrypt_time / seg_decrypt_time if seg_decrypt_time > 0 else float('inf')
        
        print(f"Multi-Round:  {mr_time:.4f}s encrypt, {mr_decrypt_time:.4f}s decrypt")
        print(f"Segmented:    {seg_time:.4f}s encrypt, {seg_decrypt_time:.4f}s decrypt")
        print(f"Speedup:      {speedup:.2f}x encrypt, {decrypt_speedup:.2f}x decrypt")
        print(f"Correctness:  MR={test_data == decrypted_mr}, SEG={test_data == decrypted_seg}")


def use_case_demo():
    """Use case recommendation demonstration"""
    print("\n🎯 Use Case Recommendations Demo")
    print("-" * 30)
    
    use_cases = [
        "Real-time video streaming",
        "Secure file backup system",
        "Live chat encryption",
        "Database encryption at rest",
        "IoT sensor data encryption",
        "High-frequency trading data",
        "Document archive encryption"
    ]
    
    print("SineScramble can recommend the best mode for your use case:")
    print()
    
    for use_case in use_cases:
        recommendation = recommend_mode_for_use_case(use_case)
        print(f"📌 {use_case}")
        print(f"   → {recommendation}")
        print()


def interactive_demo():
    """Interactive demonstration"""
    print("\n💬 Interactive Demo")
    print("-" * 30)
    
    try:
        # Get user input
        message = input("Enter a message to encrypt: ").strip()
        if not message:
            message = "Default test message"
            print(f"Using default: {message}")
        
        print("\nChoose mode:")
        print("1. Multi-Round (High Security)")
        print("2. Segmented (High Performance)")
        mode_choice = input("Enter choice (1 or 2): ").strip()
        
        if mode_choice == "2":
            mode = OperationMode.SEGMENTED
            mode_name = "Segmented"
        else:
            mode = OperationMode.MULTI_ROUND
            mode_name = "Multi-Round"
        
        print("\nChoose key source:")
        print("1. Random key")
        print("2. Password-based key")
        key_choice = input("Enter choice (1 or 2): ").strip()
        
        if key_choice == "2":
            password = input("Enter password: ").strip()
            if not password:
                password = "DefaultPassword123"
                print(f"Using default password: {password}")
            key = key_from_password(password, 8)
            key_source = f"password '{password}'"
        else:
            key = generate_random_key(8)
            key_source = "random generation"
        
        print(f"\n🔐 Encrypting with SineScramble")
        print(f"Mode: {mode_name}")
        print(f"Key: {len(key)}-dimensional from {key_source}")
        print(f"Security level: {estimate_security_level(len(key))}")
        
        # Encrypt and decrypt
        cipher = SineScrambleCipher(key, mode)
        encrypted = cipher.encrypt(message)
        decrypted = cipher.decrypt(encrypted).decode('utf-8')
        
        print(f"\nResults:")
        print(f"Original:  {message}")
        print(f"Encrypted: {encrypted.hex()}")
        print(f"Decrypted: {decrypted}")
        print(f"Success:   {message == decrypted}")
        
        if message == decrypted:
            print("✅ Encryption/decryption successful!")
        else:
            print("❌ Encryption/decryption failed!")
            
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")


def main():
    """Main demo function"""
    print_header()
    
    demos = [
        ("Basic Encryption", basic_demo),
        ("Password-based Keys", password_demo),
        ("Avalanche Effect", avalanche_demo),
        ("File Operations", file_demo),
        ("Performance Comparison", performance_demo),
        ("Use Case Recommendations", use_case_demo),
        ("Interactive Demo", interactive_demo)
    ]
    
    try:
        for name, demo_func in demos:
            demo_func()
            
        print("\n🎉 Demo completed successfully!")
        print("\nTo run individual demos or tests:")
        print("  ./run.sh test    - Run full test suite")
        print("  ./run.sh demo    - Run interactive demo only")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye! 👋")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 