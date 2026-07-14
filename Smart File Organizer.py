import os
import shutil
import hashlib
import json
from datetime import datetime

history_file = "organizer_history.json"

categories = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"],
    "Audio": [".mp3", ".wav", ".flac"],
    "Archives": [".zip", ".rar", ".7z", ".tar"],
    "Programs": [".exe", ".msi", ".apk"],
    "Code": [".py", ".c", ".cpp", ".java", ".js", ".html", ".css"]
}

history = []

def save_history():
    with open(history_file, "w") as f:
        json.dump(history, f, indent=4)

def load_history():
    global history
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)

def get_category(file):
    ext = os.path.splitext(file)[1].lower()
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    return "Others"

def organize(path):
    global history
    if not os.path.exists(path):
        print("Invalid path")
        return

    for file in os.listdir(path):
        full = os.path.join(path, file)

        if os.path.isfile(full):
            category = get_category(file)
            folder = os.path.join(path, category)

            if not os.path.exists(folder):
                os.makedirs(folder)

            destination = os.path.join(folder, file)

            if os.path.exists(destination):
                name, ext = os.path.splitext(file)
                destination = os.path.join(folder, name + "_" + datetime.now().strftime("%H%M%S") + ext)

            shutil.move(full, destination)

            history.append({
                "old": full,
                "new": destination
            })

    save_history()
    print("Organization completed")

def undo():
    global history

    if not history:
        print("Nothing to undo")
        return

    for item in reversed(history):
        if os.path.exists(item["new"]):
            shutil.move(item["new"], item["old"])

    history = []
    save_history()
    print("Undo completed")

def hash_file(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        while chunk := f.read(4096):
            h.update(chunk)

    return h.hexdigest()

def find_duplicates(path):
    hashes = {}
    duplicates = []

    for root, dirs, files in os.walk(path):
        for file in files:
            try:
                full = os.path.join(root, file)
                file_hash = hash_file(full)

                if file_hash in hashes:
                    duplicates.append((full, hashes[file_hash]))
                else:
                    hashes[file_hash] = full

            except:
                pass

    if duplicates:
        print("\nDuplicate Files:")
        for a, b in duplicates:
            print(a)
            print(b)
            print("-" * 30)
    else:
        print("No duplicates found")

def statistics(path):
    count = 0
    size = 0
    types = {}

    for root, dirs, files in os.walk(path):
        for file in files:
            try:
                full = os.path.join(root, file)
                count += 1
                size += os.path.getsize(full)

                ext = os.path.splitext(file)[1].lower()
                types[ext] = types.get(ext, 0) + 1

            except:
                pass

    print("\nStatistics")
    print("Files:", count)
    print("Size:", round(size / 1024 / 1024, 2), "MB")

    for t, c in types.items():
        print(t if t else "No Extension", ":", c)

def menu():
    load_history()

    while True:
        print("""
==============================
     SMART FILE ORGANIZER
==============================

1. Organize Files
2. Find Duplicate Files
3. Show Statistics
4. Undo Organization
5. Exit
""")

        choice = input("Choice: ")

        if choice == "1":
            organize(input("Folder path: "))

        elif choice == "2":
            find_duplicates(input("Folder path: "))

        elif choice == "3":
            statistics(input("Folder path: "))

        elif choice == "4":
            undo()

        elif choice == "5":
            break

        else:
            print("Invalid choice")

menu()
