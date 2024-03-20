from os import environ
import logging
import requests
from auxiliar_functions import get_user_tag, hex2str, str2hex

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
    address_current = data["metadata"]["msg_sender"].lower()
    post_type, wallet, nft_id, price, post_timestamp, loan_period = hex2str(data["payload"]).split(",")

    user_tag = get_user_tag(address_current, wallet)

    if user_tag not in user_info:
        user_info[user_tag] = {
            "offers": [],
            "demands": [],
            "reputation": 0
        }

    if post_type == "offer":
        user_info[user_tag]["offers"].append({nft_id: [price, post_timestamp, loan_period]})

    elif post_type == "demand":
        user_info[user_tag]["demand"].append({nft_id: [price, post_timestamp, loan_period]})
    
    
    
    return "accept"

# user_info = {
#     "0x1": {
#         "offers": [{'macaco#123': ['0,065', '18-03-2024-19:30', '7']}],
#         "demands": [],
#         "reputation": 0
#     },
# }



def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    payload = hex2str(data["payload"])
    logger.info(f"data payload: {payload}")

    outgoing_payload = []

    if payload == "posts":
        for user_tag in user_info:
            if len(user_info[user_tag]["offers"]) > 0 :
                outgoing_payload.append(user_info[user_tag]["offers"])
            elif len(user_info[user_tag]["demands"]) > 0:
                outgoing_payload.append(user_info[user_tag]["demands"])

        report = {"payload": str2hex(f'\n\nAll Offers and Demands:\n\n{outgoing_payload}')}

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
