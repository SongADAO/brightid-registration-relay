import json
from flask import Flask, request, jsonify

from config import *
from cors import *
from relay import *

app = Flask(__name__)

def format_error(e):
    if ("'code'" in str(e)) & ("'message'" in str(e)):
        errorJsonStr = str(e).replace("'", '"')
        errorJson = json.loads(errorJsonStr)

        app.logger.info(errorJson['code'])
        app.logger.info(errorJson['message'])
        app.logger.info(errorJson)
        app.logger.info('code' in errorJson)
        app.logger.info('message' in errorJson)

        if ('code' in errorJson) and ('message' in errorJson):
            return jsonify({'success': False, 'error': {'code': errorJson['code'], 'message': errorJson['message']}})

    if ('code' in e) and ('message' in e):
        return jsonify({'success': False, 'error': {'code': e['code'], 'message': e['message']}})

    if ('message' in e):
        return jsonify({'success': False, 'error': {'code': 0, 'message': e['message']}})

    return jsonify({'success': False, 'error': {'code': 0, 'message': str(e)}})

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
