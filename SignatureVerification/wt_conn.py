import environ
import requests
import json

env = environ.Env()

WEETRUST_USER_ID = env("WEETRUST_USER_ID")
WEETRUST_API_KEY = env("WEETRUST_API_KEY")
WEETRUST_API_URL = env("WEETRUST_API_URL")


def get_token():
    """Get the access token from the API. Return the access token as a string."""
    err_message = "Error: No se puede adquirir un token para comenzar la tarea; póngase en contacto con el soporte técnico."
    try:
        headersList = {
            "user-id": WEETRUST_USER_ID,
            "api-key": WEETRUST_API_KEY,
            "Content-Type": "application/json",
        }
        lb_request = requests.post(f"{WEETRUST_API_URL}/access/token", headers=headersList)
        lb_request.raise_for_status()  # Raises a HTTPError if the response status is 4xx, 5xx

        response_data = lb_request.json()
        access_token = response_data["responseData"]["accessToken"]
        return access_token

    except requests.exceptions.HTTPError as http_err:
        # add error {http_err} to log - f'HTTP error occurred: {http_err}'
        return err_message
    except requests.exceptions.RequestException as err:
        # add error {err} to log - f'Request error occurred: {err}'
        return err_message
    except Exception as e:
        # add error {e} to log - f'An error occurred: {e}'
        return err_message


def headers_list():
    """Get the headers list for the API. Return the headers list as a dictionary."""
    headersList = {
        "user-id": WEETRUST_USER_ID,
        "token": get_token()
    }
    return headersList


def add_document(document_path):
    """ Add a document to the API. Return the response from the API as a JSON object."""
    payload = ""
    headers = headers_list()
    headers["position"] = "geolocation"
    with open(document_path, "rb") as f:
        post_files = {"document": f}
        r = requests.post(f"{WEETRUST_API_URL}/documents", data=payload, files=post_files, headers=headers)
    if r.status_code == 200:
        return r.json(), r.status_code
    else:
        return r.text, r.status_code


def get_document_list():
    """ Get the list of documents from the API. Return the response from the API as a JSON object."""
    r = requests.get(f"{WEETRUST_API_URL}/documents", headers=headers_list())
    if r.status_code == 200:
        return r.json(), r.status_code
    else:
        return r.text, r.status_code


def get_document(document_id):
    """ Get a specific document from the API. Return the response from the API as a JSON object."""
    r = requests.get(f"{WEETRUST_API_URL}/documents/{document_id}", headers=headers_list())
    if r.status_code == 200:
        return r.json(), r.status_code
    else:
        return r.text, r.status_code


def delete_document(document_id):
    """ Delete a specific document from the API. Return the response from the API as a JSON object."""
    r = requests.delete(
        f"{WEETRUST_API_URL}/documents/?documentID={document_id}", headers=headers_list()
    )
    if r.status_code == 200:
        return r.json(), r.status_code
    else:
        return r.text, r.status_code


def fixed_coordinates(coordinates):
    headers_lst = headers_list()
    headers_lst["Content-Type"] = "application/json"

    payload = json.dumps(coordinates)
    r = requests.put(f"{WEETRUST_API_URL}/documents/fixed-signatory", headers=headers_lst, data=payload)
    if r.status_code == 200:
        return r.json(), r.status_code
    else:
        return r.text, r.status_code


def request_signature(pl_data):
    headers_lst = headers_list()
    headers_lst["Content-Type"] = "application/json"

    payload = json.dumps(pl_data)
    r = requests.put(
        f"{WEETRUST_API_URL}/documents/signatory", headers=headers_lst, data=payload
    )
    if r.status_code == 200:
        return r.json(), r.status_code
    else:
        return r.text, r.status_code


def resend_signature(doc_id):
    headers_lst = headers_list()
    payload = ""
    r = requests.put(
        f"{WEETRUST_API_URL}/documents/resend-email?documentID={doc_id}", headers=headers_lst, data=payload
    )
    if r.status_code == 200:
        return r.json(), r.status_code
    else:
        return r.text, r.status_code


def share_document(document_id, email):
    """ Share a document with a user. Return the response from the API as a JSON object. "Document status should be completed" """
    payload = json.dumps({"documentID": document_id, "postedTo": email})
    r = requests.put(
        f"{WEETRUST_API_URL}/documents/share", headers=headers_list(), data=payload
    )
    if r.status_code == 200:
        return r.json(), r.status_code
    else:
        return r.text, r.status_code


def add_webhook(url, hook_type="completedDocument"):
    """Add a webhook to the API. Return the response from the API as a JSON object."""
    payload = ""
    r = requests.post(
        f"{WEETRUST_API_URL}/webhooks?url={url}&type={hook_type}",
        headers=headers_list(),
        data=payload,
    )
    if r.status_code != 200:
        return f"Error: {r.status_code} - {r.text}"
    return r.json()


def get_webhooks(webhook_id=None):
    """Get all webhooks or a specific webhook by ID. Return the response from the API as a JSON object."""
    if webhook_id:
        url_tail = f'?webhookID={webhook_id}'
    else:
        url_tail = ''
    payload = ""
    r = requests.get(
        f"{WEETRUST_API_URL}/webhooks{url_tail}",
        headers=headers_list(),
        data=payload,
    )
    if r.status_code != 200:
        return f"Error: {r.status_code} - {r.text}"
    return r.json()


def update_webhook(url, webhook_id, pl_data):
    """ Update a webhook by ID. Return the response from the API as a JSON object."""
    payload = json.dumps(pl_data)
    r = requests.put(
        f"{WEETRUST_API_URL}/webhooks?url={url}&webHookID={webhook_id}",
        headers=headers_list(),
        data=payload,
    )
    if r.status_code != 200:
        return f"Error: {r.status_code} - {r.text}"
    return r.json()


def d_webhook(wh_id):
    reqUrl = f"{WEETRUST_API_URL}/webhooks?webHookID={wh_id}"
    headersList = headers_list()
    payload = ""
    response = requests.request("DELETE", reqUrl, data=payload, headers=headersList)
    return response.json()
