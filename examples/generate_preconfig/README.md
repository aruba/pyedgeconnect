Generate EdgeConnect Preconfig (YAML) from CSV/Excel

This folder contains example workflows to generate Aruba EdgeConnect preconfiguration YAML files using a Jinja2 template and optionally upload them to Orchestrator via the pyedgeconnect SDK.

What you can do here
- Generate YAML preconfig files locally from:
  - CSV: preconfig_from_csv.py
  - Excel: preconfig_from_excel.py (supports selecting a worksheet)
- Upload validated preconfigs to Orchestrator (optionally auto-approve/apply)
- Remove preconfigs from Orchestrator in bulk using a CSV: remove-preconfig.py
- Derive a starter CSV header from the Jinja2 template: templates/generate_csv_from_jinja2.py
- Explore or adapt the included Jinja template: templates/ec_preconfig_template.jinja2

Directory layout
- preconfig_from_csv.py — Generate YAML from CSV; optionally validate/upload.
- preconfig_from_excel.py — Generate YAML from Excel (vertically alligned data); optionally validate/upload.
- remove-preconfig.py — Bulk delete preconfigs from Orchestrator using a CSV (by name/hostname).
- templates/
  - ec_preconfig_template.jinja2 — Jinja2 template for rendering preconfig YAML. Column names referenced as data['...'] map to CSV headers.
  - ec_preconfig_template_advanced.jinja2 - Jinja2 template for rendering preconfig YAML from the advanced Excel preconfig example.
  - generate_csv_from_jinja2.py — Parses the template and produces a CSV with headers matching the template’s expected keys.
  - preconfig.csv — A template/skeleton CSV produced from the Jinja template (if present).
- preconfig.csv — Example input (simple) for CSV workflow. 
- preconfig-advanced.xlsx — Example Excel workbook with more options. Data is vertically alligned.
- preconfig_outputs/ — Generated YAML output files are written here.
- JupyterLab_Notebook/ — Notebook version of the CSV workflow. 

Prerequisites
- Python 3.9+ (tested with modern versions)
- Install dependencies for this example:
  - From this folder, run:
    - pip install -r requirements.txt
  - Or add to your project’s environment:
    - jinja2, openpyxl, pyedgeconnect, and (optional) JupyterLab packages listed in requirements.txt

Authentication and environment variables
These scripts can prompt for credentials interactively, or you can provide values via flags and/or environment variables.
- Orchestrator URL:
  - Preferred: -o https://<orchestrator-host> or set ORCH_URL
- API Key (recommended):
  - Set ORCH_API_KEY
  - If not set, script will prompt; press Enter to skip API key and use username/password instead.
- Username/password (if not using an API key):
  - Set ORCH_USER and ORCH_PASSWORD (optional). If not set, you’ll be prompted.
- MFA: If your user requires MFA, the scripts will ask and prompt for a token.

Notes
- SSL verification is disabled in the sample code (verify_ssl=False). For production, consider enabling certificate verification.
- Upload only occurs when you pass --upload, and after Orchestrator validates your YAML. The scripts always write local YAML files to preconfig_outputs/ regardless of upload.

Jinja2 template mapping
- The template at templates/ec_preconfig_template.jinja2 references CSV headers via the Jinja variable data['header_name'].
- Your input CSV/Excel must include headers that match these keys. Many fields are optional or have defaults in the template.
- You can generate a starter CSV header directly from the template using templates/generate_csv_from_jinja2.py (see below).

Using preconfig_from_csv.py
Purpose: Render YAML preconfigs from a CSV and optionally upload to Orchestrator.

Flags
- -c, --csv <path> (required): Source CSV file with headers matching the template’s data keys.
- -u, --upload (optional flag): If present, validate (and optionally upload) to Orchestrator.
- -aa, --autoapply (optional flag): Mark preconfigs for auto-approve/apply during upload.
- -j, --jinja <filename> (optional): Template filename in templates/ (default: ec_preconfig_template.jinja2).
- -o, --orch <url> (optional): Orchestrator URL. If omitted, ORCH_URL env var or a prompt is used.

Examples (PowerShell)
- Generate local YAMLs only:
  - python preconfig_from_csv.py -c .\preconfig-advanced.csv
- Generate and validate against Orchestrator (no upload):
  - $env:ORCH_URL = "https://orchestrator.example.com"
  - $env:ORCH_API_KEY = "<your-api-key>"
  - python preconfig_from_csv.py -c .\preconfig-advanced.csv --upload
- Generate, validate, and upload with auto-apply:
  - python preconfig_from_csv.py -c .\preconfig-advanced.csv --upload --autoapply
- Use a custom template in templates/:
  - python preconfig_from_csv.py -c .\preconfig-basic.csv -j my_custom_template.jinja2

Input requirements
- CSV must include at least hostname (used as preconfig name and tag) and any other fields your template requires. Optional fields may be omitted or left blank.
- If you include a serial_number column, its value will be passed when creating the preconfig.

Outputs
- YAML files are placed in preconfig_outputs/ with names like <hostname>_preconfig.yml. If validation fails (when --upload is set), a file named <hostname>_preconfig-FAILED.yml is also written for reference.

Using preconfig_from_excel.py
Purpose: Same as the CSV workflow, but reads data from an Excel workbook.

Flags
- -x, --excel <name> (required): Excel workbook to read.
- -s, --sheet <name> (optional): Worksheet to read. If omitted, the active sheet is used. 
- -u, --upload (optional flag): If present, validate (and optionally upload) to Orchestrator.
- -aa, --autoapply (optional flag): Mark preconfigs for auto-approve/apply during upload.
- -j, --jinja <filename> (optional): Template filename in templates/ (default: ec_preconfig_template_advanced.jinja2).
- -o, --orch <url> (optional): Orchestrator URL. If omitted, ORCH_URL env var or a prompt is used.

Examples (PowerShell)
- Generate local YAMLs from active sheet:
  - python preconfig_from_excel.py -x .\preconfig-advanced.xlsx
- Generate from a specific worksheet and upload with auto-apply:
  - python preconfig_from_excel.py -x .\preconfig-advanced.xlsx -s "BranchSites" --upload --autoapply -o https://orchestrator.example.com

Input requirements
- First row must be headers matching the template’s data keys.
- Empty rows are skipped. Cells are trimmed; missing values render as empty strings unless the template provides a default.

Outputs
- Same as CSV workflow: files are written to preconfig_outputs/.

Using remove-preconfig.py
Purpose: Remove preconfigs from Orchestrator that match names listed in a CSV (by hostname column).

Flags
- -c, --csv <path> (required): CSV file containing at least a hostname column. Each row’s hostname is used to match existing preconfigs in Orchestrator by name.
- -o, --orch <url> (optional): Orchestrator URL. If omitted, ORCH_URL env var or a prompt is used.

Behavior
- Authenticates to Orchestrator (API key or username/password).
- Fetches all preconfigs and matches by name against values in the hostname column of your CSV.
- Prompts you with a list of the matching preconfig IDs to delete, and asks for confirmation before deletion.

Examples (PowerShell)
- Delete preconfigs listed in a CSV:
  - $env:ORCH_URL = "https://orchestrator.example.com"
  - $env:ORCH_API_KEY = "<your-api-key>"
  - python remove-preconfig.py -c .\preconfig-advanced.csv

Using templates/generate_csv_from_jinja2.py
Purpose: Create a starter CSV with header columns matching the keys referenced in the Jinja2 template.

Behavior and paths
- Reads templates/ec_preconfig_template.jinja2 by default (TEMPLATE_FILE).
- Writes templates/../preconfig.csv (i.e., a preconfig.csv in this folder) by default (OUTPUT_FILE).

Run (PowerShell)
- cd templates
- python generate_csv_from_jinja2.py
- A preconfig.csv file will be created one folder up with column headers inferred from data['...'] keys in the template.

Tips for customizing the template
- Add or remove sections from templates/ec_preconfig_template.jinja2 to align with your standards.
- Wrap optional sections in Jinja conditionals as demonstrated to render them only when values are present.
- Use default filters (e.g., {{ data['field'] | default("", false) }}) to avoid requiring every field in your CSV/Excel.
- For list inputs, you can store comma-separated values in a single cell and split in the template with .split(','). See the template’s businessIntentOverlays and templateGroups examples.

Troubleshooting
- Validation fails during upload:
  - Inspect the corresponding <hostname>_preconfig-FAILED.yml written to preconfig_outputs/.
  - Ensure your headers match the template keys and values conform to Orchestrator’s expected schema.
- Authentication errors:
  - Verify ORCH_URL and credentials or API key.
  - If using MFA, answer 'y' when prompted and provide a valid token.
- SSL/certificate issues:
  - These examples use verify_ssl=False. For production, configure your environment to verify SSL and update the SDK usage accordingly.
- Excel sheet not found:
  - Use -s to specify an existing worksheet name, or open the workbook and confirm its sheet names.

Appendix: Quick start
1) Install requirements
- cd examples\generate_preconfig
- pip install -r requirements.txt

2) Generate YAML locally from CSV
- python preconfig_from_csv.py -c .\preconfig-advanced.csv

3) Upload to Orchestrator
- $env:ORCH_URL = "https://orchestrator.example.com"
- $env:ORCH_API_KEY = "<your-api-key>"
- python preconfig_from_csv.py -c .\preconfig-advanced.csv --upload --autoapply

4) Remove preconfigs later (careful!)
- python remove-preconfig.py -c .\preconfig-advanced.csv

Where to look next
- JupyterLab_Notebook/Generate_PreConfigs.ipynb for an interactive walkthrough.
- The pyedgeconnect SDK in this repo for additional orchestration capabilities.
