import json
import sys
import time
import tkinter as tk
import socket
import threading
from tkinter import ttk


class Client:
    def __init__(self, app_callback):
        self.app_callback = app_callback
        self.host = '127.0.0.1'
        self.port = 8081
        self.token = None

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

        threading.Thread(target=self.listen, daemon=True).start()

        print(f"Connected to {self.host}:{self.port}")


    def listen(self):
        try:
            while True:
                response = self.client_socket.recv(1024)
                if not response:
                    self.reconnect_server()
                    print("Server closed the connection.")
                    break
                response_data = json.loads(response.decode('utf-8'))
                self.app_callback(response_data)
        except ConnectionAbortedError:
            print("Connection Aborted Error.")
        except ConnectionResetError:
            print("Server disconnected unexpectedly.")
    def receive_message(self):
        # Receive the server's response
        response = self.client_socket.recv(1024)
        print(f"Server response: {response.decode('utf-8')}")
        return response

    def reconnect_server(self):
        self.client_socket.close()
        while True:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.host, self.port))
                print("Reconnected to the server.")
                break
            except Exception as e:
                print(f"Reconnection failed: {e}")
                time.sleep(1)

    def close_socket(self):
        self.client_socket.close()


class Application(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("Chat App")
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Use a modern theme

        self.bg_color = "#F0F0F0"  # Light gray
        self.text_color = "#333333"  # Dark gray
        self.button_color = "#4CAF50"  # Soft green
        self.entry_bg_color = "#FFFFFF"  # White
        self.entry_fg_color = "#333333"  # Dark gray

        self.style.configure("TButton", background=self.button_color, foreground=self.text_color,
                             font=("Helvetica", 12))
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Helvetica", 12))
        self.style.configure("TEntry", background=self.entry_bg_color, foreground=self.entry_fg_color,
                             font=("Helvetica", 12))
        self.master.configure(bg=self.bg_color)

        # Calculate the screen width and height
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        # Set the window size and position it in the center of the screen
        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.5)
        # Calculate the center coordinates
        center_x = int(window_width / 2)
        center_y = int(window_height / 2)
        self.master.geometry(
            f"{window_width}x{window_height}+{center_x - int(window_width / 2)}+{center_y - int(window_height / 2)}")
        self.button_style = {"font": ("Helvetica", 12), "padx": 10, "pady": 5}
        self.username_entry = None  # Initialize to None
        self.password_entry = None
        self.confirm_password_entry = None
        self.create_startup_screen()
        self.pack(expand=True, fill="both")
        self.client_instance = Client(self.handle_server_response)

    def quit(self):
        self.destroy()
        sys.exit()

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.create_startup_screen()

    def handle_server_response(self, response_data):
        """
        Handle the server response. Update the GUI based on the response data.

        Parameters:
        response_data (dict): A dictionary containing the server's response.
        """
        if response_data.get("status") == "success":
            # Store the token if it's in the response
            if "token" in response_data:
                self.client_instance.token = response_data["token"]
                print(f"Token received: {self.client_instance.token}")
            self.main_app()
        elif response_data.get("type") == "signup":
            self.main_app()
        elif response_data.get("type") == "message":
            print("Message received")
        # Add more elif blocks for other types of responses
        else:
            print("Unknown response type:", response_data)

    def receive_and_handle_message(self):
        while True:
            try:
                response = self.client_instance.client_socket.recv(1024)
                if not response:
                    break  # Connection closed by the server
                response_data = json.loads(response.decode('utf-8'))
                self.handle_server_response(response_data)
            except Exception as e:
                print(f"Error handling server response: {e}")
                break  # Stop the loop on errors

    def sign_up(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        fields = [username, password, confirm_password]

        if password != confirm_password:
            print("Passwords do not match")
        elif all(field == '' for field in fields):
            print("Fields can't be empty")
        else:
            # Send a sign-up request to the server
            self.request_data = {
                "request_type": "signup",
                "username": username,
                "password": password
            }
            request_json = json.dumps(self.request_data).encode('utf-8')
            print(f"Sending JSON request: {request_json}")
            self.client_instance.client_socket.send(request_json)

    def sign_in(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        fields = [username, password]

        if all(field == '' for field in fields):
            print("Fields can't be empty")
        else:
            # Correct request_type for sign-in
            self.request_data = {
                "request_type": "signin",
                "username": username,
                "password": password
            }
            request_json = json.dumps(self.request_data).encode('utf-8')
            print(f"Sending JSON request: {request_json}")
            self.client_instance.client_socket.send(request_json)

    def create_signin_screen(self):
        self.clear_frame()
        sign_in_frame = ttk.Frame(self)
        sign_in_frame.pack(expand=True, fill="both")

        username_label = ttk.Label(sign_in_frame, text="Username:")
        username_label.pack(padx=10, pady=5)

        self.username_entry = ttk.Entry(sign_in_frame, width=30)
        self.username_entry.pack(padx=10, pady=5)

        password_label = ttk.Label(sign_in_frame, text="Password:")
        password_label.pack(padx=10, pady=5)

        self.password_entry = ttk.Entry(sign_in_frame, show="*", width=30)
        self.password_entry.pack(padx=10, pady=5)

        sign_in_button = ttk.Button(sign_in_frame, text="Sign In", command=self.sign_in)
        sign_in_button.pack(anchor="center", pady=(10, 0))

        back_button = ttk.Button(sign_in_frame, text="Back", command=self.main_menu)
        back_button.pack(anchor="center", pady=(10, 0))

        quit_button = ttk.Button(sign_in_frame, text="Quit", command=self.quit)
        quit_button.pack(anchor="center", pady=(10, 0))

    def create_signup_screen(self):
        self.clear_frame()
        sign_up_frame = ttk.Frame(self)
        sign_up_frame.pack(expand=True, fill="both")

        username_label = ttk.Label(sign_up_frame, text="Username:")
        username_label.pack(padx=10, pady=5)

        self.username_entry = ttk.Entry(sign_up_frame, width=30)
        self.username_entry.pack(padx=10, pady=5)

        password_label = ttk.Label(sign_up_frame, text="Password:")
        password_label.pack(padx=10, pady=5)

        self.password_entry = ttk.Entry(sign_up_frame, show="*", width=30)
        self.password_entry.pack(padx=10, pady=5)

        confirm_password_label = ttk.Label(sign_up_frame, text="Confirm password:")
        confirm_password_label.pack(padx=10, pady=5)

        self.confirm_password_entry = ttk.Entry(sign_up_frame, show="*", width=30)
        self.confirm_password_entry.pack(padx=10, pady=5)

        sign_up_button = ttk.Button(sign_up_frame, text="Sign Up", command=self.sign_up)
        sign_up_button.pack(anchor="center", pady=(10, 0))

        back_button = ttk.Button(sign_up_frame, text="Back", command=self.main_menu)
        back_button.pack(anchor="center", pady=(10, 0))

        quit_button = ttk.Button(sign_up_frame, text="Quit", command=self.quit)
        quit_button.pack(anchor="center", pady=(10, 0))

    def create_startup_screen(self):
        self.clear_frame()
        startup_frame = ttk.Frame(self)
        startup_frame.pack(expand=True, fill="both")

        welcome_label = ttk.Label(startup_frame, text="Welcome to Messenger App", font=("Helvetica", 16, "bold"))
        welcome_label.pack(pady=20)

        sign_in_button = ttk.Button(startup_frame, text="Sign In", command=self.create_signin_screen)
        sign_up_button = ttk.Button(startup_frame, text="Sign Up", command=self.create_signup_screen)
        quit_button = ttk.Button(startup_frame, text="Quit", command=self.quit)

        sign_in_button.pack(anchor='center', pady=(10, 0))
        sign_up_button.pack(anchor='center', pady=(10, 0))
        quit_button.pack(anchor="center", pady=(10, 0))

    def print_token(self):
        print(self.client_instance.token)

    def main_app(self):
        self.clear_frame()
        main_app_frame = ttk.Frame(self)
        main_app_frame.pack(expand=True, fill="both")
        main_app_frame.grid_rowconfigure(0, weight=1)
        main_app_frame.grid_columnconfigure(0, weight=1)
        main_app_frame.grid_columnconfigure(1, weight=3)

        # Sidebar
        sidebar = ttk.Frame(main_app_frame, relief="sunken")
        sidebar.grid(row=0, column=0, sticky="ns")
        for i in range(5):  # Adjust the range for the number of rows you need
            sidebar.grid_rowconfigure(i, weight=1)

        # Adding buttons to the sidebar
        sidebar_buttons = ["Sidebar Button 1", "Sidebar Button 2", "Sidebar Button 3", "Sidebar Button 4"]
        for i, button_text in enumerate(sidebar_buttons):
            button = ttk.Button(sidebar, text=button_text, command=None)  # Replace None with actual commands
            button.grid(row=i, column=0, padx=10, pady=10, sticky="ew")

        # Sign Out button at the bottom of the sidebar
        signout_button = ttk.Button(sidebar, text="Sign Out", command=self.main_menu)
        signout_button.grid(row=5, column=0, padx=10, pady=10, sticky="ew")

        # Message area
        message_area = ttk.Frame(main_app_frame, relief="sunken")
        message_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        message_area.grid_rowconfigure(0, weight=1)
        message_area.grid_columnconfigure(0, weight=1)

        # Example content inside the message area
        label = ttk.Label(message_area, text="Message Frame Content", font=("Helvetica", 12))
        label.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        # Message input bar
        message_bar = ttk.Frame(main_app_frame)
        message_bar.grid(row=1, column=1, sticky="ew")
        message_box = tk.Text(message_bar, height=2)  # Text widget remains tk
        message_box.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        send_button = ttk.Button(message_bar, text="Send")
        send_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")


if __name__ == "__main__":
    root = tk.Tk()
    myapp = Application(root)
    myapp.mainloop()
