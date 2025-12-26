import os, datetime, subprocess
from pathlib import Path
import yadisk

BASE_DIR = Path(__file__).resolve().parent
BACKUP_DIR = BASE_DIR / 'backups'
BACKUP_DIR.mkdir(exist_ok=True)

DB_NAME = 'store'
DB_USER = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_PASSWORD = 'quasexort13'

YANDEX_TOKEN = "y0__xDFvomZBxj2wTwgusy04xVUxtgL4E6rzYhwUYGX77JxfHIrUw"  
YANDEX_DIR = "/backups"  

def create_local_backup():
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = BACKUP_DIR / f'{DB_NAME}_backup_{ts}.sql'
    cmd = [
        'pg_dump',
        f'-h{DB_HOST}',
        f'-p{DB_PORT}',
        f'-U{DB_USER}',
        DB_NAME,
    ]
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_PASSWORD
    with open(filename, 'w', encoding='utf-8') as f:
        subprocess.check_call(cmd, stdout=f, env=env)
    return filename

def upload_to_remote(path):
    y = yadisk.YaDisk(token=YANDEX_TOKEN)

    if not y.exists(YANDEX_DIR):
        y.mkdir(YANDEX_DIR)

    remote_path = f"{YANDEX_DIR}/{path.name}"
    with open(path, "rb") as f:
        y.upload(f, remote_path, overwrite=True)

if __name__ == "__main__":
    backup_file = create_local_backup()
    upload_to_remote(backup_file)
    print("Backup created and uploaded:", backup_file)