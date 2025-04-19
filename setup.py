import os
import subprocess
import sys
import time
import platform


def run(command, cwd=None):
    print(f"▶ Running: {command}")
    result = subprocess.run(["bash", "-c", command], cwd=cwd)
    if result.returncode != 0:
        print("Command failed.")
        sys.exit(1)

def create_venv():
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        run("python3 -m venv venv")
    else:
        print("Virtual environment already exists.")

def activate_venv():
    if os.name == "nt":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_requirements():
    print("Installing dependencies...")
    run(f"{activate_venv()} && pip install --upgrade pip", cwd=".")
    run(f"{activate_venv()} && pip install -r requirements.txt", cwd=".")

def run_migrations():
    print("Applying migrations...")
    run(f"{activate_venv()} && python manage.py migrate", cwd=".")

def collect_static():
    print("Collecting static files...")
    run(f"{activate_venv()} && python manage.py collectstatic --noinput", cwd=".")

def start_redis():
    if platform.system().lower() == "windows":
        print("You're on Windows. Please ensure Redis is running manually (e.g., Redis installed via MSI or running as a service).")
    else:
        print("Starting Redis server (if installed)...")
        run("sudo service redis-server start || echo 'Redis not found or already running.'")

    print("Deleting 'top_districts' key if exists...")
    command = (
        f"{activate_venv()} && "
        f"python manage.py shell -c "
        f"\"from django.core.cache import cache; cache.delete('top_districts'); print('Deleted')\""
    )
    run(command)

def prefill_top_districts():
    print("Fetching top districts and storing in cache...")
    command = (
        f"{activate_venv()} && "
        f"python manage.py shell -c "
        f"\"from travel.utils import calculate_top_districts;"
        f"from django.core.cache import cache;"
        f"import json;"
        f"cache.set('top_districts', json.dumps(calculate_top_districts()), timeout=7200)\""
    )
    run(command)

def start_celery():
    print("Starting Celery worker and beat...")
    run(f"{activate_venv()} && celery -A core worker --loglevel=info &", cwd=".")
    time.sleep(2)
    run(f"{activate_venv()} && celery -A core beat --loglevel=info &", cwd=".")
    time.sleep(2)

def start_django():
    print("Starting Django server...")
    run(f"{activate_venv()} && python manage.py runserver", cwd=".")

def main():
    create_venv()
    install_requirements()
    run_migrations()
    collect_static()
    start_redis()
    prefill_top_districts()
    start_celery()
    start_django()

if __name__ == "__main__":
    main()
