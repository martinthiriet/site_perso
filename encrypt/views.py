import os
import base64
from django.shortcuts import render
from django.http import JsonResponse

# Utility functions
def generate_key(length: int) -> bytes:
    return os.urandom(length)

def encrypt(message: str, key: bytes) -> str:
    message = message.lower()
    message_bytes = message.encode()
    encrypted_bytes = bytes(m ^ k for m, k in zip(message_bytes, key))
    return base64.b32encode(encrypted_bytes).decode().rstrip('=')

def decrypt(encrypted_str: str, key: bytes) -> str:
    padded_encrypted_str = encrypted_str + ('=' * ((8 - len(encrypted_str) % 8) % 8))
    encrypted_bytes = base64.b32decode(padded_encrypted_str)
    decrypted_bytes = bytes(e ^ k for e, k in zip(encrypted_bytes, key))
    return decrypted_bytes.decode().lower()

def home_encrypt(request):
    if request.method == "POST":
        message = request.POST.get("message", "")
        key = request.POST.get("key", "").encode()
        action = request.POST.get("action", "")

        print(message)
        
        if action == "encrypt":
            encrypted_message = encrypt(message, key)
            return render(request, "home_encrypt.html", {'encrypt_key': generate_key(16).hex(),'message':"Encrypted text : "+encrypted_message})
        elif action == "decrypt":
            try:
                decrypted_message = decrypt(message, key)
                return render(request, "home_encrypt.html", {'encrypt_key': generate_key(16).hex(),'message':"Decripted text : "+decrypted_message})
            except :
                return render(request, "home_encrypt.html", {'encrypt_key': generate_key(16).hex(),'message':"Failed to convert text"})
    
    return render(request, "home_encrypt.html", {'encrypt_key': generate_key(16).hex(),'message':""})


def source_code(request):
    return render(request, "source_code.html")