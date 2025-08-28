# src/licensee/license_manager.py

import random
import time
import math
from typing import Optional
from datetime import datetime, timezone, timedelta

# Import components from our licensee package
from .license_data import LicenseData, BIT_ALLOCATIONS, TOTAL_BITS, ALPHABET
from .encoding import bits_to_chars, chars_to_bits, ENCODED_CHARS_LEN
from .permutation import (
    get_permutation_map,
    get_inverse_permutation_map,
    apply_permutation,
    apply_inverse_permutation,
    TOTAL_CHARS_TO_PERMUTE,
)
from .crypto import (
    load_private_key,
    load_public_key,
    sign_data,
    verify_signature,
)  # Make sure to replace load_public_key with actual loading in production
from .encoding import bytes_to_alphabet_string, alphabet_string_to_bytes

# Define a consistent epoch start date (e.g., beginning of 2024 UTC)
EPOCH_START_DATE = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

# Define the expected bit length for the digital signature (RSA-2048)
SIGNATURE_BIT_LENGTH = 2048  # RSA-2048 signature size in bits

# --- Helper Functions ---


def calculate_simple_checksum(license_data: LicenseData) -> int:
    """Calculates a simple checksum of the license data fields.

    This is a non-cryptographic checksum for quick validation.
    Does NOT include swap_param or entropy_value in calculation directly,
    but operates on data that includes mode_flag.
    """
    # Create a list of values to checksum (excluding swap_param and entropy_value)
    # Note: The order of values here should be consistent with packing/unpacking logic
    values_to_checksum = [
        license_data.mode_flag,
        license_data.issue_date_days,
        license_data.license_plan,
        license_data.duration_days,
        license_data.key_holder_group,
        license_data.unique_license_id,
        license_data.version_lock,
    ]

    checksum_value = sum(values_to_checksum) % (
        1 << BIT_ALLOCATIONS["simple_checksum"]
    )  # Ensure checksum fits in allocated bits
    return checksum_value


# --- License Key Generation ---


def generate_license_key(
    private_key,
    license_plan: int,
    duration_days: int,
    key_holder_group: int,
    unique_license_id: int,
    version_lock: int = 0,  # 0 means no version lock
    use_included_swap_param: bool = True,  # If False, validator needs hardcoded param
    fixed_swap_param: Optional[
        float
    ] = None,  # Used if use_included_swap_param is False
) -> str:
    """Generates a new license key string.

    Args:
        private_key: The private key for signing the data.
        license_plan: The integer ID of the license plan.
        duration_days: The duration of the license in days.
        key_holder_group: The integer ID of the key holder group.
        unique_license_id: A unique integer ID for this license key.
        version_lock: The major version number the key is locked to (0 for none).
        use_included_swap_param: Whether to include a randomly generated swap_param in the key.
                                 If False, the validator must have a hardcoded swap_param.
        fixed_swap_param: A specific swap_param float to use if use_included_swap_param is False.

    Returns:
        The formatted license key string.

    Raises:
        ValueError: If fixed_swap_param is not provided when use_included_swap_param is False.
        NotImplementedError: If private key loading is not implemented.
    """
    mode_flag = 1 if use_included_swap_param else 0
    swap_param = 0.0  # Default if hardcoded
    if use_included_swap_param:
        swap_param = random.random()
    else:
        if fixed_swap_param is None:
            raise ValueError(
                "fixed_swap_param must be provided if use_included_swap_param is False"
            )
        swap_param = fixed_swap_param

    # Calculate entropy bits based on mode flag
    fixed_data_bits = (
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

    entropy_bits = TOTAL_BITS - fixed_data_bits
    # Ensure entropy_bits is non-negative
    if entropy_bits < 0:
        raise ValueError("Bit allocation error: Fixed data bits exceed total bits.")

    entropy_value = random.getrandbits(entropy_bits) if entropy_bits > 0 else 0

    # Get current date in days since epoch
    now_utc = datetime.now(timezone.utc)
    issue_date_days = (now_utc - EPOCH_START_DATE).days
    if issue_date_days < 0:
        # Should not happen if EPOCH_START_DATE is in the past
        issue_date_days = 0

    # Create LicenseData object (calculate checksum first)
    # Temporarily create a LicenseData object without checksum and entropy to calculate checksum
    # Note: For checksum calculation, include fields that contribute to it.
    temp_license_data = LicenseData(
        mode_flag=mode_flag,
        swap_param=swap_param,  # Use the determined swap_param for checksum calculation consistency if needed
        issue_date_days=issue_date_days,
        license_plan=license_plan,
        duration_days=duration_days,
        key_holder_group=key_holder_group,
        unique_license_id=unique_license_id,
        version_lock=version_lock,
        simple_checksum=0,  # Placeholder for checksum calculation
        entropy_bits=entropy_bits,  # Pass correct entropy_bits count for checksum calc consistency
        entropy_value=0,  # Placeholder
    )
    # Calculate checksum based on relevant fields BEFORE packing
    simple_checksum = calculate_simple_checksum(temp_license_data)

    # Now create the final LicenseData object with the calculated checksum and actual entropy
    final_license_data = LicenseData(
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
        entropy_value=entropy_value,
    )

    # 1. Pack LicenseData into 150 bits (19 bytes)
    license_data_bytes = final_license_data.to_bits()

    # 2. Sign license data bytes
    # The signature will be based on the original packed license data, not the permuted string.
    signature_bytes = sign_data(license_data_bytes, private_key)

    # 3. Concatenate license data bytes and signature bytes
    # The total will be 19 bytes (license data) + SIGNATURE_BIT_LENGTH / 8 bytes (signature)
    # Assuming RSA-2048 (256 bytes):
    combined_bytes = license_data_bytes + signature_bytes

    # 4. Encode combined bytes into characters (using our ALPHABET)
    # Total bits = 150 (license) + 2048 (signature) = 2198 bits
    # Characters needed = ceil(2198 / 5) = 440 characters
    original_440_chars = bytes_to_alphabet_string(combined_bytes)

    # 5. Apply Sine Permutation to the 440 characters
    # Get the swap_param used (either random or fixed)
    actual_swap_param_for_permutation = swap_param

    perm_map = get_permutation_map(actual_swap_param_for_permutation)
    # Permute the entire 440 characters string
    permuted_440_chars = apply_permutation(original_440_chars, perm_map)

    # 6. Format Final Key by segmenting the 440 permuted characters
    # Break the 440 permuted characters into 5-char segments (440 / 5 = 88 segments)
    # The key format will be AAAAA-BBBBB-... (88 segments)
    # We need to adjust the segmentation loop and potentially the validation parsing.

    # Let's stick to the original segmentation pattern (6 segments of 5 chars) for consistency,
    # but the total permuted length is 440. We need to decide how to present a 440-char key.
    # The previous format was 6 segments of 5 chars + signature section. Total chars = 30 + sig_chars.
    # Now total chars is 440, all are permuted.
    # Let's segment into 5-char chunks separated by hyphens.

    segment_length = 5
    num_segments = len(permuted_440_chars) // segment_length
    segmented_chars = "-".join(
        [
            permuted_440_chars[i : i + segment_length]
            for i in range(0, len(permuted_440_chars), segment_length)
        ]
    )

    final_key = (
        segmented_chars  # The entire key is now the segmented, permuted characters.
    )

    return final_key


# --- License Key Validation ---


def validate_license_key(
    license_key_string: str,
    current_app_version: int,  # Added parameter for version lock check
    hardcoded_swap_param: Optional[
        float
    ] = None,  # Required if the key's mode_flag is 0
) -> Optional[LicenseData]:
    """Validates a license key string and returns the license data if valid.

    Args:
        license_key_string: The license key string to validate.
        current_app_version: The current major version of the application.
        hardcoded_swap_param: The hardcoded swap_param to use if the key's mode_flag is 0.

    Returns:
        A LicenseData object if the key is valid, None otherwise.
    """
    # print(f"Attempting to validate key: {license_key_string}") # Debugging

    # 1. Parse Key
    parts = license_key_string.split("-")
    if len(parts) != 7:  # 6 segments + 1 signature
        # print("Validation failed: Incorrect number of parts.")
        return None

    segmented_chars = parts[:6]
    encoded_signature = parts[6]

    # Reconstruct the 30 permuted characters string
    permuted_chars = "".join(segmented_chars)

    if len(permuted_chars) != TOTAL_CHARS_TO_PERMUTE:
        # print(f"Validation failed: Incorrect number of permuted characters ({len(permuted_chars)}).")
        return None

    # Decode signature (using our ALPHABET)
    try:
        # Use alphabet_string_to_bytes and specify the expected bit length
        signature_bytes = alphabet_string_to_bytes(
            encoded_signature, SIGNATURE_BIT_LENGTH
        )
    except ValueError:
        # print("Validation failed: Invalid signature encoding (expected ALPHABET string).")
        return None

    # 2. Verify Signature
    data_to_verify = permuted_chars.encode("ascii")  # Assuming permuted chars are ASCII
    # Load public key (implement securely!)
    # For testing, using the dummy loader. Replace with actual public key loading.
    public_key = load_public_key()

    if not verify_signature(data_to_verify, signature_bytes, public_key):
        # print("Validation failed: Signature verification failed.")
        return None

    # Signature is valid. Now determine swap_param and un-permute.

    # 3. Determine Swap Parameter and Mode Flag
    # This is the most complex part. We need to get the mode_flag and swap_param
    # bits from the permuted_chars. This requires knowing the inverse permutation,
    # which depends on the swap_param.

    # We will use the robust helper function that either uses the hardcoded_swap_param
    # (if provided) or attempts to brute-force the swap_param from the permuted data
    # based on expected mode_flag = 1 and checksum validation.

    # --- Robust Swap Param Determination Helper ---
    def get_mode_and_swap_param_from_permuted_chars_robust(
        permuted_chars: str, hardcoded_swap_param: Optional[float]
    ) -> tuple[int, float, Optional[LicenseData]]:
        """ROBUST helper to determine mode_flag and swap_param, and return unpacked data.

        If hardcoded_swap_param is provided, assumes mode=0 and uses that value.
        If not provided, attempts to brute-force swap_param (256 values) for mode=1.

        Returns: (mode_flag, determined_swap_param, unpacked_license_data) or (-1, 0.0, None) on failure.
        """
        # Try the hardcoded swap_param scenario first (Mode 0)
        if hardcoded_swap_param is not None:
            try:
                # Attempt un-permutation and unpacking with the hardcoded param
                perm_map = get_permutation_map(hardcoded_swap_param)
                inv_perm_map = get_inverse_permutation_map(perm_map)
                original_chars = apply_inverse_permutation(permuted_chars, inv_perm_map)
                original_bit_bytes = chars_to_bits(original_chars)
                unpacked_data = LicenseData.from_bits(original_bit_bytes)

                # If successfully unpacked and mode flag is 0 and checksum matches, we found it.
                if unpacked_data.mode_flag == 0:
                    calculated_checksum = calculate_simple_checksum(unpacked_data)
                    if unpacked_data.simple_checksum == calculated_checksum:
                        # print("Successfully validated with hardcoded swap_param.")
                        return 0, hardcoded_swap_param, unpacked_data

            except Exception:
                # Ignore errors, continue to brute force if hardcoded_swap_param was None
                pass  # print(f"Attempt with hardcoded swap_param {hardcoded_swap_param} failed: {e}")

        # If hardcoded_swap_param was not provided or failed, attempt brute-force for included swap_param (Mode 1)
        if hardcoded_swap_param is None:
            # print("Attempting to brute-force swap_param for mode 1...")
            # Iterate through all possible 8-bit swap_param values (0 to 255)
            for swap_param_int in range(1 << BIT_ALLOCATIONS["swap_param"]):
                # Convert int to float (ensure division by float for accurate float conversion)
                current_swap_param = swap_param_int / float(
                    (1 << BIT_ALLOCATIONS["swap_param"]) - 1
                )

                try:
                    # Attempt un-permutation and unpacking with the current swap_param guess
                    perm_map = get_permutation_map(current_swap_param)
                    inv_perm_map = get_inverse_permutation_map(perm_map)
                    original_chars = apply_inverse_permutation(
                        permuted_chars, inv_perm_map
                    )
                    original_bit_bytes = chars_to_bits(original_chars)
                    unpacked_data = LicenseData.from_bits(original_bit_bytes)

                    # If successfully unpacked and mode flag is 1 and swap_param matches and checksum matches, we found it.
                    # Allow for small float comparison inaccuracies
                    if (
                        unpacked_data.mode_flag == 1
                        and abs(unpacked_data.swap_param - current_swap_param) < 0.01
                    ):
                        calculated_checksum = calculate_simple_checksum(unpacked_data)
                        if unpacked_data.simple_checksum == calculated_checksum:
                            # print(f"Successfully brute-forced swap_param: {current_swap_param}")
                            return 1, current_swap_param, unpacked_data

                except Exception:
                    # Ignore errors for this swap_param value
                    pass  # print(f"Attempt with swap_param {current_swap_param} failed: {e}")

            # print("Brute-force failed.")

        # If neither hardcoded nor brute-force for included swap_param worked
        return -1, 0.0, None  # Indicate failure

    # Call the robust helper to get mode, swap_param, and unpacked data
    mode_flag, determined_swap_param, unpacked_license_data = (
        get_mode_and_swap_param_from_permuted_chars_robust(
            permuted_chars, hardcoded_swap_param
        )
    )

    if mode_flag == -1 or unpacked_license_data is None:
        # print("Validation failed: Could not determine mode flag and swap parameter or unpack data.")
        return None

    # Data is unpacked and mode/swap_param determined. Now validate the content.

    # 4. Validate Data Consistency (Checksum - already done in robust helper, but re-check mode consistency)
    if mode_flag != unpacked_license_data.mode_flag:
        # This is a safety check, should be consistent if robust helper worked.
        # print(f"Validation failed: Mode flag inconsistency after robust helper. Determined {mode_flag}, unpacked {unpacked_license_data.mode_flag}.")
        return None

    # Check simple checksum (re-calculate to be safe, though robust helper did this)
    calculated_checksum = calculate_simple_checksum(unpacked_license_data)
    if unpacked_license_data.simple_checksum != calculated_checksum:
        # print(f"Validation failed: Checksum mismatch after robust helper. Expected {unpacked_license_data.simple_checksum}, calculated {calculated_checksum}.")
        return None

    # 5. Validate License Data (Expiry, Version Lock)

    # Check Expiry
    issue_date = EPOCH_START_DATE + timedelta(
        days=unpacked_license_data.issue_date_days
    )
    expiry_date = issue_date + timedelta(days=unpacked_license_data.duration_days)
    now_utc = datetime.now(timezone.utc)

    if now_utc > expiry_date:
        # print("Validation failed: License has expired.")
        return None

    # Check Version Lock (if version_lock > 0)
    if (
        unpacked_license_data.version_lock > 0
        and unpacked_license_data.version_lock != current_app_version
    ):
        # print(f"Validation failed: Version lock mismatch. Key version {unpacked_license_data.version_lock}, current version {current_app_version}.")
        return None

    # If all checks pass
    # print("License key is valid.")
    return unpacked_license_data


# Example Usage (within license_manager.py)
if __name__ == "__main__":
    print("--- Testing License Key Generation and Validation ---")

    # --- Scenario 1: Key with swap_param included ---
    print("\nScenario 1: Generating key with included swap_param...")
    try:
        generated_key_included = generate_license_key(
            private_key=None,
            license_plan=3,  # Enterprise
            duration_days=730,  # 2 years
            key_holder_group=50,  # Commercial Customer
            unique_license_id=98765,
            version_lock=2,  # Locked to v2
            use_included_swap_param=True,
        )
        print(f"Generated Key (Included Swap Param): {generated_key_included}")

        print("Validating key (Included Swap Param) with no hardcoded_swap_param...")
        validated_data_included = validate_license_key(
            generated_key_included, current_app_version=2, hardcoded_swap_param=None
        )

        if validated_data_included:
            print("Validation Successful for Included Swap Param Key.")
            print(f"Unpacked Data: {validated_data_included}")
            assert validated_data_included.mode_flag == 1
            assert validated_data_included.license_plan == 3
            assert validated_data_included.version_lock == 2
            # Add more assertions for other fields
        else:
            print("Validation Failed for Included Swap Param Key.")

        print(
            "Validating key (Included Swap Param) with incorrect hardcoded_swap_param..."
        )
        # This should correctly fail because the key expects an included swap_param (mode=1)
        # but we are providing a hardcoded one, which will be tried first by the robust helper.
        validated_data_included_wrong_hardcoded = validate_license_key(
            generated_key_included, current_app_version=2, hardcoded_swap_param=0.1
        )
        if not validated_data_included_wrong_hardcoded:
            print("Validation correctly failed with incorrect hardcoded_swap_param.")
        else:
            print(
                "Validation INCORRECTLY succeeded with incorrect hardcoded_swap_param."
            )

    except NotImplementedError:
        print("Skipping Scenario 1 due to unimplemented private key loading.")
    except Exception as e:
        print(f"An error occurred during Scenario 1: {e}")

    print("\n---")

    # --- Scenario 2: Key with swap_param hardcoded (requires validator to provide param) ---
    print(
        "\nScenario 2: Generating key with swap_param hardcoded (requires validator to know param)..."
    )
    try:
        # Define a specific hardcoded swap_param for this scenario
        hardcoded_param_for_test = 0.88
        generated_key_hardcoded = generate_license_key(
            private_key=None,
            license_plan=1,  # Basic
            duration_days=30,  # 30 days trial
            key_holder_group=1,  # Dev
            unique_license_id=112233,
            version_lock=0,  # No lock
            use_included_swap_param=False,
            fixed_swap_param=hardcoded_param_for_test,  # Provide the param to generator so it knows which to use
        )
        print(f"Generated Key (Hardcoded Swap Param): {generated_key_hardcoded}")

        print(
            f"Validating key (Hardcoded Swap Param) providing the correct hardcoded_swap_param ({hardcoded_param_for_test})..."
        )
        validated_data_hardcoded = validate_license_key(
            generated_key_hardcoded,
            current_app_version=1,
            hardcoded_swap_param=hardcoded_param_for_test,
        )

        if validated_data_hardcoded:
            print("Validation Successful for Hardcoded Swap Param Key.")
            print(f"Unpacked Data: {validated_data_hardcoded}")
            assert validated_data_hardcoded.mode_flag == 0
            assert validated_data_hardcoded.license_plan == 1
            assert validated_data_hardcoded.version_lock == 0
            # Add more assertions
        else:
            print("Validation Failed for Hardcoded Swap Param Key.")

        print(
            "Validating key (Hardcoded Swap Param) WITHOUT providing hardcoded_swap_param (should fail)..."
        )
        # This will trigger the mode=1 brute-force path in the robust helper, which should not find a mode=0 key.
        validated_data_hardcoded_no_param = validate_license_key(
            generated_key_hardcoded, current_app_version=1, hardcoded_swap_param=None
        )
        if not validated_data_hardcoded_no_param:
            print("Validation correctly failed without hardcoded_swap_param.")
        else:
            print("Validation INCORRECTLY succeeded without hardcoded_swap_param.")

        print(
            "Validating key (Hardcoded Swap Param) with incorrect hardcoded_swap_param..."
        )
        validated_data_hardcoded_wrong_param = validate_license_key(
            generated_key_hardcoded, current_app_version=1, hardcoded_swap_param=0.1
        )
        if not validated_data_hardcoded_wrong_param:
            print("Validation correctly failed with incorrect hardcoded_swap_param.")
        else:
            print(
                "Validation INCORRECTLY succeeded with incorrect hardcoded_swap_param."
            )

    except NotImplementedError:
        print("Skipping Scenario 2 due to unimplemented private key loading.")
    except Exception as e:
        print(f"An error occurred during Scenario 2: {e}")
