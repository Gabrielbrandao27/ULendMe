from cartesi_wallet.outputs import Voucher
from eth_abi import encode as encode_abi
from utils import hex2str, str2hex, encode, decode_json
from urllib.parse import urlparse
import web3
from web3 import Web3
import cartesi_wallet.wallet as Wallet
import logging
import json
import os
import requests

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = os.environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

# Connect to the Ethereum network
web3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"))

# Load the ABI of the Factory contract
with open("factory_abi.json") as f:
    factory_abi = json.load(f)

# Replace with the actual deployed Factory contract address
FACTORY_CONTRACT_ADDRESS = "0xYourFactoryContractAddress"

# Initialize the Factory contract
factory_contract = web3.eth.contract(address=FACTORY_CONTRACT_ADDRESS, abi=factory_abi)

DAPP_RELAY = "0xF5DE34d6BbC0446E2a45719E718efEbaaE179daE"
ERC_721 = "0x237F8DD094C0e47f4236f12b4Fa01d6Dae89fb87"
ERC_20 = "0x9C21AEb2093C32DDbC53eEF24B873BDCd1aDa1DB"
ETHER = "0xFfdbe43d4c855BF7e0f105c400A50857f53AB044"

SAFE_MINT_FUNCTION = b"\x75\x5e\xdd\x17"
ERC_721_CONTRACT_ADRESS = "0xc6e7df5e7b4f2a278906862b61205850344d4e7d"

wallet = Wallet
rollup_address = ""

# this structure will store all the information related to the user
user_info = {}

# this structure will store all the information related to the NFTs listed on the wall
nft_listings = {}

# It's a dictionary where token_id is the key and the voucher object is the value.
pending_vouchers = {}


def post_nft_for_lending(owner, token_id, price, lending_period):
    logger.info(f"User {owner} is posting NFT {token_id} for lending")

    if owner not in nft_listings:
        nft_listings[owner] = []

    nft_listings[owner].append(
        {
            "token_id": token_id,
            "price": price,
            "lending_period": lending_period,
            "is_available": True,  # Initially, the NFT is available for lending
        }
    )

    logger.info(f"NFT {token_id} posted for lending by {owner}")

    return "accept"


def deploy_multisig_wallet(owner, borrower, token_id):
    logger.info(
        f"Deploying MultiSig Wallet for NFT {token_id} between {owner} and {borrower}"
    )

    # Call the Factory contract to deploy a new multi-sig wallet.
    # Prepare transaction parameters
    tx = factory_contract.functions.deployMultiSigWallet(owner, borrower).buildTransaction({
        'from': owner,          # The owner initiates the transaction
        'gas': 3000000,         # Set gas limit
        'gasPrice': web3.toWei('20', 'gwei')  # Set gas price
    })

    # Send the transaction to the Ethereum network
    signed_tx = web3.eth.account.sign_transaction(tx, private_key='YOUR_PRIVATE_KEY')
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # Wait for the transaction to be mined and retrieve the receipt
    receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    multisig_address = receipt["contractAddress"]

    logger.info(f"Deployed MultiSig Wallet at {multisig_address} for NFT {token_id}")

    return multisig_address


def create_voucher_for_new_multisig_wallet(owner, borrower, token_id, multisig_address):
    logger.info(
        f"Creating voucher to transfer NFT {token_id} to MultiSig Wallet {multisig_address}"
    )

    # Prepare the voucher details
    voucher = Voucher(
        contract_address=multisig_address,  # Use the new multi-sig wallet address
        payload=encode_abi(
            ["address", "uint256"],  # types of the arguments
            [owner, token_id],  # values of the arguments
        ),
    )  # Prepare the payload for the NFT transfer

    # Store the voucher in state for later execution
    pending_vouchers[token_id] = voucher

    logger.info(
        f"Voucher created for NFT {token_id} to MultiSig Wallet {multisig_address}"
    )

    return "accept"


def execute_voucher_for_nft_transfer(token_id):
    logger.info(f"Executing voucher to transfer NFT {token_id}")

    # Retrieve the voucher for this NFT
    voucher = pending_vouchers.get(token_id)
    if not voucher:
        error_msg = f"No voucher found for NFT {token_id}"
        logger.error(error_msg)
        return "reject"

    # Execute the voucher using the rollup server
    response = requests.post(
        rollup_server + "/voucher",
        json={"payload": voucher.payload, "destination": voucher.destination},
    )

    if response.status_code == 200:
        logger.info(f"Voucher executed for NFT {token_id}")
    else:
        logger.error(f"Failed to execute voucher for NFT {token_id}")

    return "accept"


def borrow_nft_request(borrower, owner, token_id):
    logger.info(f"User {borrower} is requesting to borrow NFT {token_id} from {owner}")

    # Check if the NFT is available
    if owner not in nft_listings or token_id not in [
        item["token_id"] for item in nft_listings[owner] if item["is_available"]
    ]:
        error_msg = f"NFT {token_id} is not available for borrowing."
        logger.info(error_msg)
        return "reject"

    # Mark the NFT as unavailable
    for item in nft_listings[owner]:
        if item["token_id"] == token_id:
            item["is_available"] = False
            break

    # Deploy a new multi-sig wallet using the factory
    multisig_address = deploy_multisig_wallet(owner, borrower, token_id)

    # Create the voucher for transferring the NFT to the multi-sig wallet
    create_voucher_for_new_multisig_wallet(owner, borrower, token_id, multisig_address)

    # Prompt for the voucher to be executed automatically after User2 accepts
    execute_voucher_for_nft_transfer(token_id)

    logger.info(
        f"Borrow request processed for NFT {token_id}. MultiSig Wallet created at {multisig_address}"
    )

    return "accept"


def handle_advance(data):
    logger.info(f"Received advance request data {data}")
    msg_sender = data["metadata"]["msg_sender"].lower()
    payload = data["payload"]
    logger.info(f"Chegou aqui: {payload}")

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

    # Transfering and Withdrawing Ether and ERC721 and minting NFT
    try:
        if rollup_address == "":
            raise Exception("Dapp Relay not set")

        req_json = decode_json(payload)
        print(req_json)

        if req_json["method"] == "ether_transfer":
            converted_value = (
                int(req_json["amount"])
                if isinstance(req_json["amount"], str) and req_json["amount"].isdigit()
                else req_json["amount"]
            )
            notice = wallet.ether_transfer(
                req_json["from"].lower(), req_json["to"].lower(), converted_value
            )
            response = requests.post(
                rollup_server + "/notice", json={"payload": notice.payload}
            )
            return "accept"

        if req_json["method"] == "ether_withdraw":
            converted_value = (
                int(req_json["amount"])
                if isinstance(req_json["amount"], str) and req_json["amount"].isdigit()
                else req_json["amount"]
            )
            voucher = wallet.ether_withdraw(
                rollup_address, req_json["from"].lower(), converted_value
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

        if req_json["method"] == "erc721_mint":
            payload = SAFE_MINT_FUNCTION + encode_abi(["address"], [msg_sender])
            logger.info(payload)
            contract_address = ERC_721_CONTRACT_ADRESS.lower()
            voucher = Voucher(contract_address, payload)
            response = requests.post(
                rollup_server + "/voucher",
                json={"destination": voucher.destination, "payload": voucher.payload},
            )
            return "accept"

    except Exception as error:
        error_msg = f"Failed to process command '{payload}'. {error}"
        response = requests.post(
            rollup_server + "/report", json={"payload": encode(error_msg)}
        )
        logger.debug(error_msg, exc_info=True)
        return "reject"

    # Posting an NFT for lending
    try:
        req_json = decode_json(payload)
        if req_json["method"] == "post_nft_for_lending":
            owner = msg_sender
            token_id = req_json["token_id"]
            price = req_json["price"]
            lending_period = req_json["lending_period"]

            post_nft_for_lending(owner, token_id, price, lending_period)

            response = requests.post(
                rollup_server + "/notice",
                json={
                    "payload": str2hex(f"NFT {token_id} posted by {owner} for lending")
                },
            )
            return "accept"

    except Exception as error:
        error_msg = f"Failed to post NFT for lending '{payload}'. {error}"
        logger.debug(error_msg, exc_info=True)
        return "reject"

    # Handling NFT borrowing request
    try:
        req_json = decode_json(payload)
        if req_json["method"] == "borrow_nft":
            borrower = msg_sender
            owner = req_json["owner"].lower()
            token_id = req_json["token_id"]

            borrow_nft_request(borrower, owner, token_id)

            response = requests.post(
                rollup_server + "/notice",
                json={
                    "payload": str2hex(
                        f"Borrow request for NFT {token_id} sent to owner {owner}"
                    )
                },
            )
            return "accept"

    except Exception as error:
        error_msg = f"Failed to process borrow request '{payload}'. {error}"
        logger.debug(error_msg, exc_info=True)
        return "reject"


def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    payload = hex2str(data["payload"])
    logger.info(f"data payload: {payload}")

    inputs = []
    inputs = payload.split(",")
    report = {"payload": ""}

    # Checking if the Inspect was for NFT Catalog
    if inputs[0] == "Catalog":
        report = {
            "payload": str2hex(f"\n\nAll NFTs avaible on the Catalog:\n{nft_listings}")
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
