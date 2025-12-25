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
    # Extend key if message is longer than key
    extended_key = (key * ((len(message_bytes) // len(key)) + 1))[:len(message_bytes)]
    encrypted_bytes = bytes(m ^ k for m, k in zip(message_bytes, extended_key))
    return base64.b32encode(encrypted_bytes).decode().rstrip('=')

def decrypt(encrypted_str: str, key: bytes) -> str:
    padded_encrypted_str = encrypted_str + ('=' * ((8 - len(encrypted_str) % 8) % 8))
    encrypted_bytes = base64.b32decode(padded_encrypted_str)
    # Extend key if encrypted message is longer than key
    extended_key = (key * ((len(encrypted_bytes) // len(key)) + 1))[:len(encrypted_bytes)]
    decrypted_bytes = bytes(e ^ k for e, k in zip(encrypted_bytes, extended_key))
    return decrypted_bytes.decode().lower()

def home_encrypt(request):
    if request.method == "POST":
        message = request.POST.get("message", "")
        key = request.POST.get("key", "").encode()
        action = request.POST.get("action", "")
        
        if action == "encrypt":
            # Split message by newlines
            lines = message.split('\n')
            encrypted_lines = []
            
            for line in lines:
                stripped_line = line.strip()  # Remove leading/trailing whitespace
                if stripped_line:  # Only encrypt non-empty lines
                    encrypted_line = encrypt(stripped_line, key)
                    encrypted_lines.append(encrypted_line)
                else:
                    encrypted_lines.append("")  # Keep empty lines
            
            result = '\n'.join(encrypted_lines)
            return render(request, "home_encrypt.html", {
                'encrypt_key': generate_key(16).hex(),
                'message': "Encrypted text:\n" + result
            })
            
        elif action == "decrypt":
            try:
                # Split message by newlines
                lines = message.split('\n')
                decrypted_lines = []
                
                for line in lines:
                    stripped_line = line.strip()  # Remove leading/trailing whitespace
                    if stripped_line:  # Only decrypt non-empty lines
                        decrypted_line = decrypt(stripped_line, key)
                        decrypted_lines.append(decrypted_line)
                    else:
                        decrypted_lines.append("")  # Keep empty lines
                
                result = '\n'.join(decrypted_lines)
                return render(request, "home_encrypt.html", {
                    'encrypt_key': generate_key(16).hex(),
                    'message': "Decrypted text:\n" + result
                })
            except Exception as e:
                return render(request, "home_encrypt.html", {
                    'encrypt_key': generate_key(16).hex(),
                    'message': f"Failed to convert text: {str(e)}"
                })
    
    return render(request, "home_encrypt.html", {
        'encrypt_key': generate_key(16).hex(),
        'message': ""
    })

def source_code(request):
    return render(request, "source_code.html")
