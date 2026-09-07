import socket
import http.server
import urllib.parse
import re


def parse_headers(request_data):
    lines = request_data.decode('utf-8', errors='ignore').split('\r\n')
    if not lines:
        return None, [], {}

    first_line = lines[0].split(' ')
    if len(first_line) < 3:
        return None, [], {}

    method = first_line[0]
    path = first_line[1]

    headers = {}
    for line in lines[1:]:
        if line == '':
            break
        if ': ' in line:
            key, value = line.split(': ', 1)
            headers[key] = value

    return method, path, headers


def get_status_code(path):
    parsed = urllib.parse.urlparse(path)
    params = urllib.parse.parse_qs(parsed.query)

    if 'status' in params and params['status']:
        status = params['status'][0]
        try:
            code = int(status)
            if 100 <= code <= 599:  # Проверяем, что код валидный
                return code
        except ValueError:
            pass
    return 200


def get_status_phrase(code):
    phrases = {
        200: 'OK',
        201: 'Created',
        204: 'No Content',
        301: 'Moved Permanently',
        302: 'Found',
        304: 'Not Modified',
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        408: 'Request Timeout',
        500: 'Internal Server Error',
        501: 'Not Implemented',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        504: 'Gateway Timeout'
    }
    return phrases.get(code, 'OK')


def handle_client(client_socket, addr):
    try:
        request_data = client_socket.recv(4096)
        if not request_data:
            return

        method, path, headers = parse_headers(request_data)
        if method is None:
            return

        status_code = get_status_code(path)
        status_phrase = get_status_phrase(status_code)

        response_body_lines = [
            f'Request Method: {method}',
            f'Request Source: {addr}',
            f'Response Status: {status_code} {status_phrase}'
        ]

        for key, value in headers.items():
            response_body_lines.append(f'{key}: {value}')

        response_body = '\r\n'.join(response_body_lines)

        response = (
            f'HTTP/1.1 {status_code} {status_phrase}\r\n'
            f'Content-Type: text/plain\r\n'
            f'Content-Length: {len(response_body)}\r\n'
            f'Connection: close\r\n'
            f'\r\n'
            f'{response_body}'
        )

        client_socket.send(response.encode('utf-8'))

    except Exception as e:
        print(f"Ошибка обработки клиента: {e}")
    finally:
        client_socket.close()


def run_server(host='127.0.0.1', port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Сервер запущен на {host}:{port}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            handle_client(client_socket, addr)
    except KeyboardInterrupt:
        print("\nСервер остановлен")
    finally:
        server_socket.close()


if __name__ == "__main__":
    run_server()