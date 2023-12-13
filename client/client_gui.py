import json
import sys
import time
import tkinter as tk
import socket
import threading


class Client:
    def __init__(self):

        self.host = '127.0.0.1'
        self.port = 8081
        # Create a socket object
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        self.client_socket.connect((self.host, self.port))
        threading.Thread(target=self.listen, daemon=True).start()

        print(f"Connected to {self.host}:{self.port}")


    def listen(self):
        try:
            while True:
                # Receive data from the server
                response = self.client_socket.recv(1024)
                if not response:
                    # Connection closed by the server
                    print("Server closed the connection.")
                    break

                print(f"Received data: {response.decode('utf-8')}")

                # You can add your logic to process the received message here

        except ConnectionAbortedError:
            print("Connection Aborted Error.")
        except ConnectionResetError:
            print("Server disconnected unexpectedly.")
    def send_hello(self):
        message = "Hello from the client!"
        self.client_socket.send(message.encode('utf-8'))

    def receive_message(self):
        # Receive the server's response
        response = self.client_socket.recv(1024)
        print(f"Server response: {response.decode('utf-8')}")

    # Close the socket
    def close_socket(self):
        self.client_socket.close()


class Application(tk.Frame):

    def quit(self):
        self.destroy()
        sys.exit()

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.create_startup_screen()

    def __init__(self, master):
        super().__init__(master)
        self.client_instance = Client()
        self.master = master
        self.master.title("Chat App")
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
            time.sleep(0.1)
            request_json = json.dumps(self.request_data).encode('utf-8')
            print(f"Sending JSON request: {request_json}")
            self.client_instance.client_socket.send(request_json)
            self.main_app()

        print("Sign up called")

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
            self.main_app()

    def create_signin_screen(self):

        self.clear_frame()
        # Create a new frame for the sign-in screen
        sign_in_frame = tk.Frame(self)
        sign_in_frame.pack(expand=True)

        # Create and configure widgets for the sign-in screen
        username_label = tk.Label(sign_in_frame, text="Username:")
        username_label.pack(padx=10, pady=5)

        self.username_entry = tk.Entry(sign_in_frame, width=30)
        self.username_entry.pack(padx=10, pady=5)

        password_label = tk.Label(sign_in_frame, text="Password:")
        password_label.pack(padx=10, pady=5)

        self.password_entry = tk.Entry(sign_in_frame, show="*", width=30)
        self.password_entry.pack(padx=10, pady=5)

        sign_in_button = tk.Button(sign_in_frame, text="Sign In", command=self.sign_in, **self.button_style)
        sign_in_button.pack(anchor="center", pady=(10, 0))

        back_button = tk.Button(sign_in_frame, text="Back", command=self.main_menu, **self.button_style)
        back_button.pack(anchor="center", pady=(10, 0))

        quit_button = tk.Button(sign_in_frame, text="Quit", command=self.quit, **self.button_style)
        quit_button.pack(anchor="center", pady=(10, 0))

    def create_signup_screen(self):
        self.clear_frame()

        # Create a new frame for the sign-up screen
        sign_up_frame = tk.Frame(self)
        sign_up_frame.pack(expand=True)

        # Create and configure widgets for the sign-up screen
        username_label = tk.Label(sign_up_frame, text="Username:")
        username_label.pack(padx=10, pady=5)

        self.username_entry = tk.Entry(sign_up_frame, width=30)
        self.username_entry.pack(padx=10, pady=5)

        password_label = tk.Label(sign_up_frame, text="Password:")
        password_label.pack(padx=10, pady=5)

        self.password_entry = tk.Entry(sign_up_frame, show="*", width=30)
        self.password_entry.pack(padx=10, pady=5)

        confirm_password_label = tk.Label(sign_up_frame, text="Confirm password:")
        confirm_password_label.pack(padx=10, pady=5)

        self.confirm_password_entry = tk.Entry(sign_up_frame, show="*", width=30)
        self.confirm_password_entry.pack(padx=10, pady=5)

        sign_up_button = tk.Button(sign_up_frame, text="Sign Up", command=self.sign_up, **self.button_style)
        sign_up_button.pack(anchor="center", pady=(10, 0))

        back_button = tk.Button(sign_up_frame, text="Back", command=self.main_menu, **self.button_style)
        back_button.pack(anchor="center", pady=(10, 0))

        quit_button = tk.Button(sign_up_frame, text="Quit", command=self.quit, **self.button_style)
        quit_button.pack(anchor="center", pady=(10, 0))

    def create_startup_screen(self):
        self.clear_frame()
        startup_frame = tk.Frame(self, background="#b6b9de")
        startup_frame.pack(expand=True, fill="both")
        # Create and configure widgets
        welcome_label = tk.Label(startup_frame, text="Welcome to Messenger App", font=("Helvetica", 16, "bold"))
        welcome_label.pack(pady=20)

        sign_in_button = tk.Button(startup_frame, text="Sign In", command=self.create_signin_screen,
                                   **self.button_style)
        sign_up_button = tk.Button(startup_frame, text="Sign Up", command=self.create_signup_screen,
                                   **self.button_style)
        quit_button = tk.Button(startup_frame, text="Quit", command=self.quit,
                                **self.button_style)

        sign_in_button.pack(anchor='center', pady=(10, 0))
        sign_up_button.pack(anchor='center', pady=(10, 0))
        quit_button.pack(anchor="center", pady=(10, 0))

    def main_app(self):
        self.clear_frame()

        # Create a new frame for the main app screen
        main_app_frame = tk.Frame(self, background="#363c7d")
        main_app_frame.pack(expand=True, fill="both")
        main_app_frame.grid_rowconfigure(0, weight=1)
        main_app_frame.grid_columnconfigure(0, weight=1)
        main_app_frame.grid_columnconfigure(1, weight=1)

        message = tk.Frame(main_app_frame, relief="sunken", background="#b6b9de")
        message.grid(row=0, column=1, sticky="nsew")
        # Example content inside the message frame
        label = tk.Label(message, text="Message Frame Content", font=("Helvetica", 12), pady=10)
        label.pack()
        label1 = tk.Label(message, text="Message Frame Content", font=("Helvetica", 12), pady=10)
        label1.pack()
        label2 = tk.Label(message, text="Message Frame Content", font=("Helvetica", 12), pady=10)
        label2.pack()
        label3 = tk.Label(message, text="Message Frame Content", font=("Helvetica", 12), pady=10)
        label3.pack()
        # Create and configure widgets for the main app screen
        message_bar = tk.Frame(main_app_frame, relief="sunken")
        message_bar.grid(row=1, column=1, sticky="nsew")
        message_box = tk.Text(message_bar, height=1)
        message_box.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        send_button = tk.Button(message_bar, text="Send")
        send_button.grid(row=1, column=2)

        # Example of a button in the sidebar
        sidebar = tk.Frame(main_app_frame, bd=1, relief="sunken")  # Add border and relief
        sidebar.grid(row=0, column=0, padx=10, pady=10, sticky="nsw")
        signout_button = tk.Button(main_app_frame, text="Sign Out", command=self.main_menu, **self.button_style)
        signout_button.grid(row=1, column=0, padx=10, pady=10)

        sidebar_button = tk.Button(sidebar, text="Sidebar Button", command=None,
                                   **self.button_style)
        sidebar_button.pack(pady=(10, 0))
        sidebar_button = tk.Button(sidebar, text="Sidebar Button", command=None, **self.button_style)
        sidebar_button.pack(pady=(10, 0))
        sidebar_button = tk.Button(sidebar, text="Sidebar Button", command=None,
                                   **self.button_style)
        sidebar_button.pack(pady=(10, 0))
        sidebar_button = tk.Button(sidebar, text="Sidebar Button", command=None,
                                   **self.button_style)
        sidebar_button.pack(pady=(10, 0))
        sidebar_button = tk.Button(sidebar, text="Sidebar Button", command=None,
                                   **self.button_style)
        sidebar_button.pack(pady=(10, 0))
        sidebar_button = tk.Button(sidebar, text="Sidebar Button", command=None,
                                   **self.button_style)
        sidebar_button.pack(pady=(10, 0))


if __name__ == "__main__":
    root = tk.Tk()
    myapp = Application(root)
    myapp.mainloop()
