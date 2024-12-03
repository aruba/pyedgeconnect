import csv
import os
from jinja2 import Environment, FileSystemLoader

# Paths to your files and directories
csv_filename = 'preconfig.csv'
template_filename = 'ec_preconfig_template.jinja2'  # Your Jinja2 template file
output_file_path = 'output.yaml'    # The YAML file to be generated
output_directory = 'output/'          # Directory to save YAML files


# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Load the Jinja2 template
env = Environment(loader=FileSystemLoader('.'), lstrip_blocks=True, trim_blocks=True)
template = env.get_template(template_filename)

# Open the CSV file with configuration data
with open(csv_filename, encoding='utf-8-sig') as csvfile:
    csv_reader = csv.DictReader(csvfile)

    # Read all data rows into a list
    data_rows = list(csv_reader)
    print(f"Total data rows read: {len(data_rows)}")

    # Check if any data rows were read
    if not data_rows:
        print("No data rows found in the CSV file.")
        exit(1)

    # Process each row in the CSV
    for index, row in enumerate(data_rows, start=1):
        print(f"Processing row {index}: {row}")

        # Skip empty rows
        if not any(row.values()):
            print(f"Row {index} is empty. Skipping.")
            continue

        # Render the CSV values through the Jinja2 template
        yaml_content = template.render(data=row)

        # Get the hostname or a unique identifier for the filename
        hostname = row.get('hostname') or f'row_{index}'
        yaml_filename = f'{hostname}_preconfig.yml'

        # Write the rendered YAML content to a file
        output_path = os.path.join(output_directory, yaml_filename)
        with open(output_path, 'w') as yaml_file:
            yaml_file.write(yaml_content)

        print(f"YAML file '{yaml_filename}' has been generated.")

print("All YAML files have been generated.")
