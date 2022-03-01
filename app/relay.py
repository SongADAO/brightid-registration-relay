import time
import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware
from config import *

w3 = Web3(Web3.WebsocketProvider(RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def transact(f):
    nonce = w3.eth.getTransactionCount(RELAYER_ADDRESS, 'pending')
    tx = f.buildTransaction({
        'chainId': CHAINID,
        'gas': int(GAS),
        'gasPrice': int(GAS_PRICE),
        'nonce': nonce,
    })
    signed_txn = w3.eth.account.sign_transaction(tx, private_key=RELAYER_PRIVATE)
    w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    receipt = w3.eth.waitForTransactionReceipt(signed_txn['hash'])
    assert receipt['status'], '{} failed'.format(tx)

def toBase32(inputStr):
    return '0x' + inputStr.encode('utf-8').hex()

def checkBrightIDLink(contextId, logger):
    logger.info('checking BrightID link {}'.format(contextId))

    # waiting for link
    for i in range(LINK_CHECK_NUM):
        # Query BrightID verification data
        data = requests.get(VERIFICATIONS_URL + '/' + CONTEXT + '/' + contextId).json()
        # logger.info('Query verification data')
        # logger.info(data)

        # Check to see if the user has a linked BrightID
        if 'errorNum' not in data or data['errorNum'] != NOT_FOUND:
            logger.info('{} is linked'.format(contextId))

            # Verify the contextId is the one currently linked to the BrightID account
            contextIds = data.get('data', {}).get('contextIds', [])
            if contextIds and contextIds[0].lower() != contextId.lower():
                logger.info('wallet is not current BrightID link')
                logger.info(contextIds)
                logger.info(contextId)
                raise Exception('This wallet is not the most recent one you\'ve linked to BrightID. Please relink {} via BrightID!'.format(contextIds[0]))

            return

        logger.info('{} is NOT linked'.format(contextId))
        time.sleep(LINK_CHECK_PERIOD)
    else:
        logger.info('{} monitoring expired'.format(contextId))
        raise Exception('Could not determine that wallet is linked to BrightID.')

def checkBrightIDSponsorship(contextId, logger):
    # Query BrightID verification data
    # This can be used to check for a valid sponsorship and
    # will be used to complete the verification in the next step.
    data = requests.get(VERIFICATIONS_URL + '/' + CONTEXT + '/' + contextId).json()
    # logger.info('Query verification data')
    # logger.info(data)

    # return if user does not have BrightID verification
    # or there are other errors
    if 'errorMessage' in data:
        logger.info(data['errorMessage'])
        raise Exception(data['errorMessage'])

def verify(addr, logger):
    logger.info('verifying {}'.format(addr))

    addr = Web3.toChecksumAddress(addr)

    # Query user verification status.
    isVerifiedUser = contract.functions.isVerifiedUser(addr).call()

    # isVerifiedUser = False # DEBUG

    # Check to see if the user is already verified.
    if isVerifiedUser == True:
        logger.info('{} is verified'.format(addr))
        return

    logger.info('{} is NOT verified'.format(addr))

    # Get the BrightID data that will be used as
    # input for the verification transaction.
    data = requests.get(VERIFICATIONS_URL + '/' + CONTEXT + '/' + addr + '?signed=eth&timestamp=seconds').json()
    # logger.info('Query verification signing data')
    # logger.info(data)

    data = data['data']

    # Make sure all contextIds are in checksum format.
    data['contextIds'] = list(map(Web3.toChecksumAddress, data['contextIds']))

    # Run the verification transaction.
    logger.info('verifying {}'.format(addr))
    transact(contract.functions.verify(
        data['contextIds'],
        data['timestamp'],
        data['sig']['v'],
        '0x' + data['sig']['r'],
        '0x' + data['sig']['s']
    ))

    logger.info('{} verified'.format(addr))

def sponsor(addr, logger):
    logger.info('sponsoring {}'.format(addr))

    addr = Web3.toChecksumAddress(addr)

    # Query BrightID verification data
    data = requests.get(VERIFICATIONS_URL + '/' + CONTEXT + '/' + addr).json()
    # logger.info('Query verification data')
    # logger.info(data)

    # Check to see if the user is already sponsored.
    if 'errorNum' not in data or data['errorNum'] != NOT_SPONSORED:
        logger.info('{} is sponsored'.format(addr))
        return

    logger.info('{} is NOT sponsored'.format(addr))

    # Run the sponsorship transaction.
    logger.info('sponsoring {}'.format(addr))
    transact(contract.functions.sponsor(addr))

    # Recheck a users sponsorship status in intervals.
    for i in range(SPONSOR_CHECK_NUM):
        logger.info('waiting for sponsor operation get applied')
        time.sleep(SPONSOR_CHECK_PERIOD)

        # Query BrightID verification data
        data = requests.get(VERIFICATIONS_URL + '/' + CONTEXT + '/' + addr).json()
        # logger.info('Query verification data')
        # logger.info(data)

        # Check the user's sponsorship status.
        if 'errorNum' not in data or data['errorNum'] != NOT_SPONSORED:
            logger.info('{} sponsored'.format(addr))
            return

    # User never ended up sponsored. Something must have failed.
    logger.info('sponsoring failed')
    raise Exception('Sponsoring failed.')

def process(addr, logger):
    logger.info('processing {}'.format(addr))

    # Make sure the address is a current BrightID link
    checkBrightIDLink(addr, logger)

    # Sponsor user
    sponsor(addr, logger)

    # Make sure that the user is still sponsored
    checkBrightIDSponsorship(addr, logger)

    # Verify user
    verify(addr, logger)
