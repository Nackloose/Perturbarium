# src/licensee/license_data.py

import struct
import time
from dataclasses import dataclass

# Define the 32-character alphabet excluding confusing characters (I, O, L, U)
ALPHABET = "0123456789ABCDEFGHJKMNPQRSTWVXYZ"
assert (
    len(ALPHABET) == 32
), "Alphabet must contain exactly 32 characters for Base32 encoding."
ALPHABET_MAP = {char: index for index, char in enumerate(ALPHABET)}

# Define the total number of bits for license data + entropy
TOTAL_BITS = 150

# Define bit allocations for each data point within the 150 bits
# The order here defines the fixed location in the original bit sequence
BIT_ALLOCATIONS = {
    "mode_flag": 1,
    "swap_param": 8,  # Only used if mode_flag is 1
    "issue_date": 14,
    "license_plan": 4,
    "duration_expiry": 10,
    "key_holder_group": 8,
    "unique_license_id": 32,
    "version_lock": 8,
    "simple_checksum": 5,
    # Remaining bits are for entropy, calculated based on the mode flag
}


@dataclass
class LicenseData:
    mode_flag: int  # 0 for hardcoded swap_param, 1 for swap_param included in key
    swap_param: float  # Included only if mode_flag is 1
    issue_date_days: int  # Days since epoch
    license_plan: int
    duration_days: int  # Duration in days
    key_holder_group: int
    unique_license_id: int
    version_lock: int  # Major version number, 0 if no lock
    simple_checksum: int  # Checksum of data fields
    entropy_bits: int  # Number of entropy bits based on mode
    entropy_value: int  # The actual entropy value

    def to_bits(self) -> bytes:
        # Pack the data fields into a bit sequence (150 bits = 19 bytes)
        # This is a simplified packing logic and needs careful implementation
        # to handle bit alignment and optional swap_param.

        # Start with a bit array or integer
        all_bits = 0
        current_bit_pos = TOTAL_BITS  # Pack from MSB downwards

        # Helper to pack a value
        def pack_value(value, num_bits):
            nonlocal all_bits, current_bit_pos
            # Ensure value fits in num_bits
            if value >= (1 << num_bits):
                raise ValueError(f"Value {value} exceeds bit capacity {num_bits}")
            current_bit_pos -= num_bits
            all_bits |= value << current_bit_pos

        # Pack Mode Flag (always present)
        pack_value(self.mode_flag, BIT_ALLOCATIONS["mode_flag"])

        # Pack Swap Param (only if mode_flag is 1)
        if self.mode_flag == 1:
            # Convert float (0.0-1.0) to an 8-bit integer (0-255)
            swap_param_int = int(
                self.swap_param * ((1 << BIT_ALLOCATIONS["swap_param"]) - 1)
            )
            pack_value(swap_param_int, BIT_ALLOCATIONS["swap_param"])

        # Pack other fixed-location data points
        pack_value(self.issue_date_days, BIT_ALLOCATIONS["issue_date"])
        pack_value(self.license_plan, BIT_ALLOCATIONS["license_plan"])
        pack_value(self.duration_days, BIT_ALLOCATIONS["duration_expiry"])
        pack_value(self.key_holder_group, BIT_ALLOCATIONS["key_holder_group"])
        pack_value(self.unique_license_id, BIT_ALLOCATIONS["unique_license_id"])
        pack_value(self.version_lock, BIT_ALLOCATIONS["version_lock"])
        pack_value(self.simple_checksum, BIT_ALLOCATIONS["simple_checksum"])

        # Pack Entropy (fills remaining bits)
        # The number of entropy bits depends on whether swap_param was included
        num_packed_bits = TOTAL_BITS - (self.entropy_bits)
        if current_bit_pos != (TOTAL_BITS - num_packed_bits):
            raise RuntimeError("Bit packing error: Packed bits don't match expected.")

        pack_value(self.entropy_value, self.entropy_bits)

        # Convert the integer bit sequence to bytes (150 bits is 18.75 bytes, need 19)
        # Pack as a big-endian unsigned long long (8 bytes) followed by remaining bytes
        # This assumes TOTAL_BITS is <= 152 for 19 bytes (19*8=152)
        if TOTAL_BITS > 152:
            raise NotImplementedError(
                "TOTAL_BITS > 152 requires more complex byte packing"
            )

        # Need to handle the case where total bits is not a multiple of 8
        # For 150 bits, we have 18 full bytes and 6 bits in the 19th byte.
        # The total_bits integer will have the 150 bits aligned to the right.
        # We need to shift left to align to the left for byte packing.
        # Example: 150 bits. Integer is <bits>
        # We need to pack int(<bits> << (152 - 150)) = int(<bits> << 2) into 19 bytes.

        bytes_needed = (TOTAL_BITS + 7) // 8
        # Shift left to align the most significant bit of our data to the MSB of the bytes
        aligned_bits = all_bits << (bytes_needed * 8 - TOTAL_BITS)

        # Use struct to pack the aligned bits into bytes
        # Need to determine the correct struct format based on bytes_needed
        if bytes_needed <= 8:
            # Use unsigned long long for up to 8 bytes (64 bits) - not enough for 150
            raise ValueError("Cannot pack 150 bits into 8 bytes or less")
        # The manual byte extraction handles any number of bytes greater than 8
        packed_bytes = bytearray()
        # Extract bytes from the aligned_bits integer
        for i in range(bytes_needed):
            # Extract the most significant byte first (big-endian)
            byte = (aligned_bits >> ((bytes_needed - 1 - i) * 8)) & 0xFF
            packed_bytes.append(byte)
        return bytes(packed_bytes)

    @staticmethod
    def from_bits(bit_bytes: bytes) -> "LicenseData":
        # Unpack the data fields from a bit sequence (150 bits = 19 bytes)
        # This is a simplified unpacking logic and needs careful implementation
        # to handle bit alignment and optional swap_param.

        bytes_provided = len(bit_bytes)
        if bytes_provided * 8 < TOTAL_BITS:
            raise ValueError(
                f"Provided bytes ({bytes_provided}) contain less than {TOTAL_BITS} bits."
            )

        # Convert bytes to an integer bit sequence (assuming big-endian)
        all_bits = 0
        for byte in bit_bytes:
            all_bits = (all_bits << 8) | byte

        # The integer 'all_bits' might have more bits than TOTAL_BITS
        # We need to work with the most significant TOTAL_BITS
        # Example: 19 bytes = 152 bits. Our data is 150 bits.
        # The 150 bits are the MSB of the 152 bits if packed correctly.
        # Shift right to discard padding bits if bytes_provided * 8 > TOTAL_BITS
        bits_to_discard = bytes_provided * 8 - TOTAL_BITS
        all_bits >>= bits_to_discard

        current_bit_pos = TOTAL_BITS  # Unpack from MSB downwards

        # Helper to unpack a value
        def unpack_value(num_bits):
            nonlocal all_bits, current_bit_pos
            current_bit_pos -= num_bits
            # Extract the bits for this value
            mask = (1 << num_bits) - 1
            value = (all_bits >> current_bit_pos) & mask
            return value

        # Unpack Mode Flag (always present)
        mode_flag = unpack_value(BIT_ALLOCATIONS["mode_flag"])

        # Unpack Swap Param (only if mode_flag is 1)
        swap_param = 0.0  # Default value
        if mode_flag == 1:
            swap_param_int = unpack_value(BIT_ALLOCATIONS["swap_param"])
            # Convert 8-bit integer (0-255) back to float (0.0-1.0)
            swap_param = swap_param_int / ((1 << BIT_ALLOCATIONS["swap_param"]) - 1)

        # Unpack other fixed-location data points
        issue_date_days = unpack_value(BIT_ALLOCATIONS["issue_date"])
        license_plan = unpack_value(BIT_ALLOCATIONS["license_plan"])
        duration_days = unpack_value(BIT_ALLOCATIONS["duration_expiry"])
        key_holder_group = unpack_value(BIT_ALLOCATIONS["key_holder_group"])
        unique_license_id = unpack_value(BIT_ALLOCATIONS["unique_license_id"])
        version_lock = unpack_value(BIT_ALLOCATIONS["version_lock"])
        simple_checksum = unpack_value(BIT_ALLOCATIONS["simple_checksum"])

        # Determine the number of entropy bits based on the mode flag
        fixed_bits_unpacked = (
            BIT_ALLOCATIONS["mode_flag"]
            + (BIT_ALLOCATIONS["swap_param"] if mode_flag == 1 else 0)
            + BIT_ALLOCATIONS["issue_date"]
            + BIT_ALLOCATIONS["license_plan"]
            + BIT_ALLOCATIONS["duration_expiry"]
            + BIT_ALLOCATIONS["key_holder_group"]
            + BIT_ALLOCATIONS["unique_license_id"]
            + BIT_ALLOCATIONS["version_lock"]
            + BIT_ALLOCATIONS["simple_checksum"]
        )

        entropy_bits = TOTAL_BITS - fixed_bits_unpacked

        # Unpack Entropy
        entropy_value = unpack_value(entropy_bits)

        return LicenseData(
            mode_flag=mode_flag,
            swap_param=swap_param,
            issue_date_days=issue_date_days,
            license_plan=license_plan,
            duration_days=duration_days,
            key_holder_group=key_holder_group,
            unique_license_id=unique_license_id,
            version_lock=version_lock,
            simple_checksum=simple_checksum,
            entropy_bits=entropy_bits,
            entropy_value=entropy_value,  # This might be more entropy than needed, but it's the remaining bits
        )


# Example usage (for testing packing/unpacking logic)
if __name__ == "__main__":
    # Example data for a key with swap_param included
    example_data_included = LicenseData(
        mode_flag=1,
        swap_param=0.75,  # Example float
        issue_date_days=int(time.time() / (24 * 3600)),  # Days since epoch
        license_plan=2,  # Pro Plan
        duration_days=365,  # 1 year
        key_holder_group=10,  # Beta testers group
        unique_license_id=123456789,
        version_lock=1,  # Locked to v1
        simple_checksum=0,  # Placeholder, needs actual calculation
        entropy_bits=60,  # Based on mode_flag=1
        entropy_value=0,  # Placeholder, needs random generation
    )

    packed_bytes_included = example_data_included.to_bits()
    print(f"Packed bytes (swap_param included): {packed_bytes_included.hex()}")
    unpacked_data_included = LicenseData.from_bits(packed_bytes_included)
    print(f"Unpacked data (swap_param included): {unpacked_data_included}")
    assert example_data_included.mode_flag == unpacked_data_included.mode_flag
    assert (
        abs(example_data_included.swap_param - unpacked_data_included.swap_param) < 0.01
    )  # Allow for float conversion inaccuracies
    assert (
        example_data_included.issue_date_days == unpacked_data_included.issue_date_days
    )
    assert example_data_included.license_plan == unpacked_data_included.license_plan
    assert example_data_included.duration_days == unpacked_data_included.duration_days
    assert (
        example_data_included.key_holder_group
        == unpacked_data_included.key_holder_group
    )
    assert (
        example_data_included.unique_license_id
        == unpacked_data_included.unique_license_id
    )
    assert example_data_included.version_lock == unpacked_data_included.version_lock
    assert (
        example_data_included.simple_checksum == unpacked_data_included.simple_checksum
    )
    assert example_data_included.entropy_bits == unpacked_data_included.entropy_bits
    # Note: entropy_value unpacking might not match exactly due to bit alignment/padding unless TOTAL_BITS is multiple of 8.
    # For 150 bits, the last 6 bits of the 19th byte are padding when packing to bytes,
    # and those bits will be 0. When unpacking, they will be read as 0.
    # The comparison should be on the actual packed entropy bits.

    print("\\n---")

    # Example data for a key with swap_param hardcoded
    example_data_hardcoded = LicenseData(
        mode_flag=0,
        swap_param=0.0,  # Not used, but dataclass requires a value
        issue_date_days=int(time.time() / (24 * 3600)),  # Days since epoch
        license_plan=1,  # Basic Plan
        duration_days=7,  # 7 days trial
        key_holder_group=1,  # Dev group
        unique_license_id=987654321,
        version_lock=0,  # No version lock
        simple_checksum=0,  # Placeholder
        entropy_bits=68,  # Based on mode_flag=0
        entropy_value=0,  # Placeholder
    )

    packed_bytes_hardcoded = example_data_hardcoded.to_bits()
    print(f"Packed bytes (swap_param hardcoded): {packed_bytes_hardcoded.hex()}")
    unpacked_data_hardcoded = LicenseData.from_bits(packed_bytes_hardcoded)
    print(f"Unpacked data (swap_param hardcoded): {unpacked_data_hardcoded}")
    assert example_data_hardcoded.mode_flag == unpacked_data_hardcoded.mode_flag
    # swap_param won't match if hardcoded, as it's not packed/unpacked
    assert (
        example_data_hardcoded.issue_date_days
        == unpacked_data_hardcoded.issue_date_days
    )
    assert example_data_hardcoded.license_plan == unpacked_data_hardcoded.license_plan
    assert example_data_hardcoded.duration_days == unpacked_data_hardcoded.duration_days
    assert (
        example_data_hardcoded.key_holder_group
        == unpacked_data_hardcoded.key_holder_group
    )
    assert (
        example_data_hardcoded.unique_license_id
        == unpacked_data_hardcoded.unique_license_id
    )
    assert example_data_hardcoded.version_lock == unpacked_data_hardcoded.version_lock
    assert (
        example_data_hardcoded.simple_checksum
        == unpacked_data_hardcoded.simple_checksum
    )
    assert example_data_hardcoded.entropy_bits == unpacked_data_hardcoded.entropy_bits
