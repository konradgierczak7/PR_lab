import socket
import pickle
import numpy as np
from PIL import Image


def send_all(sock, data):
    data = pickle.dumps(data)
    sock.sendall(len(data).to_bytes(4, byteorder='big'))
    sock.sendall(data)


def receive_all(sock):
    length = int.from_bytes(sock.recv(4), byteorder='big')
    data = b''
    while len(data) < length:
        packet = sock.recv(4096)
        if not packet:
            break
        data += packet
    return pickle.loads(data)


def split_image(image, n):
    arr = np.array(image.convert('L'))
    h = arr.shape[0]
    fragments = []
    for i in range(n):
        start = i * h // n
        end = (i + 1) * h // n
        fragments.append(arr[start:end])
    return fragments


def merge_image(fragments):
    h = sum(f.shape[0] for f in fragments)
    w = fragments[0].shape[1]
    result = np.zeros((h, w), dtype=np.uint8)
    y = 0
    for f in fragments:
        result[y:y + f.shape[0]] = f
        y += f.shape[0]
    return Image.fromarray(result)


def server_main(image_path, n_fragments):
    image = Image.open(image_path)
    fragments = split_image(image, n_fragments)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 2040))
    server_socket.listen(1)
    print("Serwer nasłuchuje...")
    processed_fragments = []
    for i in range(n_fragments):
        client_socket, client_adress = server_socket.accept()
        print(f"Połączono z klientem {i+1}: {client_adress}")
        send_all(client_socket, fragments[i])
        print(f"Wysłano fragment {i+1} do klienta")
        processed_fragment = receive_all(client_socket)
        print(f"Otrzymano przetworzony fragment {i+1} od klienta")
        processed_fragments.append(processed_fragment)
        print(f"Zamknięto połączenie z klientem {i+1}")
        client_socket.close()
    print("Wszystkie fragmenty przetworzone, łączenie fragmentów...")
    result_image = merge_image(processed_fragments)
    print("Zapisanie przetworzonego obrazu jako processed_image.png...")
    result_image.save("processed_image.png")
    print("Obraz przetworzony zapisany jako processed_image.png")


if __name__ == '__main__':
    server_main('PR_lab\\PR_lab3\\zad2\\obraz.jpg', 4) 