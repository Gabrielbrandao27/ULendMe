from eth_abi_ext import decode_packed


def get_user_tag(address_current, wallet):
    game_key = f"{address_current}-{wallet}"

    return game_key


def hex2str(hex):
    """
    Decodes a hex string into a regular string
    """
    return bytes.fromhex(hex[2:]).decode("utf-8")


def str2hex(str):
    """
    Encodes a string as a hex string
    """
    return "0x" + str.encode("utf-8").hex()


def handle_erc721_deposit(data):
    binary = bytes.fromhex(data["payload"][2:])
    try:
        decoded = decode_packed(["address", "address", "uint256"], binary)
    except Exception as e:
        # payload does not conform to ERC721 deposit ABI
        return "reject"

    erc721 = decoded[0]
    depositor = decoded[1]
    token_id = decoded[2]

    return erc721, depositor, token_id
