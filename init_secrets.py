import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_secrets")

def write_secret(env_var_name: str, file_name: str):
    secret_content = os.getenv(env_var_name)
    if secret_content:
        try:
            # Parse it to ensure it's valid JSON, then write it
            data = json.loads(secret_content)
            with open(file_name, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Successfully generated {file_name} from environment variable {env_var_name}")
        except json.JSONDecodeError:
            logger.error(f"Error: {env_var_name} is not valid JSON!")
        except Exception as e:
            logger.error(f"Error writing {file_name}: {e}")
    else:
        logger.warning(f"No {env_var_name} found in environment variables. Assuming {file_name} already exists or is not needed.")

if __name__ == "__main__":
    write_secret("GOOGLE_CRED_JSON", "credentials.json")
    write_secret("GOOGLE_TOKEN_JSON", "token.json")
