import shutil
import os

def prepare_server_files():
    print("Preparing files for server upload...")
    
    # 1. Create server_env.txt from .env
    if os.path.exists('.env'):
        shutil.copy('.env', 'server_env.txt')
        print("✅ Created 'server_env.txt' from '.env'")
        print("   -> Upload this file to your server")
        print("   -> On server, run: mv server_env.txt .env")
    else:
        print("❌ Error: .env file not found locally!")
        return

    print("\nNext Steps:")
    print("1. Upload 'server_env.txt' to your server folder")
    print("2. Run these commands on your server:")
    print("   mv server_env.txt .env")
    print("   python run.py")

if __name__ == "__main__":
    prepare_server_files()
