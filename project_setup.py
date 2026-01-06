import os

folders = [
    'app/models', 'app/static', 'app/templates', 'app/utils', 'app/views',
    'migrations', 'tests'
]

files = [
    'app/__init__.py', 'app/models/__init__.py', 'app/views/__init__.py',
    'config.py', 'run.py', '.env', '.gitignore', 'requirements.txt'
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

for file in files:
    with open(file, 'a'):
        os.utime(file, None)

print("Project structure created successfully!")