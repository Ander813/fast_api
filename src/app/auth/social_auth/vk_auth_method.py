from authlib.common.urls import add_params_to_uri, add_params_to_qs


def client_secret_get(client, method, uri, headers, body):
    if method == 'GET':
        uri = add_params_to_uri(uri, [('client_id', client.client_id),
                                      ('client_secret', client.client_secret)])
        return uri, headers, body
    body = add_params_to_qs(body, [('client_id', client.client_id),
                                   ('client_secret', client.client_secret)])
    if 'Content-Length' in headers:
        headers['Content-Length'] = str(len(body))
    return uri, headers, body