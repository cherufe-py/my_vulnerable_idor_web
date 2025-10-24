import sqlite3
import os
import shutil
from uuid import uuid4
import random
from faker import Faker

APP_DB = 'example.db'
UPLOAD_FOLDER = 'uploads'

fake = Faker()


def generate_random_content():
    num_paragraphs = random.randint(2, 4)
    paragraphs = []

    for _ in range(num_paragraphs):
        paragraphs.append(fake.paragraph(nb_sentences=random.randint(2, 5)))

    return '\n\n'.join(paragraphs)


def create_sample_files():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    file_data = {}

    for i in range(50):
        filename = f"file_{i + 1:02d}.txt"
        unique_filename = f"{uuid4().hex}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        content = generate_random_content()

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        file_data[unique_filename] = {
            'original_name': filename,
            'content': content
        }

    print(f"✓ Created {len(file_data)} sample files directly in {UPLOAD_FOLDER}/")
    return file_data


def add_files_to_database():
    db = sqlite3.connect(APP_DB)
    cur = db.cursor()

    additional_users = [
        ('charlie', 'charliepass'),
        ('diana', 'dianapass'),
        ('eve', 'evepass')
    ]

    for username, password in additional_users:
        try:
            cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        except sqlite3.IntegrityError:
            pass

    db.commit()

    cur.execute('SELECT id, username FROM users ORDER BY id')
    users = cur.fetchall()
    print(f"Available users: {[user[1] for user in users]}")

    upload_files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]

    file_assignments = []
    file_counter = 0

    for user_id, username in users:
        for i in range(10):
            if file_counter < len(upload_files):
                filename = upload_files[file_counter]
                display_name = f"Doc_{username}_{i + 1:02d}.txt"
                file_assignments.append((user_id, display_name, filename))
                file_counter += 1

    files_added = 0
    for user_id, display_name, filename in file_assignments:
        cur.execute(
            'INSERT INTO files (name, filename, content_type, user_id) VALUES (?, ?, ?, ?)',
            (display_name, filename, 'text/plain', user_id)
        )
        files_added += 1

    db.commit()

    cur.execute('SELECT COUNT(*) FROM files')
    file_count = cur.fetchone()[0]

    cur.execute('''
        SELECT u.username, COUNT(f.id) as file_count 
        FROM users u 
        LEFT JOIN files f ON u.id = f.user_id 
        GROUP BY u.id
    ''')
    user_files = cur.fetchall()

    db.close()

    print(f"Database Summary")
    print(f"Total files: {file_count}")
    for username, count in user_files:
        print(f"User {username}: {count} files")


def main():
    print("🚀 Creating sample files with Faker paragraphs in uploads folder...")

    create_sample_files()
    add_files_to_database()

    print("Sample files setup completed successfully!")
    print(f"All files are in the '{UPLOAD_FOLDER}' folder")


if __name__ == '__main__':
    main()