import json
from flask import Flask, request, jsonify

from config import *
from cors import *
from relay import *

app = Flask(__name__)

def format_error(e):
    errorCode = 0
    errorMessage = str(e)

    app.logger.info(str(e))

    try:
        e = ast.literal_eval(str(e))
    except Exception:
        pass

    if (type(e) is dict) and ('code' in e):
        errorCode = e['code']

    if (type(e) is dict) and ('message' in e):
        errorMessage = e['message']

    return jsonify({
        'success': False,
        'error': {'code': errorCode, 'message': errorMessage},
    })

def format_success():
    return jsonify({'success': True})

# Index
@app.route(RELAY_BASE_ROUTE + '/')
def index_endpoint():
    app.logger.info('index_endpoint')

    return 'running'

# Register CORS Preflight
@app.route(RELAY_BASE_ROUTE + '/register', methods=['OPTIONS'])
def register_endpoint_options():
    app.logger.info('register_endpoint_options')

    return cors_preflight_response()

# Register
@app.route(RELAY_BASE_ROUTE + '/register', methods=['POST'])
def register_endpoint():
    app.logger.info('register_endpoint')

    # Check to make sure a wallet address is specified.
    addr = request.json and request.json.get('addr', '').lower()
    if not addr:
        return cors_response(format_error('Missing address')), 400

    try:
        process(addr, app.logger)
    except Exception as e:
        return cors_response(format_error(e)), 400

    return cors_response(format_success())

# Test
@app.route(RELAY_BASE_ROUTE + '/test', methods=['GET'])
def test_endpoint():
    app.logger.info('test_endpoint')

    # Check to make sure a wallet address is specified.
    addr = request.args.get('addr', '').lower()
    if not addr:
        return format_error('Missing address'), 400

    try:
        process(addr, app.logger)
    except Exception as e:
        return format_error(e), 400

    return format_success()

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
