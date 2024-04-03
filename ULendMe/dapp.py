from os import environ
import cartesi_wallet.wallet as Wallet
import logging
import requests
from utils import hex2str, str2hex, encode, decode_json
from urllib.parse import urlparse

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

DAPP_RELAY = "0xF5DE34d6BbC0446E2a45719E718efEbaaE179daE"
ERC_721 = "0x237F8DD094C0e47f4236f12b4Fa01d6Dae89fb87"
ERC_20 = "0x9C21AEb2093C32DDbC53eEF24B873BDCd1aDa1DB"
ETHER = "0xFfdbe43d4c855BF7e0f105c400A50857f53AB044"

wallet = Wallet

# this structure will store all the information related to the user
user_info = {}


def handle_advance(data):
    logger.info(f"Received advance request data {data}")
    msg_sender = data["metadata"]["msg_sender"].lower()
    payload = data["payload"]

    # Set Relay
    if msg_sender.lower() == DAPP_RELAY.lower():
        global rollup_address
        logger.info(f"Received advance from dapp relay")
        rollup_address = payload
        response = requests.post(
            rollup_server + "/notice",
            json={"payload": str2hex(f"Set rollup_address {rollup_address}")},
        )
        return "accept"

    # Depositing Ether and ERC721
    try:
        notice = None
        if msg_sender.lower() == ETHER.lower():
            notice = wallet.ether_deposit_process(payload)
            response = requests.post(
                rollup_server + "/notice", json={"payload": notice.payload}
            )
        elif msg_sender == ERC_721.lower():
            notice = wallet.erc721_deposit_process(payload)
            response = requests.post(
                rollup_server + "/notice", json={"payload": notice.payload}
            )
        if notice:
            logger.info(
                f"Received notice status {response.status_code} body {response.content}"
            )
            return "accept"
    except Exception as error:
        error_msg = f"Failed to process deposit '{payload}'. {error}"
        logger.debug(error_msg, exc_info=True)
        return "reject"

    # Transfering and Withdrawing Ether and ERC721
    try:
        req_json = decode_json(payload)
        print(req_json)

        if req_json["method"] == "ether_transfer":
            notice = wallet.ether_transfer(
                req_json["from"].lower(), req_json["to"].lower(), req_json["amount"]
            )
            response = requests.post(
                rollup_server + "/notice", json={"payload": notice.payload}
            )
            return "accept"
        
        if req_json["method"] == "ether_withdraw":
            voucher = wallet.ether_withdraw(
                rollup_address, req_json["from"].lower(), req_json["amount"]
            )
            response = requests.post(
                rollup_server + "/voucher",
                json={"payload": voucher.payload, "destination": voucher.destination},
            )
            return "accept"
        
        if req_json["method"] == "erc721_transfer":
            notice = wallet.erc721_transfer(
                req_json["from"].lower(),
                req_json["to"].lower(),
                req_json["erc721"].lower(),
                req_json["token_id"],
            )
            response = requests.post(
                rollup_server + "/notice", json={"payload": notice.payload}
            )
            return "accept"
        
        if req_json["method"] == "erc721_withdraw":
            voucher = wallet.erc721_withdraw(
                rollup_address,
                req_json["from"].lower(),
                req_json["erc721"].lower(),
                req_json["token_id"],
            )
            response = requests.post(
                rollup_server + "/voucher",
                json={"payload": voucher.payload, "destination": voucher.destination},
            )
            return "accept"

    except Exception as error:
        error_msg = f"Failed to process command '{payload}'. {error}"
        response = requests.post(
            rollup_server + "/report", json={"payload": encode(error_msg)}
        )
        logger.debug(error_msg, exc_info=True)
        return "reject"


    # Adding offer to the Catalog
    try:
        offer, offer_token_id, price, post_timestamp, loan_period = hex2str(
            payload
        ).split(",")

        if offer == "offer":
            address_current = msg_sender

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

    except Exception as error:
        error_msg = f"Failed to process offer '{payload}'. {error}"
        logger.debug(error_msg, exc_info=True)
        return "reject"


def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    payload = hex2str(data["payload"])
    logger.info(f"data payload: {payload}")

    inputs = []
    inputs = payload.split(",")
    report = {"payload": ""}

    if inputs[0] == "Catalog":
        report = {
            "payload": str2hex(f"\n\nAll NFTs avaible on the Catalog:\n{user_info}")
        }

        response = requests.post(rollup_server + "/report", json=report)
        logger.info(f"Received report status {response.status_code}")

        return "accept"

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

    try:
        url = urlparse(hex2str(data["payload"]))
        if url.path.startswith("balance/"):
            info = url.path.replace("balance/", "").split("/")
            token_type, account = info[0].lower(), info[1].lower()
            token_address, token_id, amount = "", 0, 0

            if token_type == "ether":
                amount = wallet.balance_get(account).ether_get()

            elif token_type == "erc721":
                token_address, token_id = info[2], info[3]
                amount = (
                    1
                    if token_id
                    in wallet.balance_get(account).erc721_get(token_address.lower())
                    else 0
                )

            report = {
                "payload": encode(
                    {"token_id": token_id, "amount": amount, "token_type": token_type}
                )
            }
            response = requests.post(rollup_server + "/report", json=report)
            logger.info(
                f"Received report status {response.status_code} body {response.content}"
            )

        return "accept"

    except Exception as error:
        error_msg = f"Failed to process inspect request. {error}"
        logger.debug(error_msg, exc_info=True)
        return "reject"


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
