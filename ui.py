import tkinter as tk
from tkinter import messagebox
import json
import socket

class ATMClientUI:
    def __init__(self, master):
        self.master = master
        master.title("ATM Client")

        self.label_account = tk.Label(master, text="Account Number:")
        self.label_account.grid(row=0, column=0, sticky=tk.E)

        self.entry_account = tk.Entry(master)
        self.entry_account.grid(row=0, column=1)

        self.label_pin = tk.Label(master, text="PIN:")
        self.label_pin.grid(row=1, column=0, sticky=tk.E)

        self.entry_pin = tk.Entry(master, show="*")
        self.entry_pin.grid(row=1, column=1)

        self.login_button = tk.Button(master, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

    def login(self):
        account_number = self.entry_account.get()
        pin = self.entry_pin.get()

        data = {
            'type': 'login',
            'account_number': account_number,
            'pin': pin
        }

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect(('127.0.0.1', 1111))
                client_socket.sendall(json.dumps(data).encode())
                response = client_socket.recv(1024)
                response_data = json.loads(response.decode())

                if response_data['status'] == 'success':
                    messagebox.showinfo("Success", response_data['message'])
                    # Open new window or perform further actions upon successful login
                else:
                    messagebox.showerror("Error", response_data['message'])

        except Exception as e:
            messagebox.showerror("Error", "An error occurred: {}".format(e))

def main():
    root = tk.Tk()
    app = ATMClientUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
