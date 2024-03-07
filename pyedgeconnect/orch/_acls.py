# MIT License
# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
#
# acls : ECOS ACLs (access control lists)


def get_appliance_acls(
    self,
    ne_id: str,
    cached: bool,
) -> dict:
    """Get Access list settings configurations from appliance

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - acls
          - GET
          - /acls/{neId}?cached={cached}

    :return: Returns dictionary where each key is name of an ACL, each
        value is an object of the ACL's settings. Each ACL's settings
        contains "entry" and "rmap". "rmap" give info about the
        routemap which uses this ACL.
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/acls?nePk={ne_id}&cached={cached}"
    else:
        path = f"/acls/{ne_id}?cached={cached}"

    return self._get(path)
