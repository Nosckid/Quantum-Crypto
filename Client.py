import socket
from Crypto import *
import random

# Constants
SERVER_HOST = '127.0.0.1'  # Change this to the server's IP if it's running on a different machine
SERVER_PORT = 5555  # Port number for the TCP connection


# Function to connect to the server and send packets
def tcp_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # Connect to the server
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            total_size = int(client_socket.recv(1024).decode())
            crumbs = [None] * total_size
            attempted_keys = [[] for _ in range(total_size)]
            num_decoded = 0

            while num_decoded < total_size:
                ciphertext = client_socket.recv(1024)
                crumb_idx = num_decoded
                decrypted = False

                # Select a random key from the keys that have not been tried for crumb index crumb_idx
                available_keys = [key for key in keys.values() if key not in attempted_keys[crumb_idx]]
                if not available_keys:
                    continue

                key = random.choice(available_keys)
                attempted_keys[crumb_idx].append(key)

                try:
                    decrypted_text = aes_decrypt(ciphertext, key)
                    if decrypted_text == "The quick brown fox jumps over the lazy dog.":
                        crumbs[crumb_idx] = key
                        num_decoded += 1
                        decrypted = True
                except:
                    continue

                client_socket.sendall(f"{(num_decoded / total_size) * 100:.2f}%".encode())

            with open("received_file.bmp", "wb") as output_file:
                bytes_content = [recompose_byte(crumbs[i:i + 4]) for i in range(0, total_size, 4)]
                output_file.write(bytearray(bytes_content))

        except Exception as e:
            print(f"[ERROR] {e}")


if __name__ == "__main__":
    tcp_client()
