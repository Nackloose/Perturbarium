# **Licensee**
## A Multi-Layered Framework for Secure Software License Key Generation and Validation

**Version:** 1.0.0  
**Date:** July 9, 2025  
**Authors:** N Lisowski

---

**Algorithm Version:** 1.6  
**Security Level:** 128-bit Equivalent  
**Date:** July 10, 2025

## **Abstract**

This paper details a multi-layered mathematical framework for generating secure software license keys. The algorithm's design centers on obfuscating data in alignment with its final encoding structure. The framework integrates: **(1)** an RSA-3072 digital signature for core payload integrity; **(2)** the SineShift algorithm, which deterministically permutes the signed binary data in **5-bit chunks**; and **(3)** a final Base32-like encoding stage. This method ensures that standard byte-aligned data is thoroughly scrambled before being converted to a string, creating a compact, secure, and structurally opaque license key.

---

## **1. Introduction**

Effective software license management must prevent unauthorized use while remaining user-friendly. The primary threats include **key tampering**, **key forgery**, and **reverse engineering**.

This paper proposes a framework that combines cryptographic signing with structural obfuscation at the binary level. By permuting data in units that match the final encoding scheme, the system ensures that the relationship between the original data and the final string is non-obvious, significantly increasing the difficulty of analysis and unauthorized manipulation.

---

## **2. System Architecture and Methodology**

The algorithm constructs a complete binary key before applying a final encoding step. The structure of this binary key is conditional, determined by a leading `mode_flag`.

### **2.1 Algorithmic Flow**

The generation and validation processes are precise mirror images that pivot based on the leading bit.

#### **License Generation Flow:**

1.  **Data Packing (Payload):** Core license parameters are packed into a fixed-size binary payload, and a checksum is appended.
2.  **Cryptographic Signing (Layer 1):** The binary payload is signed using an RSA-3072 private key, producing a binary signature.
3.  **Binary Assembly:** The payload and signature are concatenated into a single binary block (the "main body"). This body is padded to ensure its length is a multiple of 5 bits.
4.  **Obfuscation (Layer 2):** The SineShift permutation algorithm is applied to the main body, rearranging its sequence of non-overlapping **5-bit chunks**.
5.  **Conditional Prefix Prepending:** A binary prefix (either 1 bit for `mode 0`, or 65 bits for `mode 1`) is prepended to the permuted body.
6.  **Encoding (Layer 3):** The entire resulting binary block is encoded into a final, human-readable character string.

#### **License Validation Flow:**

1.  **Parsing and Decoding (Layer 3):** The key is de-hyphenated and decoded back into a single binary block.
2.  **Conditional Separation:** The `mode_flag` is read from the first bit. Based on its value, the binary prefix (1 or 65 bits) is separated from the permuted binary body.
3.  **Inverse Obfuscation (Layer 2):** The inverse SineShift permutation is applied to the **5-bit chunks** of the binary body, restoring their original order.
4.  **Cryptographic Verification (Layer 1):** The restored binary body is separated into the payload and signature. The signature is verified against the payload.
5.  **Integrity and Parameter Validation:** The checksum within the payload is verified.

---

## **3. Layer 1: Cryptographic Signing**

The foundation of the key's security is its cryptographic signature.

### **3.1 RSA-3072 Digital Signature**

An RSA-3072 signature provides a 128-bit equivalent security level. It guarantees that the core license terms within the payload cannot be altered without cryptographic detection.

$S = \text{Sign}_{\text{RSA-3072-PSS}}(\text{SHA-256}(\text{Payload}), K_{\text{private}})$

---

## **4. Layer 2: Binary Obfuscation**

This layer scrambles the binary data structure to prevent analysis of the final encoded string.

### **4.1 The SineShift Algorithm**

SineShift is a deterministic permutation algorithm that rearranges the structure of the binary data. Specifically, it operates on the main binary body (payload + signature) by treating it as a sequence of non-overlapping **5-bit chunks**.

The algorithm generates a unique permutation map from a secret floating-point `swap_param`:

$\text{score}(i) = A \cdot \sin(k \cdot \gamma + i \cdot \omega) + i$

Where $i$ is the index of each 5-bit chunk. The chunks are then reordered based on their calculated scores.

By permuting the data in 5-bit groups, SineShift effectively obfuscates standard data structures that rely on 8-bit (byte) or 32-bit (word) alignment. This scrambling of byte-aligned data adds another hurdle for reverse engineering, as familiar patterns within the binary data are destroyed before the final encoding. 🧩

---

## **5. Layer 3: Data Structure and Encoding**

This layer defines the structure of the binary components and the final representation.

### **5.1 Binary Data Structure**

The complete binary key is assembled from a variable-length prefix and a fixed-length payload.

* **Binary Prefix** (1 or 65 bits): A single `mode_flag` bit. If the flag is `1`, it is immediately followed by the 64-bit `swap_param`.
* **Binary Payload** (160 bits):

    | Field               | Bits | Description                          |
    | :------------------ | :--- | :----------------------------------- |
    | `issue_date`        | 20   | Date of issue (days since epoch).    |
    | `license_plan`      | 4    | Defines the product tier or plan.    |
    | `duration_expiry`   | 16   | License duration in days.            |
    | `key_holder_group`  | 8    | User or group identifier.            |
    | `unique_license_id` | 32   | Unique identifier to prevent replay. |
    | `version_lock`      | 8    | Locks the key to a specific version. |
    | `entropy`           | 67   | Random bits for key uniqueness.      |
    | `checksum`          | 5    | Integrity checksum on the payload.   |

### **5.2 Custom Encoding Alphabet**

A final encoding step converts the complete binary key into a human-readable string using a custom 32-character alphabet.

$\Sigma = \{0,1,2,3,4,5,6,7,8,9,A,B,C,D,E,F,G,H,J,K,M,N,P,Q,R,S,T,V,W,X,Y,Z\}$

---

## **6. Security Analysis**

* **Payload Tampering Attack:** An attempt to alter the core license data will invalidate the RSA signature. This attack is computationally infeasible.
* **Permutation Tampering Attack:**
    * If `mode_flag` is **0**, this attack is impossible, as no `swap_param` is present in the key to be modified.
    * If `mode_flag` is **1**, the `swap_param` in the prefix is not signed. Security in this mode relies on the difficulty of reverse-engineering the permutation algorithm.
* **Key Forgery Attack:** An attacker cannot generate a valid signature for a new payload without the RSA private key.
* **Pattern Analysis:** Because the permutation rearranges 5-bit chunks, the final encoded characters have no discernible relationship to their original positions. Standard byte-aligned data is effectively scrambled, preventing structural analysis.
* **Replay Attack:** The `unique_license_id` within the signed payload prevents key reuse.