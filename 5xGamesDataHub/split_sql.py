import os
import re

SOURCE_FILE = r"c:\Users\Shawn\Desktop\CodeLibrary\5xGamesDataHub\Maxcomputer_SlamDunk_SQL_Library.sql"
OUTPUT_DIR = r"c:\Users\Shawn\Desktop\CodeLibrary\5xGamesDataHub\app\sql_templates\slamdunk"

def split_sqls():
    if not os.path.exists(SOURCE_FILE):
        print("Source file not found")
        return

    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_filename = None
    current_content = []

    for line in lines:
        line_stripped = line.strip()
        
        # Check for start of a new section
        # Format: -- 1. Title (filename)
        # Regex to capture the Title and the last (key)
        # We look for: -- Number. [Title stuff] (Key)
        match = re.search(r'-- \d+\.\s+(.*)\s+\(([^()]+)\)\s*$', line_stripped)
        
        if match:
            # Save previous file
            if current_filename and current_content:
                save_file(current_filename, current_content)
            
            # Start new capture
            current_filename = match.group(2).strip()
            current_content = [line] # Keep the header line for metadata parsing later
        
        elif current_filename:
            current_content.append(line)
            
    # Save last file
    if current_filename and current_content:
        save_file(current_filename, current_content)

def save_file(filename, lines):
    # Ensure legal filename
    filename = re.sub(r'[^\w\-]', '_', filename) + ".sql"
    path = os.path.join(OUTPUT_DIR, filename)
    
    content = "".join(lines).strip()
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {filename}")

if __name__ == "__main__":
    split_sqls()
