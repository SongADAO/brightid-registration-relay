import os
import time
import threading
import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware
from flask import Flask, request, jsonify
from config import *

HOST = os.environ['HOST']
PORT = os.environ['PORT']
CONTEXT = os.environ['CONTEXT']
BRIGHTID_ADDRESS = os.environ['BRIGHTID_ADDRESS']
RELAYER_ADDRESS = os.environ['RELAYER_ADDRESS']
RELAYER_PRIVATE = os.environ['RELAYER_PRIVATE']

w3 = Web3(Web3.WebsocketProvider(RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
brightid = w3.eth.contract(address=BRIGHTID_ADDRESS, abi=BRIGHTID_ABI)

def transact(f):
    nonce = w3.eth.getTransactionCount(RELAYER_ADDRESS, 'pending')
    tx = f.buildTransaction({
        'chainId': CHAINID,
        'gas': GAS,
        'gasPrice': GAS_PRICE,
        'nonce': nonce,
    })
    signed_txn = w3.eth.account.sign_transaction(tx, private_key=RELAYER_PRIVATE)
    w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    receipt = w3.eth.waitForTransactionReceipt(signed_txn['hash'])
    assert receipt['status'], '{} failed'.format(tx)

def verify(addr):
    app.logger.info('verifying {}'.format(addr))

    addr = Web3.toChecksumAddress(addr)

    # Query user verification status.
    isVerifiedUser = brightid.functions.isVerifiedUser(addr).call()

    # Check to see if the user is already verified.
    if isVerifiedUser == True:
        app.logger.info('{} is verified'.format(addr))
        return

    app.logger.info('{} is NOT verified'.format(addr))

    # Get the BrightID data that will be used as
    # input for the verification transaction.
    data = requests.get(VERIFICATIONS_URL + '/' + CONTEXT + '/' + addr + '?signed=eth&timestamp=seconds').json()
    app.logger.info('Query verification signing data')
    app.logger.info(data)

    data = data['data']

    # Make sure all contextIds are in checksum format.
    data['contextIds'] = list(map(Web3.toChecksumAddress, data['contextIds']))

    # Run the verification transaction.
    app.logger.info('verifing {}'.format(addr))
    transact(brightid.functions.verify(
        data['contextIds'],
        data['timestamp'],
        data['sig']['v'],
        '0x' + data['sig']['r'],
        '0x' + data['sig']['s']
    ))

    app.logger.info('{} verified'.format(addr))

def sponsor(addr):
    app.logger.info('sponsoring {}'.format(addr))

    addr = Web3.toChecksumAddress(addr)

    # Query BrightID verification data
    data = requests.get(VERIFICATIONS_URL + '/' + CONTEXT + '/' + addr).json()
    # app.logger.info('Query verification data')
    # app.logger.info(data)

    # Check to see if the user is already sponsored.
    if 'errorNum' not in data or data['errorNum'] != NOT_SPONSORED:
        app.logger.info('{} is sponsored'.format(addr))
        return

    app.logger.info('{} is NOT sponsored'.format(addr))

    # Run the sponsorship transaction.
    app.logger.info('sponsoring {}'.format(addr))
    transact(brightid.functions.sponsor(addr))

    # Recheck a users sponsorship status in intervals.
    for i in range(SPONSOR_CHECK_NUM):
        app.logger.info('waiting for sponsor operation get applied')
        time.sleep(SPONSOR_CHECK_PERIOD)

        # Check the user's sponsorship status.
        data = requests.get(VERIFICATIONS_URL + '/' + CONTEXT + '/' + addr).json()
        if 'errorNum' not in data or data['errorNum'] != NOT_SPONSORED:
            app.logger.info('{} sponsored'.format(addr))
            return

    # User never ended up sponsored. Something must have failed.
    raise Exception('sponsoring failed')

def process(addr):
    app.logger.info('processing {}'.format(addr))

    addr = Web3.toChecksumAddress(addr)

    # waiting for link
    for i in range(LINK_CHECK_NUM):
        # Query BrightID verification data
        data = requests.get(VERIFICATIONS_URL + '/' + CONTEXT + '/' + addr).json()
        # app.logger.info('Query verification data')
        # app.logger.info(data)

        # Check to see if the user has a linked BrightID
        if 'errorNum' not in data or data['errorNum'] != NOT_FOUND:
            app.logger.info('{} is linked'.format(addr))
            break

        app.logger.info('{} is NOT linked'.format(addr))
        time.sleep(LINK_CHECK_PERIOD)
    else:
        app.logger.info('{} monitoring expired'.format(addr))
        return

    # Sponsor user
    sponsor(addr)

    # Query BrightID verification data
    # This can be used to check for a valid sponsorship and
    # will be used to complete the verification in the next step.
    data = requests.get(VERIFICATIONS_URL + '/' + CONTEXT + '/' + addr).json()
    # app.logger.info('Query verification data')
    # app.logger.info(data)

    # return if user does not have BrightID verification
    # or there are other errors
    if 'errorMessage' in data:
        app.logger.info(addr)
        app.logger.info(data['errorMessage'])
        return

    # verify user
    verify(addr)

processing = {}
def _process(addr):
    if addr in processing:
        return
    processing[addr] = True
    try:
        process(addr)
    except:
        raise
    finally:
        del processing[addr]

app = Flask(__name__)

@app.route("/")
def index_endpoint():
    app.logger.info('index_endpoint')
    return "running"

@app.route('/test', methods=['GET'])
def test_endpoint():
    app.logger.info('test_endpoint')

    # Check to make sure a wallet address is specified.
    addr = request.args.get('addr').lower()
    if not addr:
        return jsonify({'success': False})

    # Query BrightID verification data
    data = requests.get(VERIFICATIONS_URL + '/' + CONTEXT + '/' + addr).json()
    # app.logger.info('Query verification data')
    # app.logger.info(data)

    contextIds = data.get('data', {}).get('contextIds', [])
    if contextIds and contextIds[0] != addr:
        e = 'This address is used before. Link a new address or use {} as your last linked address!'.format(contextIds[0])
        return jsonify({'success': False, 'error': e})

    process(addr)

    return jsonify({'success': True})

@app.route('/register', methods=['POST'])
def register_endpoint():
    app.logger.info('register_endpoint')

    # Check to make sure a wallet address is specified.
    addr = request.json and request.json.get('addr', '').lower()
    if not addr:
        return jsonify({'success': False})

    # Query BrightID verification data
    data = requests.get(VERIFICATIONS_URL + '/' + CONTEXT + '/' + addr).json()
    # app.logger.info('Query verification data')
    # app.logger.info(data)

    contextIds = data.get('data', {}).get('contextIds', [])
    if contextIds and contextIds[0] != addr:
        e = 'This address is used before. Link a new address or use {} as your last linked address!'.format(contextIds[0])
        return jsonify({'success': False, 'error': e})

    threading.Thread(target=_process, args=(addr,)).start()

    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
