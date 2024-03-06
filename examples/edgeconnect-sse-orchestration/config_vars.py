config_vars = {
    # Specify name of new service orchestration to add
    "service_name": "NEW HPE ANW SSE",
    # Specify prefix of new service to add for tunnel aliases
    # Minimize to 3-4 characters, maximum of 5 characters in length
    # Must be globally unique across all configured services
    "service_prefix": "SSE",
    # Specify domain IKE identifier, e.g., "sse.customer.lab"
    # Full IKE id would look like "EC-1_INET1@sse.customer.lab"
    "service_ike_id_fqdn": "ssedemo.zachs.lab",
    # Specify primary WAN labels for service, e.g., `["INET1","INET2"]`
    "primary_labels": ["INETA", "INETB", "INETC"],
    # Specify backup WAN labels to use for service, e.g., `["LTE"]`
    # "backup_labels": ["LTE"],
    "backup_labels": ["LTEA"],
    # Specify source interface for ipsla, e.g., interface name `lan0`
    # or interface label `LOOPBACK`
    "ipsla_source": "LOOPBACK",
}
