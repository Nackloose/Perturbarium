# src/licensee/encoding.py

from .license_data import ALPHABET, ALPHABET_MAP, TOTAL_BITS

# Number of characters in the encoded string (150 bits / 5 bits/char = 30 chars)
ENCODED_CHARS_LEN = TOTAL_BITS // 5


def bits_to_chars(bit_bytes: bytes) -> str:
    """Converts a 150-bit byte sequence into a 30-character string using ALPHABET.

    Args:
        bit_bytes: The 19 bytes containing 150 bits of data.

    Returns:
        A 30-character string from ALPHABET.

    Raises:
        ValueError: If the input byte length is incorrect.
    """
    bytes_expected = (TOTAL_BITS + 7) // 8
    if len(bit_bytes) != bytes_expected:
        raise ValueError(f"Expected {bytes_expected} bytes but got {len(bit_bytes)}")

    # Convert bytes to a single integer
    all_bits = int.from_bytes(bit_bytes, byteorder="big")

    # The bits are packed aligned to the MSB of the bytes. Need to shift right
    # to align the LSB of the 150 bits to the LSB of the integer.
    bits_to_discard = bytes_expected * 8 - TOTAL_BITS
    all_bits >>= bits_to_discard

    encoded_chars = []
    # Extract 5 bits at a time from MSB to LSB
    for i in range(ENCODED_CHARS_LEN):
        # Calculate the position of the 5-bit chunk from the right (LSB)
        # For the first character (i=0), we want the bits from pos 145 to 149 (150 - 5*(0+1))
        # For the last character (i=29), we want the bits from pos 0 to 4 (150 - 5*(29+1))
        # The integer 'all_bits' has the 150 bits in its lower bits.
        # We need to extract the 5-bit chunk that corresponds to the i-th character.
        # The i-th character corresponds to bits (TOTAL_BITS - 5*(i+1)) to (TOTAL_BITS - 5*i - 1)
        # To get these bits, shift right by (TOTAL_BITS - 5*(i+1)) and mask with 0b11111 (31)

        bit_position = TOTAL_BITS - 5 * (i + 1)
        five_bits = (all_bits >> bit_position) & 0x1F
        encoded_chars.append(ALPHABET[five_bits])

    return "".join(encoded_chars)


def chars_to_bits(encoded_chars: str) -> bytes:
    """Converts a 30-character string from ALPHABET into a 150-bit byte sequence.

    Args:
        encoded_chars: The 30-character string from ALPHABET.

    Returns:
        The 19 bytes containing 150 bits of data.

    Raises:
        ValueError: If the input string length or characters are invalid.
    """
    if len(encoded_chars) != ENCODED_CHARS_LEN:
        raise ValueError(
            f"Expected {ENCODED_CHARS_LEN} characters but got {len(encoded_chars)}"
        )

    all_bits = 0
    # Convert characters back to 5-bit values and build the integer
    for char in encoded_chars:
        if char not in ALPHABET_MAP:
            raise ValueError(f"Invalid character in encoded string: {char}")
        five_bits = ALPHABET_MAP[char]
        all_bits = (all_bits << 5) | five_bits

    # The integer 'all_bits' now contains the 150 bits in its lower bits.
    # We need to pack this into bytes, aligning the MSB of our data to the MSB of the bytes.
    bytes_needed = (TOTAL_BITS + 7) // 8
    # Shift left to align the most significant bit of our data to the MSB of the bytes
    aligned_bits = all_bits << (bytes_needed * 8 - TOTAL_BITS)

    # Convert the integer to bytes (big-endian)
    # Use to_bytes with the calculated number of bytes and byteorder
    packed_bytes = aligned_bits.to_bytes(bytes_needed, byteorder="big")

    return packed_bytes


def bytes_to_alphabet_string(input_bytes: bytes) -> str:
    """Converts bytes to a string using our ALPHABET (Base32-like).

    Pads with zeros if needed at the end to complete 5-bit chunks implicitly.
    """
    all_bits = int.from_bytes(input_bytes, byteorder="big")
    total_bits = len(input_bytes) * 8

    encoded_chars = []
    bits_remaining = total_bits

    while bits_remaining > 0:
        # Determine how many bits to take in this chunk (up to 5)
        bits_to_take = min(5, bits_remaining)
        # Extract the relevant bits from the integer
        # Shift right to isolate the current 5-bit chunk (from the MSB side)
        shift_amount = bits_remaining - bits_to_take
        five_bits = (all_bits >> shift_amount) & ((1 << bits_to_take) - 1)

        # If we took fewer than 5 bits, shift left to align for alphabet lookup
        if bits_to_take < 5:
            five_bits <<= 5 - bits_to_take

        encoded_chars.append(ALPHABET[five_bits])
        bits_remaining -= bits_to_take

    # No explicit padding characters needed if the decoder knows the expected bit length.
    # The number of output characters will be ceil(total_bits / 5).

    return "".join(encoded_chars)


def alphabet_string_to_bytes(input_string: str, expected_total_bits: int) -> bytes:
    """Converts a string from our ALPHABET to bytes, expecting a certain total bit length.

    Args:
        input_string: The string encoded with ALPHABET.
        expected_total_bits: The expected total number of bits in the original byte sequence.

    Returns:
        The decoded byte sequence.

    Raises:
        ValueError: If input string contains invalid characters or insufficient bits.
    """
    all_bits = 0
    total_bits_read = 0
    for char in input_string:
        if char not in ALPHABET_MAP:
            raise ValueError(f"Invalid character in string: {char}")
        five_bits = ALPHABET_MAP[char]
        all_bits = (all_bits << 5) | five_bits
        total_bits_read += 5

    if total_bits_read < expected_total_bits:
        raise ValueError(
            f"Input string contains less than expected {expected_total_bits} bits."
        )

    # The integer 'all_bits' now contains the bits.
    # We need to extract the most significant `expected_total_bits`.
    # If total_bits_read > expected_total_bits, we need to shift right.
    bits_to_discard = total_bits_read - expected_total_bits
    all_bits >>= bits_to_discard

    bytes_needed = (expected_total_bits + 7) // 8

    # Shift left to align the most significant bit of our data to the MSB of the bytes
    aligned_bits = all_bits << (bytes_needed * 8 - expected_total_bits)

    return aligned_bits.to_bytes(bytes_needed, byteorder="big")


# Example Usage (within encoding.py)
if __name__ == "__main__":
    print("--- Testing General Byte Encoding/Decoding ---")

    # Example bytes (e.g., a 256-byte signature)
    import os

    signature_bytes_example = os.urandom(256)
    signature_bits_len = len(signature_bytes_example) * 8

    # Encode bytes to alphabet string
    encoded_signature_string = bytes_to_alphabet_string(signature_bytes_example)
    print(
        f"Original Signature Bytes ({len(signature_bytes_example)} bytes, {signature_bits_len} bits): {signature_bytes_example.hex()}"
    )
    print(
        f"Encoded Signature String ({len(encoded_signature_string)} chars): {encoded_signature_string}"
    )

    # Decode alphabet string back to bytes
    decoded_signature_bytes = alphabet_string_to_bytes(
        encoded_signature_string, signature_bits_len
    )
    print(
        f"Decoded Signature Bytes ({len(decoded_signature_bytes)} bytes): {decoded_signature_bytes.hex()}"
    )

    # Verify round trip
    assert (
        signature_bytes_example == decoded_signature_bytes
    ), "Signature encoding/decoding round trip failed!"
    print("Signature encoding/decoding round trip successful.")

    print("\n--- Testing 150-bit Encoding/Decoding (Original) ---")
    # Keep the original 150-bit tests as well to ensure compatibility
    # Example 150 bits (19 bytes)
    known_bits_int = 0
    for i in range(150):
        if i % 2 == 0:
            known_bits_int |= 1 << i

    # Pack these 150 bits into 19 bytes (MSB aligned)
    known_bytes = (known_bits_int << (19 * 8 - 150)).to_bytes(19, byteorder="big")
    print(f"Known Bits Bytes: {known_bytes.hex()}")

    # Convert bytes to chars
    known_encoded_string = bits_to_chars(known_bytes)
    print(
        f"Encoded Known String ({len(known_encoded_string)} chars): {known_encoded_string}"
    )

    # Convert chars back to bytes
    known_decoded_bytes = chars_to_bits(known_encoded_string)
    print(f"Decoded Known Bytes: {known_decoded_bytes.hex()}")

    assert known_bytes == known_decoded_bytes, "Round trip failed for known bits!"
    print("Round trip successful for known bits.")
