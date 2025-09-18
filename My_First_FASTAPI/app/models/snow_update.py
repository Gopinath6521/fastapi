# servicenow_updater.py
import requests
from typing import Optional
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from app.models.get_sys_id import get_sctask_sys_id_aws_azure, snow_url, snow_user, snow_pass

def update_snow_ticket(
    snow_url: str,
    snow_user: str,
    snow_pass: str,
    ticket_sys_id: str,
    update_message: str,
    table: str = "sc_task"
):
    url = f"{snow_url}/api/now/table/{table}/{ticket_sys_id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "work_notes": update_message,
        "state": 2
    }

    response = requests.patch(url, auth=(snow_user, snow_pass), headers=headers, json=payload)

    if response.status_code not in [200, 204]:
        raise Exception(f"Failed to update ticket. Status: {response.status_code}, Response: {response.text}")

    return response.json()


def close_snow_ticket(
    snow_url: str,
    snow_user: str,
    snow_pass: str,
    ticket_sys_id: str,
    update_message: str,
    state: int,
    table: str = "sc_task"
):
    url = f"{snow_url}/api/now/table/{table}/{ticket_sys_id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
    
    "work_notes": update_message,
    "state": state
    
    }
    response = requests.patch(url, auth=(snow_user, snow_pass), headers=headers, json=payload)

    if response.status_code not in [200, 204]:
        raise Exception(f"Failed to update ticket. Status: {response.status_code}, Response: {response.text}")

    return response.json()

def route_snow_ticket(
    snow_url: str,
    snow_user: str,
    snow_pass: str,
    ticket_sys_id: str,
    update_message: str,
    state: int,
    assignment_group: str,
    table: str = "sc_task"
):
    url = f"{snow_url}/api/now/table/{table}/{ticket_sys_id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "work_notes": update_message,
        "assignment_group": "Windows"
    }

    response = requests.patch(url, auth=(snow_user, snow_pass), headers=headers, json=payload)

    if response.status_code not in [200, 204]:
        raise Exception(f"Failed to update ticket. Status: {response.status_code}, Response: {response.text}")

    return response.json()