Blockchain-Powered Two-Factor Authentication for Mobile Banking

**Overview**
SecuredKey is a Python- and Flask-based prototype that enhances mobile banking transaction security by 
combining SMS-based One-Time Password (OTP) verification with blockchain-based transaction records. 
It uses ECDSA cryptography (SECP256k1) for account key generation and transaction signing to support 
transaction authenticity, integrity, and traceability.

**Features**
Two-Factor Authentication: SMS-based OTP verification using Twilio
Cryptographic Security: ECDSA key pairs and digital signatures for transaction authentication.
Blockchain-Based Records: Stores transaction details in a blockchain-style ledger.
Transaction Traceability: Records sender, receiver, amount, timestamp, and digital signature.
Multi-User Support: Supports transactions involving multiple user accounts.

**Technologies**
Python
Flask
Blockchain
ECDSA (SECP256k1)
Twilio API

**Disclaimer**
This projeintended for production banking use without further security testing and auditing.
It is a security prototype developed for educational and research purposes. 
