import json
import os

print("="*50)
print("  RENDER ENVIRONMENT VARIABLE EXTRACTOR")
print("="*50)

try:
    with open("credentials.json", "r") as f:
        creds = f.read()
        print("\n[+] Found credentials.json. Copy this EXACT text into Render as GOOGLE_CREDENTIALS_JSON:")
        print("-" * 50)
        print(creds.strip())
        print("-" * 50)
except FileNotFoundError:
    print("\n[-] credentials.json not found locally.")

try:
    with open("token.json", "r") as f:
        token = f.read()
        print("\n[+] Found token.json. Copy this EXACT text into Render as GOOGLE_TOKEN_JSON:")
        print("-" * 50)
        print(token.strip())
        print("-" * 50)
except FileNotFoundError:
    print("\n[-] token.json not found locally.")
