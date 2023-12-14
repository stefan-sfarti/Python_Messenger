import json
import socket
import threading
import hashlib
import secrets

user_data_lock = threading.Lock()
USER_DATA_FILE_PATH = "user_data.json"
# Load user data from the JSON file
with user_data_lock:
    try:
        with open(USER_DATA_FILE_PATH, 'r') as file:
            USER_DATA_FILE = json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, initialize an empty dictionary
        USER_DATA_FILE = {}
    user_tokens = {}
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
                if username and password:
                    # Check if the username already exists
                    if username in USER_DATA_FILE:
                        response = {"status": "error", "message": "Username already exists."}
                    else:
                        # Hash the password
                        hashed_password = hash_password(password)
                        # Save the hashed password in the user data file
                        USER_DATA_FILE[username] = hashed_password
                        # Save the updated user data to the JSON file
                        with open(USER_DATA_FILE_PATH, 'w') as file:
                            json.dump(USER_DATA_FILE, file)
                        # Generate a token
                        token = generate_token()
                        # Store the token on the server (you might want to use a database for this)
                        # For simplicity, I'll store it in a dictionary
                        user_tokens[username] = token
                        response = {"status": "success", "token": token}
                else:
                    response = {"status": "error", "message": "Username and password are required."}

                # Send the response to the client
                client_socket.send(json.dumps(response).encode('utf-8'))
            elif data.get("request_type") == "signin":
                username = data.get("username")
                password = data.get("password")
                if username and password:
                    hashed_password = hash_password(password)
                    if username in USER_DATA_FILE and USER_DATA_FILE[username] == hashed_password:
                        # Generate a token
                        token = generate_token()
                        # Store the token on the server (you might want to use a database for this)
                        # For simplicity, I'll store it in a dictionary
                        user_tokens[username] = token
                        response = {"status": "success", "token": token}
                    else:
                        response = {"status": "error", "message": "Invalid username or password."}
                else:
                    response = {"status": "error", "message": "Username and password are required."}
            client_socket.send(json.dumps(response).encode('utf-8'))
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

# Function to generate a random token
def generate_token():
    return secrets.token_hex(16)

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
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
