from os import environ
import cartesi
import cartesi_wallet.wallet as Wallet
import logging
import requests
from utils import hex2str, str2hex, handle_erc721_deposit

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

DAPP_RELAY = "0xF5DE34d6BbC0446E2a45719E718efEbaaE179daE"
ERC_721 = "0x237F8DD094C0e47f4236f12b4Fa01d6Dae89fb87"
ERC_20 = "0x9C21AEb2093C32DDbC53eEF24B873BDCd1aDa1DB"
ETHER = "0xFfdbe43d4c855BF7e0f105c400A50857f53AB044"

# this structure will store all the information related to the user
user_info = {}


def handle_advance(data):
    logger.info(f"Received advance request data {data}")
    notice = {"payload": data["payload"]}
    response = requests.post(rollup_server + "/notice", json=notice)
    logger.info(
        f"Received notice status {response.status_code} body {response.content}"
    )

    msg_sender = data["metadata"]["msg_sender"].lower()

    if msg_sender == ERC_721:
        erc217, address_current, token_id = handle_erc721_deposit(data)
        user_info[address_current]["loaned_tokens"].append(
            {token_id: {"Token Contract": erc217}}
        )

    else:
        address_current = msg_sender

        offer_token_id, price, post_timestamp, loan_period = hex2str(
            data["payload"]
        ).split(",")

        if address_current not in user_info:
            user_info[address_current] = {
                "offers": [],
                "loaned_tokens": [],
                "reputation": 0,
            }

        user_info[address_current]["offers"].append(
            {
                offer_token_id: {
                    "Price": price,
                    "Post Date": post_timestamp,
                    "Loan Period": loan_period,
                }
            }
        )

    return "accept"


def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    payload = hex2str(data["payload"])
    logger.info(f"data payload: {payload}")

    outgoing_payload = []

    inputs = []
    inputs = payload.split(",")
    report = {"payload": ""}

    if inputs[0] == "Catalog":
        report = {
            "payload": str2hex(f"\n\nAll NFTs avaible on the Catalog:\n{user_info}")
        }

    elif inputs[0] == "Status":
        address_current = inputs[1].lower()
        report = {
            "payload": str2hex(
                f'\n\nAll Loaned NFTs:\n{user_info[address_current]["loaned_tokens"]}'
            )
        }

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
