import os
import csv
from datetime import datetime
from glob import glob

# --- Configuration ---
DATA_FOLDER = r'C:\Users\GROWTH\Desktop\visitor_counting'
CSV_FILE = os.path.join(DATA_FOLDER, 'data.csv')
HEADERS = ['Date', 'Visitors']
# --- NEW: Define the fixed subtraction value ---
SUBTRACTION_VALUE = 6

# --- Main Logic ---

def consolidate_data():
    """
    Reads daily .txt log files, COUNTS the visitor entries (lines), 
    subtracts a fixed value (6),and  updates the CSV master file.
    """
    
    # 1. Load existing data from the CSV to avoid duplicates
    existing_data = {}
    if os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, mode='r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'Date' in row and 'Visitors' in row and row['Visitors'].isdigit():
                        existing_data[row['Date']] = int(row['Visitors'])
        except Exception as e:
            print(f"Warning: Could not read existing CSV data. Starting fresh. Error: {e}")

    new_entries = 0
    files_to_delete = []

    # 2. Iterate through all .txt files matching the pattern (visitors_YYYYMMDD.txt)
    search_pattern = os.path.join(DATA_FOLDER, 'visitors_*.txt')
    
    for filepath in glob(search_pattern):
        try {
            filename = os.path.basename(filepath) 
            
            # --- Date Parsing ---
            base_name = filename.replace('visitors_', '').replace('.txt', '')
            
            if len(base_name) == 8:
                year = base_name[:4]
                month = base_name[4:6]
                day = base_name[6:8]
                date_str = f"{year}-{month}-{day}"
            else:
                raise ValueError("Filename format incorrect (Expected YYYYMMDD in base name).")

            datetime.strptime(date_str, '%Y-%m-%d') 
            
            # --- Count Extraction and Calculation ---
            if date_str not in existing_data:
                raw_count = 0
                
                # Open the log file and count the lines
                with open(filepath, 'r') as f:
                    for line in f:
                        if line.strip(): 
                             raw_count += 1
                
                # Apply the requested calculation: Total Visitors = Raw Count - 6
                # Ensure the final count is not negative
                final_count = max(0, raw_count - SUBTRACTION_VALUE)
                
                existing_data[date_str] = final_count
                new_entries += 1
                files_to_delete.append(filepath)
                print(f"Processed file: {date_str}. Raw Count: {raw_count}, Final Count: {final_count}")

        except ValueError as ve:
            print(f"Skipping file: {filename}. Error: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred processing {filename}: {e}")


    # 3. Write all (old and new) data back to the CSV, sorted by date
    if new_entries > 0:
        sorted_data = sorted(existing_data.items())
        
        with open(CSV_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)
            writer.writerows(sorted_data)
            
        print(f"Consolidation complete. {new_entries} new entries added to {CSV_FILE}.")
        


if __name__ == "__main__":
    consolidate_data()