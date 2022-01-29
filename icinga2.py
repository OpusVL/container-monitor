import requests
from requests.auth import HTTPBasicAuth

__author__ = "Paul Bargewell"
__copyright__ = "Copyright 2021, Opus Vision Limited T/A OpusVL"
__credits__ = ["James Curtis"]
__license__ = "AGPL-3.0-or-later"
__maintainer__ = "Paul Bargewell"
__email__ = "paul.bargewell@opusvl.com"


class Icinga2:
    """
    Make API calls to Icinga2
    """

    _username = None
    _password = None
    _endpoint = None

    def __init__(self, username, password, endpoint):
        """
        Initialise the class

        Args:
            username (string): Icinga2 API User
            password (string): Icinga2 API Password
            endpoint (string): Base URL for the Icinga2 instance, eg. http://icinga2:5665
        """
        self._username = username
        self._password = password
        self._endpoint = endpoint

    def api_call(self, path, payload):
        """
        Submit the API call

        Args:
            path (string): Path to the call
            payload (dict): Data to submit

        Returns:
            dict: API Response or {}
        """
        response = requests.post(
            path,
            auth=HTTPBasicAuth(self._username, self._password),
            json=payload,
            headers={"Accept": "application/json"},
        )

        return response.json()

    def process_check_result(self, reporting_host, service, payload):
        """
        Submit a process check result

        Args:
            reporting_host (string): Icinga2 Host to report as
            service (string): Service on the Icinga2 Host to report to
            payload (dict): The data to deliver

        Payload format:
            {
                "exit_status": 0,
                "plugin_output": "OK",
                "performance_data": "string",
                "check_source": "string",
            }
        
        This is a curl of what this call should replicate
        ${CURL} --fail -k -s -u ${ICINGA_USER:-root}:${ICINGA_PASSWORD:-password} -H 'Accept: application/json' -X POST \
            "https://${ICINGA_HOST:-icinga2}:${ICINGA_PORT:-5665}/v1/actions/process-check-result?service=${REPORTING_HOST}!${SERVICE}" \
            -d "${JSON}"        
        """
        response = self.api_call(
            path=f"{self._endpoint}/v1/actions/process-check-result?service={reporting_host}!{service}",
            payload=payload,
        )

        return response
