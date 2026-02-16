import fitz
import os
import sqlite3

def inspect_latest_pdf():
    db_path = "database.db"
    if not os.path.exists(db_path):
        print("Database not found.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT filename, file_path FROM document ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    for filename, file_path in rows:
        print(f"\n--- Checking {filename} at {file_path} ---")
        if not os.path.exists(file_path):
            # Try fixing path if moved
            base = os.path.basename(file_path)
            alt_path = os.path.join("uploads", base)
            if os.path.exists(alt_path):
                file_path = alt_path
            else:
                print(f"File not found on disk.")
                continue
                
        doc = fitz.open(file_path)
        for i in range(min(5, len(doc))):
            print(f"\n--- Page {i+1} ---")
            print(doc[i].get_text())
        doc.close()

if __name__ == "__main__":
    inspect_latest_pdf()
