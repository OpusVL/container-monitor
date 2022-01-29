import click
import json
import socket
from configparser import ConfigParser

import docker

from icinga2 import Icinga2

__author__ = "Paul Bargewell"
__copyright__ = "Copyright 2021, Opus Vision Limited T/A OpusVL"
__credits__ = ["James Curtis"]
__license__ = "AGPL-3.0-or-later"
__maintainer__ = "Paul Bargewell"
__email__ = "paul.bargewell@opusvl.com"

config_object = ConfigParser()

HOSTNAME = socket.getfqdn()  # We will use this if no REPORTING_HOST

ICINGA2_ENDPOINT = None
ICINGA2_API_USER = None
ICINGA2_API_PASSWORD = None
ICINGA2_REPORTING_HOST = None
ICINGA2_SERVICE = None


class DockerWrapper:
    """
    A Wrapper for the Docker API
    """

    def get_container_status(self):
        """
        Get the status of all containers

        Returns:
            dict[]: array of all containers with state data from docker api
        """
        try:
            client = docker.from_env()
        except:
            return {"error": "Error connecting to docker api"}

        containers = []
        for c in client.containers.list(all=True):
            # Iterate the container list
            container = client.api.inspect_container(
                c.short_id
            )  # Get container details

            if (
                container.get("Config", {})
                .get("Labels", {})
                .get("com.opusvl.monitor", "on")
                != "off"
            ):
                containers.append(
                    {
                        "id": c.id,
                        "short_id": c.short_id,
                        "name": container["Name"],
                        "status": container["State"]["Status"],
                        "exitcode": container["State"]["ExitCode"],
                        "error": container["State"]["Error"],
                        "running": container["State"]["Running"],
                        # "paused": container["State"]["Paused"],
                        # "restarting": container["State"]["Restarting"],
                        # "oomkilled": container["State"]["OOMKilled"],
                        # "dead": container["State"]["Dead"],
                    }
                )
        return {"containers": containers}


def check_container_status(containers):
    """
    Iterate the containers dict and find if any of them are not running

    Args:
        containers (dict[]): List of containers being monitored

    Returns:
        dict: Icinga2 formatted payload
    """
    exit_status = 0
    plugin_output = ""
    performance_data = ""
    running = total = 0

    for container in containers:
        if container.get("status", "running") != "running":
            exit_status = 2
            plugin_output = (
                plugin_output
                + " "
                + (container.get("name", "") + " " + container.get("status", ""))
                + " | "
            )
        else:
            running = running + 1
        total = total + 1

    performance_data = f"running={running}; total={total}; "

    if exit_status == 2:
        plugin_output = f"CRITICAL {plugin_output}"
    elif exit_status == 1:
        plugin_output = f"WARNING {plugin_output}"
    else:
        plugin_output = f"OK {plugin_output}"

    return {
        "exit_status": exit_status,
        "plugin_output": plugin_output,
        "performance_data": performance_data,
    }


def read_config(config_file="settings.ini"):
    config_object.read(config_file)


@click.command()
@click.option(
    "-f", "--config-file", type=str, help="Settings file to use", default="settings.ini"
)
def main(config_file):
    """
    Container Monitor

    """
    read_config(config_file)

    try:
        settings = config_object["settings"]
    except:
        print(f"Unable to read config file: {config_file}")
        return

    ICINGA2_ENDPOINT = settings.get("ICINGA2_ENDPOINT", "http://icinga2:5665")
    ICINGA2_API_USER = settings.get("ICINGA2_API_USER", "container-monitor")
    ICINGA2_API_PASSWORD = settings.get("ICINGA2_API_PASSWORD", "")
    ICINGA2_REPORTING_HOST = settings.get("ICINGA2_REPORTING_HOST", HOSTNAME)
    ICINGA2_SERVICE = settings.get("ICINGA2_SERVICE", "check_dockmon")

    docker_wrapper = DockerWrapper()  # Use the Docker API
    containers = (
        docker_wrapper.get_container_status()
    )  # Fetch the status of all containers

    # print(json.dumps(containers, indent=4))

    if containers.get("error"):
        # If we get an error pass it on to Icinga2
        error = containers.get("error", "")
        payload = {
            "exit_status": 2,
            "plugin_output": f"CRITICAL - {error}",
            "performance_data": "",
        }
    else:
        payload = check_container_status(containers.get("containers"))

    # print(payload)

    icinga = Icinga2(
        ICINGA2_API_USER,
        ICINGA2_API_PASSWORD,
        ICINGA2_ENDPOINT,
    )  # Create new isntance of Incinga2
    response = icinga.process_check_result(
        ICINGA2_REPORTING_HOST,
        ICINGA2_SERVICE,
        payload=payload,
    )  # Submit a process check result
    print(json.dumps(response, indent=4))


if __name__ == "__main__":
    main()


@click.group()
def cli():
    pass
