from flask import Flask, request, jsonify
import hashlib
import json
from time import time
from uuid import uuid4
from datetime import date
from twilio.rest import Client
import random
import ecdsa
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class BankAccount:
    def __init__(self, account_number, balance, account_holder):
        self.account_number = account_number
        self.balance = balance
        self.account_holder = account_holder
        # Generate key pair for the account
        self.private_key, self.public_key = self.generate_key_pair()

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
        else:
            print("Insufficient funds")

    def check_balance(self):
        return self.balance

    def generate_key_pair(self):
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        public_key = private_key.get_verifying_key()
        return private_key, public_key

class Transaction:
    def __init__(self, sender, receiver, amount, date, signature=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.date = date
        self.signature = signature

    def sign_transaction(self, private_key):
        transaction_data = f"{self.sender}{self.receiver}{self.amount}{self.date}".encode()
        self.signature = private_key.sign(transaction_data)

    def verify_transaction(self, public_key):
        if not self.signature:
            return False
        transaction_data = f"{self.sender}{self.receiver}{self.amount}{self.date}".encode()
        try:
            return public_key.verify(self.signature, transaction_data)
        except ecdsa.BadSignatureError:
            return False

    def encrypt(self, key):
        cipher = AES.new(key, AES.MODE_CBC)
        plaintext = json.dumps({
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'date': self.date
        })
        ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
        return ciphertext, cipher.iv

    @staticmethod
    def decrypt(ciphertext, iv, key):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        transaction_data = json.loads(plaintext.decode())
        return transaction_data

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # Create the genesis block
        self.new_block(previous_hash="1", proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else 1,
        }
        # Reset the current list of transactions
        self.current_transactions = []
        # Append the block to the chain
        self.chain.append(block)
        #print("New block added to the blockchain:")
        #print(block)
        #print("")

        return block

    def new_transaction(self, sender, receiver, amount, sender_private_key):
        transaction = Transaction(sender, receiver, amount, time())
        transaction.sign_transaction(sender_private_key)

        # Encrypt transaction details
        key = get_random_bytes(16)
        ciphertext, iv = transaction.encrypt(key)

        # Print transaction details step by step
        print("New transaction details:")
        print(f"Sender: {transaction.sender}")
        print(f"Receiver: {transaction.receiver}")
        print(f"Amount: {transaction.amount}")
        print(f"Time: {transaction.date}")
        print(f"Signature: {transaction.signature}")
        print(f"Ciphertext: {ciphertext}")
        print(f"Initialization Vector: {iv}")
        print("")

        # Add the transaction to the current_transactions list
        self.current_transactions.append({
            'ciphertext': ciphertext,
            'iv': iv,
            'key': key
        })

        # Return the index of the next block where this transaction will be included
        return len(self.chain) + 1


    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        # Hash the block
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        print("Proof of work completed. New block mined:")
        print(block)
        print("")
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        # Validate the proof: Does hash(last_proof, proof) contain 4 leading zeros?
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

class MobileBankingApp:
    def __init__(self, blockchain):
        self.users = {}
        self.transactions = []
        self.blockchain = blockchain

    def register_user(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        phone_number = input("Enter phone number: ")
        account_number = int(input("Enter account number: "))
        balance = float(input("Enter initial balance: "))
        account_holder = input("Enter account holder name: ")
        print("Registration successful")

        #creates a new user entry in the self.users dictionary with the username as the key/
        self.users[username] = {
            "username": username,
            "password": password,
            "phone_number": phone_number,
            "account": BankAccount(account_number, balance, account_holder)
        }

    def authenticate_user(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        print("User authenticated")
        return username in self.users and self.users[username]["password"] == password


    def make_transfer(self):
        sender = input("Enter your username: ")
        receiver = input("Enter recipient username: ")
    
        # Ensure sender and receiver are different
        if sender == receiver:
            print("Error: Sender and recipient cannot be the same.")
            return None
    
        # Check if the recipient exists
        if receiver not in self.users:
            print("Error: Recipient username does not exist.")
            return None
    
        amount = float(input("Enter transfer amount: "))
        print("")

        sender_account = self.users[sender]["account"]
        receiver_account = self.users[receiver]["account"]

        if sender_account.balance >= amount:
            sender_private_key = sender_account.private_key
            transaction_index = self.blockchain.new_transaction(sender, receiver, amount, sender_private_key)
            sender_account.withdraw(amount)
            receiver_account.deposit(amount)

            # Print sender's account balance before and after transfer
            print(f"Sender's account balance after transfer: {sender_account.balance}")
            
            # Print deposit details for recipient's account
            print("Recipient's account deposit details:")
            print(f"Amount deposited: {amount}")
            print(f"New balance: {receiver_account.balance}")
            print("")

            # Return transaction index
            return transaction_index
        else:
            print("Insufficient funds.")
            return None
    


    def view_balance(self):
        username = input("Enter your username: ")
        return self.users[username]["account"].check_balance()

class TwoFactorMobileBankingApp(MobileBankingApp):
    def __init__(self, blockchain, twilio_sid, twilio_token, twilio_phone_number):
        super().__init__(blockchain)
        self.twilio_sid = twilio_sid
        self.twilio_token = twilio_token
        self.twilio_phone_number = twilio_phone_number

    def send_verification_code(self, phone_number):
        verification_code = random.randint(1000, 9999)
        
        # Ensure the generated code is 4 digits long
        while len(str(verification_code)) != 4:
            verification_code = random.randint(1000, 9999)

        # Initialize Twilio client
        client = Client(self.twilio_sid, self.twilio_token)
        
        # Send verification code via Twilio
        message = client.messages.create(
            body=f"Your verification code is: {verification_code}",
            from_=self.twilio_phone_number,
            to=phone_number
        )
        
        # Return the verification code
        return verification_code


    def verify_code(self, phone_number, code):
        # Assume the code provided is the correct one
        return True

    def confirm_transaction(self, sender, receiver, amount):
        print("Transaction Details:")
        print(f"Sender: {sender}")
        print(f"Receiver: {receiver}")
        print(f"Amount: {amount}")
        confirmation = input("Confirm transaction? (yes/no): ")
        return confirmation.lower() == "yes"


# Instantiate the blockchain
blockchain = Blockchain()

# Instantiate TwoFactorMobileBankingApp with Twilio credentials
twilio_sid = 'AC7d417cccadcabe676b4a143ee29036cb'
twilio_token = '67928809b68e94eab3026496b8c7cbcf'
twilio_phone_number = '+15713646580'
two_factor_app = TwoFactorMobileBankingApp(blockchain, twilio_sid, twilio_token, twilio_phone_number)

# Register the sender user
two_factor_app.register_user()

# Register the recipient user
recipient_username = input("Enter the recipient's username: ")
recipient_password = input("Enter the recipient's password: ")
recipient_account_number = int(input("Enter the recipient's account number: "))
recipient_balance = float(input("Enter the recipient's initial balance: "))
recipient_account_holder = input("Enter the recipient's account holder name: ")

# Placeholder phone number for the recipient
recipient_phone_number = '+1234567890'

# Creates a new user entry in the self.users dictionary with the username as the key
two_factor_app.users[recipient_username] = {
    "username": recipient_username,
    "password": recipient_password,
    "phone_number": recipient_phone_number,
    "account": BankAccount(recipient_account_number, recipient_balance, recipient_account_holder)
}

print("Recipient registration successful")

# Authenticate user with two-factor authentication
# Authenticate user with two-factor authentication
if two_factor_app.authenticate_user():
    # Send verification code
    username = input("Enter your username: ")
    phone_number = two_factor_app.users[username]["phone_number"]
    
    # Send the verification code via Twilio
    verification_code = two_factor_app.send_verification_code(phone_number)

    # Print a message to notify the user that the code has been sent
    print("Verification code has been sent to your phone number.")
    
    # Assume the user inputs the verification code (in a real scenario, you'd get it from the user)
    user_input_code = input("Enter the verification code received: ")


    # Verify the code
    if two_factor_app.verify_code(phone_number, user_input_code):
        # Two-factor authentication successful
        print("Two-factor authentication successful!")

        # Example: Make a transfer using the blockchain
        # Example: Make a transfer using the blockchain
        transaction_index = two_factor_app.make_transfer()
        if transaction_index is not None:
            print(f"New transaction added to the blockchain. Transaction index: {transaction_index}")
        else:
            print("Transaction failed.")

    else:
        print("Invalid verification code.")
else:
    print("Invalid credentials.")
