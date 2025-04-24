"""
Database cleanup utility - removes all stored data
Run this script to clear all users and expenses data
"""
import os

# File paths from models.py
USERS_FILE = "users_data.pkl"
EXPENSES_FILE = "expenses_data.pkl"
COUNTER_FILE = "counters_data.pkl"


def cleanup_database():
    """Remove all database files"""
    files_to_remove = [USERS_FILE, EXPENSES_FILE, COUNTER_FILE]

    for file in files_to_remove:
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f"Removed {file}")
            else:
                print(f"{file} does not exist")
        except Exception as e:
            print(f"Error removing {file}: {e}")

    print("\nDatabase cleanup completed!")


if __name__ == "__main__":
    confirm = input("This will remove all users and expenses data. Are you sure? (y/N): ")
    if confirm.lower() == 'y':
        cleanup_database()
    else:
        print("Operation cancelled")
