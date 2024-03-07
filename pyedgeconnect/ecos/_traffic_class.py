# MIT License
# (C) Copyright 2023 Hewlett Packard Enterprise Development LP.
#
# trafficClass : Traffic Class Names


def get_traffic_class_names(
    self,
) -> dict:
    """Get the traffic class names from appliance

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - trafficClass
          - GET
          - /trafficclass

    :return: Returns dictionary of current appliance traffic class id
        and name mapping \n
        * keyword **1** (`dict`): Traffic class 1 \n
            * keyword **name** (`str`): The name of the traffic class 1
        * keyword **2** (`dict`): Traffic class 2 \n
            * keyword **name** (`str`): The name of the traffic class 2
        * keyword **3** (`dict`): Traffic class 3 \n
            * keyword **name** (`str`): The name of the traffic class 3
        * keyword **4** (`dict`): Traffic class 4 \n
            * keyword **name** (`str`): The name of the traffic class 4
        * keyword **5** (`dict`): Traffic class 5 \n
            * keyword **name** (`str`): The name of the traffic class 5
        * keyword **6** (`dict`): Traffic class 6 \n
            * keyword **name** (`str`): The name of the traffic class 6
        * keyword **7** (`dict`): Traffic class 7 \n
            * keyword **name** (`str`): The name of the traffic class 7
        * keyword **8** (`dict`): Traffic class 8 \n
            * keyword **name** (`str`): The name of the traffic class 8
        * keyword **9** (`dict`): Traffic class 9 \n
            * keyword **name** (`str`): The name of the traffic class 9
        * keyword **10** (`dict`): Traffic class 10 \n
            * keyword **name** (`str`): The name of the traffic class 10
    :rtype: dict
    """
    return self._get("/trafficclass")


def set_traffic_class_names(
    self,
    traffic_class_names: dict,
) -> bool:
    """Modify the traffic class names on appliance

    Example:

    .. warning::

        This will overwrite current names on all traffic classes on
        appliance.
        Use :func:`~pyedgeconnect.EdgeConnect.get_traffic_class_names`
        to get current configuration first and modify if only wanting
        to update one or more traffic class names.


    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - trafficClass
          - POST
          - /trafficclass

    :param traffic_class_names: Nested dictionary of all 10 traffic
        classes and the friendly name assigned \n
        * keyword **1** (`dict`): Traffic class 1 \n
            * keyword **name** (`str`): The name of the traffic class 1
        * keyword **2** (`dict`): Traffic class 2 \n
            * keyword **name** (`str`): The name of the traffic class 2
        * keyword **3** (`dict`): Traffic class 3 \n
            * keyword **name** (`str`): The name of the traffic class 3
        * keyword **4** (`dict`): Traffic class 4 \n
            * keyword **name** (`str`): The name of the traffic class 4
        * keyword **5** (`dict`): Traffic class 5 \n
            * keyword **name** (`str`): The name of the traffic class 5
        * keyword **6** (`dict`): Traffic class 6 \n
            * keyword **name** (`str`): The name of the traffic class 6
        * keyword **7** (`dict`): Traffic class 7 \n
            * keyword **name** (`str`): The name of the traffic class 7
        * keyword **8** (`dict`): Traffic class 8 \n
            * keyword **name** (`str`): The name of the traffic class 8
        * keyword **9** (`dict`): Traffic class 9 \n
            * keyword **name** (`str`): The name of the traffic class 9
        * keyword **10** (`dict`): Traffic class 10 \n
            * keyword **name** (`str`): The name of the traffic class 10
    :type traffic_class_names: dict
    :return: Returns True/False based on successful call
    :rtype: bool
    """
    return self._post(
        "/trafficclass",
        data=traffic_class_names,
        return_type="bool",
    )
