import os
import csv
from datetime import datetime
from glob import glob

# --- Configuration (Folder Path Confirmed) ---
DATA_FOLDER = r'C:\Users\GROWTH\Desktop\visitor_counting'
CSV_FILE = os.path.join(DATA_FOLDER, 'data.csv')
HEADERS = ['Date', 'Visitors']

# --- Main Logic ---

def consolidate_data():
    """
    Reads daily .txt log files (visitors_YYYYMMDD.txt), COUNTS the visitor entries,
    updates the CSV master file, and removes processed .txt files.
    """

    # 1. Load existing data from the CSV to avoid duplicates
    existing_data = {}
    if os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, mode='r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Ensure data and count are valid before adding
                    if 'Date' in row and 'Visitors' in row and row['Visitors'].isdigit():
                        existing_data[row['Date']] = int(row['Visitors'])
        except Exception as e:
            print(f"Warning: Could not read existing CSV data. Starting fresh. Error: {e}")

    new_entries = 0
    files_to_delete = []

    # 2. Iterate through all .txt files matching the pattern (visitors_YYYYMMDD.txt)
    search_pattern = os.path.join(DATA_FOLDER, 'visitors_*.txt')

    for filepath in glob(search_pattern):
        try:
            filename = os.path.basename(filepath)

            # --- Date Parsing ---
            # Extracts date part: 20251128
            base_name = filename.replace('visitors_', '').replace('.txt', '')

            # Reformat from YYYYMMDD to YYYY-MM-DD for CSV
            if len(base_name) == 8:
                year = base_name[:4]
                month = base_name[4:6]
                day = base_name[6:8]
                date_str = f"{year}-{month}-{day}"
            else:
                raise ValueError("Filename format incorrect (Expected YYYYMMDD in base name).")

            # Validate date format
            datetime.strptime(date_str, '%Y-%m-%d')

            # --- Count Extraction (The Fix) ---
            if date_str not in existing_data:
                visitor_count = 0

                # Open the log file and count the lines
                with open(filepath, 'r') as f:
                    for line in f:
                        # Assuming every line is a visitor log, or count non-empty lines
                        if line.strip():
                             visitor_count += 1

                # Use the line count as the daily total
                existing_data[date_str] = visitor_count
                new_entries += 1
                files_to_delete.append(filepath)
                print(f"Added new entry: Date={date_str}, Count={visitor_count}")

        except ValueError as ve:
            print(f"Skipping file: {filename}. Error: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred processing {filename}: {e}")


    # 3. Write all (old and new) data back to the CSV, sorted by date
    if new_entries > 0:
        # Sort by date string (which naturally sorts chronologically)
        sorted_data = sorted(existing_data.items())

        with open(CSV_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)
            # writerows expects an iterable of rows, which is what sorted_data provides (Date, Count)
            writer.writerows(sorted_data)

        print(f"Consolidation complete. {new_entries} new entries added to {CSV_FILE}.")

        # 4. Remove processed TXT files
        for filepath in files_to_delete:
            os.remove(filepath)
            print(f"Deleted processed file: {os.path.basename(filepath)}")
    else:
        print("No new data to consolidate.")


if __name__ == "__main__":
    consolidate_data()