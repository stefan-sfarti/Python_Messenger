import json
import socket
import threading

USER_DATA_FILE = "user_data.json"
def handle_client(client_socket):
    try:
        while True:
            # Receive data from the client
            request = client_socket.recv(1024)
            print(request)
            if not request:
                # Connection closed by the client
                print("Client closed the connection.")
                break

            data = json.loads(request.decode('utf-8'))

            if data.get("request_type") == "signup":
                username = data.get("username")
                password = data.get("password")

                # Perform basic validation (you may want to enhance this)
                if username and password:
                    # Store user data in the JSON file
                    store_user_data(username, password)
                    response = "Signup successful!"
                else:
                    response = "Invalid signup request. Username and password are required."
                # Send a response back to the client
                client_socket.send(response.encode('utf-8'))
    except ConnectionResetError:
        print("Client disconnected unexpectedly.")
    finally:
        # Close the client socket
        client_socket.close()

def store_user_data(username, password):
    try:
        with open(USER_DATA_FILE, 'r') as file:
            user_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        user_data = {}
    # Store new user data
    user_data[username] = {"password": password}

    # Save the updated user data to the JSON file
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(user_data, file)
def start_server():
    # Set the server host and port
    host = '127.0.0.1'
    port = 8081

    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_socket.bind((host, port))

    # Listen for incoming connections (up to 5 connections in the queue)
    server_socket.listen(10)
    print(f"Server listening on {host}:{port}")

    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        # Create a new thread to handle the client
        client_handler = threading.Thread(target=handle_client, args=(client_socket,), daemon=True)
        client_handler.start()

if __name__ == "__main__":
    start_server()
