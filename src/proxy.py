from flask import Flask, jsonify, request, make_response, Response
import requests
from werkzeug.contrib.cache import SimpleCache
import json

app = Flask('__name__')
cache = SimpleCache()
API_MERCADOLIBRE_URL = 'https://api.mercadolibre.com/'
MAX_REQUESTS = 20

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    request_amount = cache.get(request.remote_addr)

    # si la key(ip) existe en la cache y alcanzo el limite devuelvo too many requests (429)
    if request_amount is not None and request_amount >= MAX_REQUESTS:
        return make_response(jsonify({"error" : "too_many_requests", "status": 429}), 429)
    # si la key(ip) existe en la cache y no llego al limite entonces le sumo uno
    elif request_amount is not None:
        request_amount += 1
        cache.set(request.remote_addr, request_amount, timeout=20)
        # si la key(ip) no existe en la cache, la creo
    else:
        cache.set(request.remote_addr, 1, timeout=20)
    
    url = '{0}{1}'.format(API_MERCADOLIBRE_URL, path)
   
    resp = requests.request(method=request.method,
                                url=url,
                                headers={key : value for (key, value) in request.headers if key != 'Host'},
                                data=request.get_data())

    response = Response(resp.content, resp.status_code, resp.raw.headers.items())
    return response

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080)
