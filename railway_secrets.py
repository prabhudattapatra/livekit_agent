import os
import json

def write_secret(env_var_name, filename):
    secret_data = os.environ.get(env_var_name)
    if secret_data:
        try:
            # Verify it's valid JSON before writing
            parsed = json.loads(secret_data)
            with open(filename, 'w') as f:
                json.dump(parsed, f, indent=2)
            print(f"✅ Successfully wrote {filename} from environment variable.")
        except json.JSONDecodeError:
            print(f"❌ Error: {env_var_name} is not valid JSON!")
    else:
        print(f"⚠️ {env_var_name} not found in environment. Skipping {filename}.")

if __name__ == "__main__":
    print("Running Railway Secrets Initialization...")
    write_secret("GOOGLE_CREDENTIALS_JSON", "credentials.json")
    write_secret("GOOGLE_TOKEN_JSON", "token.json")
