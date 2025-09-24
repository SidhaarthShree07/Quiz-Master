import os
import subprocess

# Create venv
def create_venv():
    if not os.path.exists('backend/venv'):
        subprocess.run(['python', '-m', 'venv', 'backend/venv'])
        print('Virtual environment created.')
    else:
        print('Virtual environment already exists.')

# Install requirements
def install_requirements():
    pip_path = os.path.join('backend', 'venv', 'Scripts', 'pip.exe')
    req_path = os.path.join('backend', 'requirements.txt')
    subprocess.run([pip_path, 'install', '-r', req_path])
    print('Requirements installed.')

def print_run_instructions():
    print("\n--- Project Run Instructions (Open 5 Terminals) ---\n")
    print("Terminal 1: Start Redis")
    print("  redis-server\n")
    print("Terminal 2: Start Flask Backend")
    print("  cd backend")
    print("  .\\venv\\Scripts\\Activate.ps1")
    print('  $env:FLASK_APP="main.py"; $env:FLASK_ENV="development"; flask run\n')
    print("Terminal 3: Start Frontend")
    print("  cd frontend")
    print("  # If you deleted node_modules, run this first:")
    print("  npm install")
    print("  npm run dev\n")
    print("Terminal 4: Start Celery Worker")
    print("  cd backend")
    print("  .\\venv\\Scripts\\Activate.ps1")
    print("  python -m celery -A celery_worker.celery worker --loglevel=info --pool=solo\n")
    print("Terminal 5: Start Celery Beat")
    print("  cd backend")
    print("  .\\venv\\Scripts\\Activate.ps1")
    print("  celery -A celery_worker.celery beat --loglevel=info\n")

if __name__ == '__main__':
    create_venv()
    install_requirements()
    print_run_instructions()
