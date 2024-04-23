# import json
import socket
import threading
import tkinter as tk

# 创建 socket 对象
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 指定服务器端 IP 地址和端口号
server_ip = '192.168.151.169'
# host = socket.gethostname()
# server_ip = host
port = 12345  # 服务器端口号

# 连接服务
client_socket.connect((server_ip, port))

# 向服务器发送请求

# 登录界面
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # 标签和输入框
        self.account_label = tk.Label(self, text="账号：")
        self.account_label.grid(row=0, column=0)
        self.account_entry = tk.Entry(self)
        self.account_entry.grid(row=0, column=1)
        
        self.pin_label = tk.Label(self, text="密码：")
        self.pin_label.grid(row=1, column=0)
        self.pin_entry = tk.Entry(self, show="*")
        self.pin_entry.grid(row=1, column=1)
        
        # 登录和注册按钮
        self.login_button = tk.Button(self, text="登录", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2)
        
        self.register_button = tk.Button(self, text="注册", command=lambda: controller.show_frame(RegisterPage))
        self.register_button.grid(row=3, column=0, columnspan=2)
    
    # 登录函数
    def login(self):
        account_number = self.account_entry.get()
        pin = self.pin_entry.get()
        request_data = 'login {} {}'.format(account_number, pin)
        client_socket.send(request_data.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        if response == 'success':
            self.controller.show_frame(AccountPage)
        else:
            self.login_status_label = tk.Label(self, text=response, fg='red')
            self.login_status_label.grid(row=4, column=0, columnspan=2)

# 注册界面
class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # 标签和输入框
        self.account_label = tk.Label(self, text="账号：")
        self.account_label.grid(row=0, column=0)
        self.account_entry = tk.Entry(self)
        self.account_entry.grid(row=0, column=1)
        
        self.pin_label = tk.Label(self, text="密码：")
        self.pin_label.grid(row=1, column=0)
        self.pin_entry = tk.Entry(self, show="*")
        self.pin_entry.grid(row=1, column=1)
        
        self.email_label = tk.Label(self, text="邮箱：")
        self.email_label.grid(row=2, column=0)
        self.email_entry = tk.Entry(self)
        self.email_entry.grid(row=2, column=1)
        
        # 注册按钮
        self.register_button = tk.Button(self, text="注册", command=self.register)
        self.register_button.grid(row=3, column=0, columnspan=2)
        
        # 返回登录界面按钮
        self.back_button = tk.Button(self, text="返回登录", command=lambda: controller.show_frame(LoginPage))
        self.back_button.grid(row=4, column=0, columnspan=2)
    
    # 注册函数
    def register(self):
        account_number = self.account_entry.get()
        pin = self.pin_entry.get()
        email = self.email_entry.get()
        request_data = 'register {} {} {}'.format(account_number, pin, email)
        client_socket.send(request_data.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        self.register_status_label = tk.Label(self, text=response, fg='red')
        self.register_status_label.grid(row=5, column=0, columnspan=2)

# 账户界面
class AccountPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # 查询余额按钮
        self.balance_button = tk.Button(self, text="查询余额", command=self.get_balance)
        self.balance_button.grid(row=0, column=0)
        self.balance_label = tk.Label(self, text="")
        self.balance_label.grid(row=1, column=0)
        
        # 存款按钮和输入框
        self.deposit_button = tk.Button(self, text="存款", command=self.deposit)
        self.deposit_button.grid(row=2, column=0)
        self.amount_deposit_label = tk.Label(self, text="存款金额：")
        self.amount_deposit_label.grid(row=3, column=0)
        self.amount_deposit_entry = tk.Entry(self)
        self.amount_deposit_entry.grid(row=3, column=1)
        self.deposit_status_label = tk.Label(self, text="")
        self.deposit_status_label.grid(row=4, column=0, columnspan=2)
        
        # 取款按钮和输入框
        self.withdrawal_button = tk.Button(self, text="取款", command=self.withdrawal)
        self.withdrawal_button.grid(row=5, column=0)
        self.amount_withdrawal_label = tk.Label(self, text="取款金额：")
        self.amount_withdrawal_label.grid(row=6, column=0)
        self.amount_withdrawal_entry = tk.Entry(self)
        self.amount_withdrawal_entry.grid(row=6, column=1)
        self.withdrawal_status_label = tk.Label(self, text="")
        self.withdrawal_status_label.grid(row=7, column=0, columnspan=2)
        
        # 查询流水按钮
        self.transaction_history_button = tk.Button(self, text="查询流水", command=self.get_transaction_history)
        self.transaction_history_button.grid(row=8, column=0)
        self.transaction_history_label = tk.Label(self, text="")
        self.transaction_history_label.grid(row=9, column=0)
    
    # 查询余额函数
    def get_balance(self):
        account_number = self.controller.account_number
        request_data = 'balance {}'.format(account_number)
        client_socket.send(request_data.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        self.balance_label.config(text="当前余额：" + response)
    
    # 存款函数
    def deposit(self):
        account_number = self.controller.account_number
        amount = self.amount_deposit_entry.get()
        request_data = 'deposit {} {}'.format(account_number, amount)
        client_socket.send(request_data.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        self.deposit_status_label.config(text=response)
    
    # 取款函数
    def withdrawal(self):
        account_number = self.controller.account_number
        amount = self.amount_withdrawal_entry.get()
        request_data = 'withdrawal {} {}'.format(account_number, amount)
        client_socket.send(request_data.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        self.withdrawal_status_label.config(text=response)
    
    # 查询流水函数
    def get_transaction_history(self):
        account_number = self.controller.account_number
        request_data = 'transaction_history {}'.format(account_number)
        client_socket.send(request_data.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        self.transaction_history_label.config(text="交易记录：" + response)

# 主程序
class ATMApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        # 设置窗口
        self.title("ATM 客户端")
        self.geometry("400x300")
        
        # 创建容器
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # 保存账户号
        self.account_number = None
        
        # 创建页面
        self.frames = {}
        for F in (LoginPage, RegisterPage, AccountPage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # 显示登录页面
        self.show_frame(LoginPage)
        
        # 启动消息接收线程
        self.receive_thread = threading.Thread(target=self.receive_message)
        self.receive_thread.daemon = True
        self.receive_thread.start()
    
    # 显示页面函数
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
    
    # 接收消息函数
    def receive_message(self):
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            # 在这里对接收到的消息进行处理，可以根据消息内容更新界面或进行其他操作
            print("Received:", message)

app = ATMApp()
app.mainloop()



# 接收服务端消息
msg = client_socket.recv(1024)
print(msg.decode('utf-8'))

# 关闭连接
client_socket.close()

