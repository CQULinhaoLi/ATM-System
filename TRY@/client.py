from click import prompt
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
import pywebio.pin as pin
import socket
import threading

# 创建 socket 对象
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 指定服务器端 IP 地址和端口号
server_ip = '192.168.151.169'
port = 12345  # 服务器端口号

# 连接服务
client_socket.connect((server_ip, port))

# 向服务器发送请求


def main_page():
    put_text("欢迎来到ATM系统，请选择功能")
    put_buttons(['登录', '注册'], onclick=[login_page, register_page])


# 登录界面
def login_page():

    data = input_group(
    "请输入用户信息，点击提交",
    [
        input("账号: ", name="username", type="text"),
        input("密码：", name="password", type="password"),
    ],
)
    username = data['username']
    password = data['password']

    # print(username, password)
    put_buttons(['登录', '注册'], onclick=[lambda: login(username, password), register_page])


# 登录函数
def login(username, password):
    # account_number = userdata[]
    # pin = userdata[1]
    request_data = 'login {} {}'.format(username, password)
    client_socket.send(request_data.encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    if response == 'success':
        account_page(username)
    else:
        toast(response, color='Wrong username or password')

# 注册界面
def register_page():
    data = input_group(
    "注册账户",
    [
        input("账号: ", name="username", type="text"),
        input("密码：", name="password", type="password"),
        input("邮箱：", name="email", type="text"),
    ],
)
    account_number = data['username']
    password = data['password']
    email = data['email']
    print(account_number, password, email)
    put_buttons(['注册', '返回登录'], onclick=[lambda: register(account_number, password, email), login_page])


# 注册函数
def register(account_number, password, email):
    # account_number = input("请输入账号：", type=TEXT)
    # pin = input("请输入密码：", type=PASSWORD)
    # email = input("请输入邮箱：", type=TEXT)
    request_data = 'register {} {} {}'.format(account_number, password, email)
    client_socket.send(request_data.encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    if response == 'success':
        toast("注册成功", color='success')
    else:
        toast(response, color='error')


# 账户操作
def handle_action(action, client_socket, username):
    # account_number = input("请输入账号：", type=TEXT)
    account_number = username
    if action == '查询余额':
        request_data = 'balance {}'.format(account_number)
        client_socket.send(request_data.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        put_text("当前余额：" + response)
    elif action == '存款':
        amount = input("请输入存款金额：", type=FLOAT)
        request_data = 'deposit {} {}'.format(account_number, amount)
        client_socket.send(request_data.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        toast(response)
    elif action == '取款':
        amount = input("请输入取款金额：", type=FLOAT)
        request_data = 'withdrawal {} {}'.format(account_number, amount)
        client_socket.send(request_data.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        toast(response)
    elif action == '查询流水':
        request_data = 'transaction_history {}'.format(account_number)
        client_socket.send(request_data.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        put_text("交易记录：" + response)
    elif action == '退出':
        main()
        # pass  # 退出循环


# 账户界面
def account_page(username):
    put_text("请选择操作：")
    put_buttons(['查询余额', '存款', '取款', '查询流水', '退出'], onclick=lambda btn_val: handle_action(btn_val, client_socket, username))
   


# 主函数
def main():
    main_page()
    # login_page()

if __name__ == '__main__':
    main()
