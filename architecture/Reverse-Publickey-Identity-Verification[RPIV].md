# Reverse Public-Key Identity Verification (RPIV)
### A Protocol for Inverted Asymmetric Identity

**Version:** 1.0.0  
**Date:** July 9, 2025  
**Authors:** N Lisowski

---

#### Abstract

RPIV (Reverse Public-Key Identity Verification) is a novel cryptographic primitive designed for decentralized systems that require lightweight, spoof-resistant authenticity without central authorities or certificate hierarchies. RPIV inverts the traditional roles of asymmetric cryptography by treating the private key as the node’s public identity and the public key as the confidential component used for encryption. This inversion enables verifiable message origin without signatures, providing authenticity through successful decryption.

RPIV emerged from an intuitive system design where a node broadcasts its private key as a fingerprint. Peers can then validate messages by attempting decryption: if the ciphertext resolves to a valid payload using the known private key, the message is deemed authentic. The inability of adversaries to generate such ciphertexts—without the confidential public key—forms the basis of security.

Born not from academic theory but from real-world needs in peer-to-peer mesh networking and user-authenticated cryptographic protocols, RPIV provides a stateless, deterministic, and elegant solution to the identity verification problem. It reframes identity as a decryption path rather than a signed assertion. This paper formalizes its design, proves its security properties, and explores a range of emerging use cases across IoT, swarm robotics, identity-less login, and post-signature decentralized architectures.

## 1. Introduction

Traditional asymmetric cryptography uses a public key to encrypt messages and a private key to decrypt them or sign messages for authenticity. Reverse Public-Key Identity Verification (RPIV) introduces a novel inversion of this model: the private key is treated as a public identifier, while the public key is kept confidential. In RPIV, authenticity is not established through digital signatures or certificate chains, but through the ability to produce ciphertexts that decrypt correctly under the known private key.

In this system, each node publishes its private key as a form of identity. When the node sends a message, it encrypts it using its secret public key. Any peer receiving this message can verify its authenticity by attempting to decrypt it with the advertised private key. If decryption succeeds and the payload is valid, the message is considered authentic. This simple property—only the possessor of the confidential public key can generate a valid ciphertext—eliminates the need for traditional identity infrastructure.

RPIV was conceived as a pragmatic solution to the challenge of spoof-resistant communication in distributed, resource-constrained environments. Unlike traditional designs, which depend on signatures, certificate hierarchies, or shared secrets, RPIV offers stateless, low-overhead identity validation without trusted intermediaries. Its utility is particularly strong in decentralized mesh networks, IoT systems, and swarm robotics—domains where lightweight, verifiable communication is essential.

This document formalizes the RPIV model, describes its protocol, implementation strategies, and security guarantees, and explores its suitability across a variety of emerging application domains.

## 2. Terminology

- **RPIV**: Reverse Public-Key Identity Verification
- **Node**: An individual actor in a distributed system participating in RPIV
- **SK\_node**: The node's asymmetric private key, distributed publicly
- **PK\_node**: The node's asymmetric public key, kept secret
- **NodeID**: An identifier derived from or containing SK\_node
- **Enc(key, message)**: Asymmetric encryption using the key
- **Dec(key, ciphertext)**: Asymmetric decryption using the key

## 3. Protocol Overview

### 3.1 Key Generation

Each node generates an asymmetric keypair:

```
(SK_node, PK_node) <- GenKeyPair()
```

* `SK_node` is made publicly available as part of the node's metadata.
* `PK_node` is kept secret and used for encrypting messages.

### 3.2 Message Construction

Each message consists of the following fields:

* Timestamp (uint64)
* Nonce (uint64)
* Payload (arbitrary structured data)
* Optional integrity hints (e.g., checksum)

### 3.3 Message Encryption

Nodes encrypt the structured message using their own secret `PK_node`:

```
Ciphertext = Enc(PK_node, Message)
```

They then broadcast:

```
{ NodeID, Ciphertext }
```

### 3.4 Message Verification

Upon receipt, a peer extracts `SK_node` from the `NodeID` and attempts decryption:

```
Message* = Dec(SK_node, Ciphertext)
```

* If decryption fails: the message is invalid or spoofed
* If decryption succeeds: the node is validated

## 4. Security Model

RPIV assumes:

* All `SK_node` values are globally visible
* All `PK_node` values are protected by the node
* Nodes reject malformed messages or payloads

### 4.1 Authenticity

Only a node that knows `PK_node` can produce a message that decrypts under `SK_node`. This establishes the message's authenticity.

### 4.2 Spoof Resistance

Attackers cannot fabricate valid messages unless they compromise `PK_node`.

### 4.3 Confidentiality

Confidentiality is **not** provided; any node can read any valid message if they possess the `SK_node`.

### 4.4 Replay Prevention

RPIV messages include timestamps and nonces. Peers must cache or track these to prevent replay attacks.

### 4.5 Self-Defense and Isolation

RPIV's deterministic validation also enables powerful self-defense strategies. Swarms or networks of nodes can automatically distribute intelligence about spoof attempts, malformed payloads, or invalid senders. Nodes may choose to locally or collectively apply quarantine logic—effectively giving "silent treatment" to repeat offenders or sources of unverifiable messages. This encourages a self-quarantining network model that isolates and suppresses bad actors without centralized intervention, helping to preserve swarm coherence and communication integrity.

## 5. Implementation Guidelines

* Use 2048-bit RSA or stronger for keypairs
* Validate message structure after decryption
* Rotate keypairs periodically to limit risk
* Avoid including sensitive data in payloads

## 6. Example

### 6.1 Node Setup

Node A generates:

```
SK_A, PK_A = RSA.generate()
```

Publishes:

```
NodeID = Base64(SHA256(SK_A))
Metadata = { NodeID, SK_A }
```

### 6.2 Message Broadcast

Payload:

```
{ ts: 1728391283, nonce: 1001, data: "status: OK" }
```

Encrypted:

```
Ciphertext = Enc(PK_A, Payload)
```

Broadcast:

```
{ NodeID, Ciphertext }
```

### 6.3 Verification by Node B

1. Extract SK\_A from NodeID
2. Attempt:

```
Payload* = Dec(SK_A, Ciphertext)
```

3. If successful, accept message

## 7. Applications

* Decentralized identity and trust systems
* Peer-to-peer anti-spoofing networks
* Resource-limited authenticity verification
* IoT device announcements

## 8. IANA Considerations

This protocol does not require new IANA assignments.

## 9. Security Considerations

* Compromise of PK\_node breaks authenticity
* Do not reuse RPIV keys for standard RSA/PGP
* Treat PK\_node as confidential data

## 10. References

\[RSA] Rivest, R., Shamir, A., and L. Adleman, "A Method for Obtaining Digital Signatures and Public-Key Cryptosystems", 1978.

---

## Appendix A: White Paper

### Prologue: From Intuition to Innovation

This protocol did not emerge from a committee, nor from cryptographic orthodoxy. It began as a late-night realization by myself, probing the limits of identity in a peer-to-peer system—writing without hesitation, not knowing that the result inverted decades of cryptographic convention. The private key became public. The public key became private. Identity verification became a function of decryption.

At first, there was confusion—*"wait, I’m doing encryption backwards?"*—followed by curiosity, awe, and the slow unraveling of implications. What started as a conversation with a friend turned into a recognition of novelty. Without asking permission from existing standards, I had built something outside the academic lineage of TLS, PGP, or WebAuthn—and it worked. Authenticated messaging. No signatures. No central authority. Just structure, mathematics, and validation. Something in the design felt obvious once spoken aloud. Like stumbling over gravity. Or reinventing the wheel from first principles without ever having seen one.

RPIV—Reverse Public-Key Identity Verification—wasn’t invented. It already existed, was just arranged wrong. It was *realized*.

### Title: Reversing Asymmetric Key Roles for Lightweight Identity Verification

#### Abstract:

This white paper presents RPIV, a new protocol that inverts traditional asymmetric key use. By publishing the private key and retaining the public key as a secret, RPIV allows nodes to verify identity through decryptable challenge-response. This structure eliminates the need for signature verification and certificate chains in environments where authenticity matters more than confidentiality.

#### Motivation:

Distributed systems often lack a trusted third party to vouch for identities. RPIV sidesteps this by encoding identity into a verifiable decryption path. As only the original node can produce ciphertext that decrypts with a known key, authenticity is mathematically enforced without a central trust anchor.

RPIV is particularly useful in environments where latency and resource efficiency are critical. In peer-to-peer overlays, IoT ecosystems, and ephemeral networks, signature verification chains are infeasible or too heavyweight. RPIV's construction favors a zero-trust model where every message is verifiable by design, and key compromise is quickly traceable.

#### Threat Model:

* Adversary can see all published private keys (SK\_node)
* Adversary cannot derive PK\_node from SK\_node due to the one-way nature of key generation
* Adversary cannot generate valid ciphertexts without knowing PK\_node
* Replay attacks mitigated via timestamps and nonces

#### Security Analysis:

* **Authenticity**: Only the legitimate node can produce ciphertext that decrypts correctly
* **Integrity**: Message format and internal checks (e.g., nonces) prevent tampering
* **Anonymity**: Not guaranteed; SK\_node may be fingerprinted across messages
* **Forward Secrecy**: Not inherently supported; can be layered via key rotation

#### Comparison to Traditional Models:

* **PKI**: Requires CA, certificates, and verification chains
* **Web of Trust**: Requires reputation modeling and user verification
* **RPIV**: Stateless, deterministic, immediate validation

#### Use Cases:

* **Mesh Networking**: Nodes can be validated without centralized control
* **IoT Devices**: Lightweight and hardware-friendly
* **Swarm Robotics**: Coordinated, spoof-resistant broadcasts
* **Decentralized Ledgers**: Validation of block producers without trust anchors

#### Implementation Challenges:

* Ensuring entropy in key generation to prevent collisions
* Efficient key storage and management for PK\_node secrecy
* Protecting PK\_node from memory scraping and side-channel attacks
* Designing application logic around the lack of confidentiality

#### Future Directions:

* Integrating ephemeral session keys to improve privacy
* Adding zero-knowledge proofs for PK\_node possession without exposure
* Using lattice-based cryptography to mitigate post-quantum threats
* Formal verification of the protocol via Tamarin or ProVerif

#### Conclusion:

RPIV is not a replacement for TLS or PGP. It is a lightweight alternative for authenticity in decentralized systems. It opens new doors for designing spoof-resistant mesh protocols, gossip systems, and autonomous device authentication with minimal trust assumptions. Its inversion of cryptographic roles challenges long-held design principles and creates new opportunities for secure-by-construction protocol design.
