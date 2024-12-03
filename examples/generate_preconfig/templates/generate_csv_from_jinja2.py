import re
import csv
from pathlib import Path

# File paths
TEMPLATE_FILE = "ec_preconfig_template.jinja2"
OUTPUT_FILE = "../preconfig.csv"

# Regex pattern to extract keys from data[...] references
DATA_PATTERN = re.compile(r"data\[(?:'([^']*)'|\"([^\"]*)\")\]")

def extract_keys(file_path):
    """
    Reads the template file and extracts unique keys from data[...] references.
    """
    with open(file_path, "r") as file:
        content = file.read()
    
    matches = DATA_PATTERN.findall(content)
    # Extract the first non-empty group from each match, remove duplicates while keeping order
    return list(dict.fromkeys(match[0] or match[1] for match in matches))

def write_to_csv(keys, output_file):
    """
    Writes the extracted keys to a CSV file as column headers.
    """
    with open(output_file, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(keys)

if __name__ == "__main__":
    # Extract keys and write them to the CSV
    keys = extract_keys(TEMPLATE_FILE)
    
    if keys:
        write_to_csv(keys, OUTPUT_FILE)
        print(f"CSV file successfully created: {OUTPUT_FILE}")
    else:
        print("No keys found in the Jinja2 template.")