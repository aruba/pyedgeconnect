# tests/test_cluster.py

import pytest
import sys
import os
from pyedgeconnect import Orchestrator
from dotenv import load_dotenv
load_dotenv()

profile_id = None
all_cluster_profiles = None

#Change these variables in accordance with the lab environment you are testing in
site_name_in_lab_with_cluster = "Frisco"
cluster_name_assigned_to_lab_test_site = "ClusterProfileFrisco"
device_ids_in_edge_ha_cluster = ["0.NE", "1.NE"]


# Get env variables. If they do not exist, exit program.
try:
    orch_url = os.getenv('ORCH_URL')
    orch_api_key = os.getenv('ORCH_API_KEY')

    if not all([orch_url, orch_api_key]):
        raise ValueError(
            "One or more required environment variables are not set.")
except ValueError as e:
    print(f"Error: {e}")
    sys.exit(1)

orch = Orchestrator(orch_url, api_key=orch_api_key, verify_ssl=False)
print(orch.orch_version)


@pytest.fixture(scope="module", autouse=True)
def check_orch_version():
    version = orch.orch_version
    version = orch.orch_version
    if orch.orch_version < 9.5:
        pytest.skip("Skipping tests for Orchestrator versions < 9.5.0")
    else:
        print(f"Orchestrator version satisfies requirements for this module: {version}")
        yield


def test_get_cluster_state():
    try:
        result = orch.get_cluster_state(site_name_in_lab_with_cluster, False)
        assert isinstance(result, dict)  # Example: Assert it returns a dictionary
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")


def test_get_cluster_alarm_count():
    try:
        result = orch.get_cluster_alarm_count()
        assert isinstance(result, dict)
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")


def test_get_all_cluster_profiles():
    try:
        result = orch.get_all_cluster_profiles()
        assert isinstance(result, list)
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")


@pytest.fixture
def setup_test_add_cluster_profile():
    # determine if test cluster profiles exist; if so, delete them before trying to add
    global profile_id
    profiles = orch.get_all_cluster_profiles()
    for profile in profiles:
        if (profile['name'] == 'ClusterProfileTest100' or
                profile['name'] == 'ClusterProfileTest101' or
                profile['name'] == 'ClusterProfileTest102' or
                profile['name'] == 'ClusterProfileTest103'):
            profile_id = profile['id']
            # delete_cluster_profile is tested further down - if that fails, this will fail
            delete = orch.delete_cluster_profile(profile_id)
            assert delete == True
    yield


@pytest.mark.usefixtures("setup_test_add_cluster_profile")
def test_add_cluster_profile():
    new_test_cluster_profiles = \
    [
        {
            'name': 'ClusterProfileTest100',
            'interfaceLabel': 'lan0',
            'flowRedirection': 'Secure',
            'waitTime': 50,
            'userSessionSync': 'Secure'
        },
        {
            'name': 'ClusterProfileTest101',
            'interfaceLabel': 'lan0',
            'flowRedirection': 'Secure',
            'waitTime': 50,
            'userSessionSync': 'Secure'
        },
        {
            'name': 'ClusterProfileTest102',
            'interfaceLabel': 'lan0',
            'flowRedirection': 'Secure',
            'waitTime': 50,
            'userSessionSync': 'Secure'
        },
        {
            'name': 'ClusterProfileTest103',
            'interfaceLabel': 'lan0',
            'flowRedirection': 'Secure',
            'waitTime': 50,
            'userSessionSync': 'Secure'
        }
    ]
    try:
        result = orch.add_cluster_profiles(new_test_cluster_profiles)
        assert result['success'] == True
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")


@pytest.fixture
def setup_test_update_cluster_profile():
    global profile_id
    profiles = orch.get_all_cluster_profiles()
    for profile in profiles:
        if profile['name'] == 'ClusterProfileTest100':
            profile_id = profile['id']
            break
    yield


@pytest.mark.usefixtures("setup_test_update_cluster_profile")
def test_update_cluster_profile():
    update_existing_profile =\
    {
        'id': profile_id,
        'name': 'ClusterProfileTest100',
        'interfaceLabel': 'lan0',
        'flowRedirection': 'Secure',
        'waitTime': 55,
        'userSessionSync': 'Secure'
    }
    try:
        orch.update_cluster_profile(update_existing_profile)
        all_cluster_profiles = orch.get_all_cluster_profiles()
        for profile in all_cluster_profiles:
            if profile['id'] == profile_id:
                assert profile['waitTime'] == 55
                break
        # assert result['success'] == True
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")


# do not run standalone - previous tests are needed to get profile_id
def test_delete_cluster_profile():
    try:
        orch.delete_cluster_profile(profile_id)
        all_cluster_profiles = orch.get_all_cluster_profiles()
        for profile in all_cluster_profiles:
            if profile['id'] == profile_id:
                pytest.fail("Test failed: Cluster profile was not deleted")
                break
            else:
                assert True
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")


def test_get_all_cluster_profile_mappings():
    try:
        result = orch.get_all_cluster_profile_mappings()
        assert isinstance(result, dict)
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")


@pytest.fixture
def setup_get_all_cluster_profiles():
    try:
        global all_cluster_profiles
        all_cluster_profiles = orch.get_all_cluster_profiles()
        assert isinstance(all_cluster_profiles, list)
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")


@pytest.mark.usefixtures("setup_get_all_cluster_profiles")
def test_update_cluster_profile_mappings():
    try:
        profile_id = None
        found = False
        for profile in all_cluster_profiles:
            if profile['name'] == 'ClusterProfileTest101':
                profile_id = profile['id']
                found = True
            # used in the finally block below to set things back the way they were before
            if profile['name'] == cluster_name_assigned_to_lab_test_site:
                profile_id_frisco_original = profile['id']
                found = True
        if not found:
            assert False, f"'{cluster_name_assigned_to_lab_test_site}' not found."

        if profile_id is not None:
            new_cluster_profile_mapping =\
            {
                profile_id: [
                    site_name_in_lab_with_cluster,
                ]
            }
            result = orch.update_cluster_profile_mapping(new_cluster_profile_mapping)
            assert result['success'] == True
            profile_mappings = orch.get_all_cluster_profile_mappings()
            print()
            for profile in profile_mappings:
                if profile == profile_id:
                    assert profile_mappings[profile] == [site_name_in_lab_with_cluster]
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")
    finally:
        # put the mapping back to the way it was
        original_cluster_profile_mapping = \
            {
                profile_id_frisco_original: [
                    site_name_in_lab_with_cluster,
                ]
            }
        result = orch.update_cluster_profile_mapping(original_cluster_profile_mapping)
        assert result['success'] == True


def test_initialize_edge_ha_cluster():
    try:
        result = orch.initialize_edge_ha_cluster(device_ids_in_edge_ha_cluster)
        assert result == True
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")


# Cleanup after tests run
@pytest.fixture(scope="module", autouse=True)
def cleanup_after_cluster_tests():
    # Setup code (runs before tests) if needed
    yield
    # Cleanup code (runs after all tests in this module)
    print("Cleaning up resources after cluster tests")
    global profile_id
    profiles = orch.get_all_cluster_profiles()
    for profile in profiles:
        if (profile['name'] == 'ClusterProfileTest100' or
                profile['name'] == 'ClusterProfileTest101' or
                profile['name'] == 'ClusterProfileTest102' or
                profile['name'] == 'ClusterProfileTest103'):
            profile_id = profile['id']
            delete = orch.delete_cluster_profile(profile_id)








