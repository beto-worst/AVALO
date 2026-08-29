def fixed_signatory_generator(document_id: str, coordinates: list, emails: dict) -> dict:
    """
    This function generates a dictionary with a fixed signatory structure for a given document.
    To be used with the fixed_coordinates() function to update the signatory coordinates with weetrust API.

    Parameters:
    document_id (str): The ID of the document for which the signatory is being generated.
    coordinates (list): A list of tuples where each tuple contains a key and a dictionary.
                        The dictionary contains user details and their coordinates.
    emails (dict): A dictionary where each key-value pair represents a user key and their corresponding email.

    Returns:
    dict: A dictionary with a fixed signatory structure. The structure includes the document ID and
          a list of static sign positions, each containing user details and their coordinates.

    Note:
    This function modifies the input 'coordinates' list by updating the user email in coordinates
    matching the key in 'emails' dictionary.
    """

    # update user email in coordinates matching the key in emails
    for key, value in emails.items():
        for i in coordinates:
            if i[0] == key:
                i[1]["user"]["email"] = value
                break

    # create fixed_signatory dict
    fixed_signatory = {"documentID": "", "staticSignPositions": []}

    # update documentID in fixed_signatory
    fixed_signatory["documentID"] = document_id

    # update staticSignPositions in fixed_signatory with with the second element in each coordinates dict
    for i in coordinates:
        fixed_signatory["staticSignPositions"].append(i[1])

    return fixed_signatory


def update_signatory_array(email_1, name_1, role_1, email_2, name_2, role_2, contract_name):
    """ To be used with create_signature_request(), this function creates a signatory array for a signature request.
    pass to create_signature_request() as first argument (emails) to create a signature request as a list of dictionaries."""

    signatory_array = [
        {
            "email": email_1,
            "name": name_1,
            "role": role_1,
            "contract": contract_name,
        },
        {
            "email": email_2,
            "name": name_2,
            "role": role_2,
            "contract": contract_name,
        },
    ]
    return signatory_array


def create_signature_request(emails: list, document_id: str, nickname: str, message: str, title: str, shared=None) -> dict:
    """
    Creates a signature request.

    Args:
        emails (list): A list of email addresses to send the signature request to.
        document_id (str): The ID of the document to be signed.
        nickname (str): The nickname of the sender.
        message (str): The message to include with the signature request.
        title (str): The title of the signature request.
        shared (str, optional): If True, the document will be shared with the recipients. Defaults to None.

        # return from update_signatory_array()
        emails: [
            {
                "email": "name@email.com",
                "name": "First name Last name",
                "role": "arrendatario",
                "contract": "contract name",
            },
            {
                "email": "name@email.com",
                "name": "First name Last name",
                "role": "arrendador",
                "contract": "contract name",
            },
        ]

    dict: A dictionary representing the signature request. The dictionary includes details about the document,
          the signatories, and other settings for the signature request.

    The signatory dictionary for each email in the emails list is created using a template. If the role of the email
    is "arrendatario", the identification is set to "id". Otherwise, the identification key is removed from the signatory.
    """

    # 1. Create a signatory for each email
    signatory_template = {
        "emailID": "",
        "name": "",
        "identification": "",  # for the renter only
        "order": 0,
    }

    # for each email in emails list create a signatory using the signatory_template,
    # if emails role equals "arrendatario" then set the identification to "face" else remove the identification key from the signatory
    signatories = []
    for email in emails:
        signatory = signatory_template.copy()
        signatory["emailID"] = email["email"]
        signatory["name"] = email["name"]
        signatory["identification"] = "id"
        # Irving asked for all signatories to have identification
        # if email["role"] == "arrendatario":
        #     signatory["identification"] = "id"
        # else:
        #     signatory.pop("identification")
        signatories.append(signatory)

    if shared:
        shared_with = [{"emailID": f"{shared}"}]
    else:
        shared_with = []

    # 2. Create the signature request
    signature_request = {
        "documentID": document_id,
        "nickname": nickname,
        "message": message,
        "title": title,
        "hasOrder": False,
        "disableMailing": False,
        "signatory": signatories,
        "sharedWith": shared_with,
    }

    return signature_request