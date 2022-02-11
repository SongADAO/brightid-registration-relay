from flask import make_response

# CORS Preflight
def cors_preflight_response():
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response

# CORS
def cors_response(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
