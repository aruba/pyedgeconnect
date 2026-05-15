# import sys
import os
from jinja2 import Environment, FileSystemLoader

def generate_preconfig_yaml(data, preconfig_section_name, ec_template_file, device_name) -> str:
    """

        The `generate_preconfig_yaml` function creates a YAML configuration file for an EdgeConnect device.

        It uses a Jinja2 template (`ec_template_file`) along with various inputs like device details, deployment info,
        tunnel settings, DHCP configuration, and high availability settings to generate the YAML content.

        The function ensures the output is saved to the `preconfig_outputs/` directory and returns the generated YAML
        file's content as a string.

    """

    env = Environment(
        loader=FileSystemLoader("templates"),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    ec_template = env.get_template(ec_template_file)
    # Local directory for configuration outputs
    output_directory = "preconfig_outputs/"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    yaml_preconfig = _write_local_yaml_file(data, preconfig_section_name, device_name, ec_template, output_directory)

    return yaml_preconfig


def _write_local_yaml_file(data, preconfig_section_name, device_name, ec_template, output_directory):
    """

    The `write_local_yaml_file` function generates a YAML file for an EdgeConnect device using a Jinja2 template
    (`ec_template`) and the provided configuration details.

    The generated YAML is saved in the specified `output_directory` with a filename based on the device name, and the
    YAML content is also returned as a string.

    """

    yaml_filename = f"{device_name}_{preconfig_section_name}-AUTOMATED_PRECONFIG.yml"
    yaml_preconfig = ec_template.render(
        data=data,
    )
    with open(output_directory + yaml_filename, "w") as preconfig_file:
        write_data = preconfig_file.write(yaml_preconfig)
    return yaml_preconfig

def validate_preconfig(orch, preconfig_yaml) -> bool:
    """
    Checks if a given YAML preconfiguration (preconfig_yaml) is valid by using the
    (orch) object's validate_preconfig method.

    Args:
        orch: The orchestrator object with validate_preconfig method
        preconfig_yaml: The YAML configuration to validate

    Returns:
        bool: True if the validation is successful (HTTP status code 200), False otherwise
    """

    validity_check = orch.validate_preconfig(preconfig_name="temp", yaml_preconfig=preconfig_yaml, auto_apply=False)
    if validity_check.status_code == 200:
        return True
    else:
        print("Preconfig is NOT valid. Please look at error response for details.")
        return False
