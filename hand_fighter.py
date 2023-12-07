import subprocess
import sys

def run_login():
    subprocess.run([sys.executable, 'src/login_interface.py'])

if __name__ == "__main__":
    run_login()