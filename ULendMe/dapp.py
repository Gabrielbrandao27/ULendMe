from os import environ
import logging
import requests
from auxiliar_functions import get_user_tag, hex2str, str2hex, handle_erc721_deposit

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

# this structure will store all the information related to the user
user_info = {}

def handle_advance(data):
    logger.info(f"Received advance request data {data}")
    notice = {"payload": data["payload"]}
    response = requests.post(rollup_server + "/notice", json=notice)
    logger.info(
        f"Received notice status {response.status_code} body {response.content}"
    )

    if data["metadata"]["msg_sender"].lower() == "0x68E3Ee84Bcb7543268D361Bb92D3bBB17e90b838":
        erc217, address_current, token_id = handle_erc721_deposit(data)
        user_info[user_tag]["loaned_tokens"].append({token_id: {"Token Contract": erc217}})

    else:
        address_current = data["metadata"]["msg_sender"].lower()

        wallet, offer_token_id, price, post_timestamp, loan_period = hex2str(data["payload"]).split(",")

    user_tag = get_user_tag(address_current, wallet)

    if user_tag not in user_info:
        user_info[user_tag] = {
            "offers": [],
            "loaned_tokens": [],
            "reputation": 0
        }

    else:
        user_info[user_tag]["offers"].append({offer_token_id: {"Price": price, "Post Date": post_timestamp, "Loan Period": loan_period}})
        
        
    return "accept"


def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    payload = hex2str(data["payload"])
    logger.info(f"data payload: {payload}")

    outgoing_payload = []

    inputs = []
    inputs = payload.split(",")

    if inputs[0] == "Catalog":
        for user_tag in user_info:
            if len(user_info[user_tag]["offers"]) > 0 :
                outgoing_payload.append(user_info[user_tag]["offers"])

        report = {"payload": str2hex(f'\n\nAll NFTs avaible on the Catalog:\n{outgoing_payload}')}
    
    elif inputs[0] == "Status":
        address_current = inputs[1].lower()
        wallet = inputs[2].lower()
        user_tag = get_user_tag(address_current, wallet)

        report = {"payload": str2hex(f'\n\nAll Loaned NFTs:\n{user_info[user_tag]["loaned_tokens"]}')}

    response = requests.post(rollup_server + "/report", json=report)
    logger.info(f"Received report status {response.status_code}")

    return "accept"


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}

while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        data = rollup_request["data"]
        handler = handlers[rollup_request["request_type"]]
        finish["status"] = handler(rollup_request["data"])
