import requests
import socket

print("=== Тест через requests ===")
headers = {
    'User-Agent': 'MyTestAgent/1.0',
    'Accept': 'text/html',
    'Custom-Header': 'MyValue',
    'X-Test-Header': '12345'
}

response = requests.get('http://127.0.0.1:5000', headers=headers)
print("Статус ответа:", response.status_code)
print("Тело ответа:")
print(response.text)
print("\nВсе заголовки клиента в ответе:")
for header_name in headers:
    if header_name in response.text:
        print(f"✅ {header_name} найден")
    else:
        print(f"❌ {header_name} НЕ найден")

print("\n=== Тест через сокет (проверка валидности HTTP ответа) ===")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 5000))

request = """GET / HTTP/1.1
Host: 127.0.0.1:5000
User-Agent: SocketTest/1.0
X-Custom: TestValue
Accept: */*

"""

sock.send(request.encode())

response_data = sock.recv(4096).decode()
sock.close()

print("Полный HTTP ответ:")
print("=" * 50)
print(response_data)
print("=" * 50)


lines = response_data.split('\r\n')
print("\nПроверка валидности HTTP ответа:")
print(f"✅ Статусная строка: {lines[0]}")
print(f"✅ Заголовки: {len([l for l in lines[1:] if l and ': ' in l])} заголовков")
print(f"✅ Тело ответа начинается после пустой строки")


for header in ['User-Agent: SocketTest/1.0', 'X-Custom: TestValue']:
    if header in response_data:
        print(f"✅ {header} найден в теле ответа")
    else:
        print(f"❌ {header} НЕ найден в теле ответа")