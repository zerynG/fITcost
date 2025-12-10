#!/usr/bin/env python3
import os
import tarfile
import datetime
from pathlib import Path


def create_backup():
    # Исключаемые директории и файлы
    EXCLUDE = [
        '__pycache__',
        '.git',
        '.venv',
        'venv',
        'env',
        'media',
        'staticfiles',
        'db.sqlite3',
        '*.pyc',
        '.DS_Store'
    ]

    # Имя архива с timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_name = f'project_backup_{timestamp}.tar.gz'

    # Получаем текущую директорию
    project_root = Path.cwd()

    # Создаем архив
    with tarfile.open(archive_name, 'w:gz') as tar:
        for item in project_root.iterdir():
            # Проверяем исключения
            if any(exclude in str(item) for exclude in EXCLUDE):
                print(f"Пропускаем: {item}")
                continue

            if item.name.startswith('.'):
                continue

            print(f"Добавляем: {item}")
            tar.add(item, arcname=item.name, recursive=False)

    print(f"Архив создан: {archive_name}")
    return archive_name


if __name__ == "__main__":
    create_backup()