from click import prompt
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
import socket
import select
import struct
import os
import time

import threading

# from TRY1.client import RegisterPage

# 创建 socket 对象
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 指定服务器端 IP 地址和端口号
server_ip = '192.168.137.1'
port = 12345  # 服务器端口号

# 连接服务
client_socket.connect((server_ip, port))

# 向服务器发送请求


def main_page():
    # global client_socket
    # if 'client_socket' in globals():
    #     client_socket.close()
    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client_socket.connect((server_ip, port))
    clear()
    put_text("欢迎来到ATM系统,请选择功能")
    put_buttons(['登录', '注册'], onclick=[login_page, register_page])


# 登录界面
def login_page():
    clear()
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
    put_buttons(['确定登录', '重新输入信息'], onclick=[lambda: login(username, password), main_page])


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
        put_text("登录失败" + response)
        put_buttons(['退出'], onclick=[main_page])


# # 退出登录函数
# def logout(client_socket):
#     # client_socket.send('logout'.encode('utf-8'))
#     # client_socket.close()
#     main_page()


# 注册界面
def register_page():
    clear()
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
    # print(account_number, password, email)
    put_buttons(['确定注册', '重新输入信息'], onclick=[lambda: register(account_number, password, email), register_page])

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
        put_buttons(['返回登录', '退出'], onclick=[login_page, main_page])

    else:
        toast(response, color='error')
        put_text("注册失败" + response)
        put_buttons(['重新注册', '退出'], onclick=[register_page, main_page])

# 转账页面
def transfer_page(username):
    clear()
    data = input_group(
        "转账",
        [
            input("目标账号: ", name="target_account", type="text"),
            input("转账金额：", name="amount", type=FLOAT),
        ],
    )
    target_account = data['target_account']
    amount = data['amount']
    print(type(amount))
    put_buttons(['确认转账', '返回'], onclick=[lambda: transfer(username, target_account, amount), lambda: account_page(username)])


# 转账函数
def transfer(sender, receiver, amount):
    request_data = 'transfer {} {} {}'.format(sender, receiver, amount)
    client_socket.send(request_data.encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    if response == 'success':
        toast("转账成功", color='success')
    else:
        toast(response, color='error')
        put_text(response)


# 链路质量
def checksum(data):
    n = len(data)
    m = n % 2
    sum = 0
    for i in range(0, n - m, 2):
        sum += (data[i]) + ((data[i + 1]) << 8)
    if m:
        sum += (data[-1])
    while sum >> 16:
        sum = (sum >> 16) + (sum & 0xffff)
    answer = ~sum & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

# 构造 ICMP 报文
def create_icmp_packet(seq):
    type = 8
    code = 0
    ID = os.getpid() & 0xffff
    data = b'abcdefghijklmnopqrstuvwabcdefghi'
    header = struct.pack('>BBHHH', type, code, 0, ID, seq)
    packet = header + data
    checksum_value = checksum(packet)
    packet = struct.pack('>BBHHH', type, code, checksum_value, ID, seq) + data
    return packet

# 发送 ICMP 请求并接收回复
def send_ping_request(host, seq):
    try:
        icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        dest_addr = socket.gethostbyname(host)
        packet = create_icmp_packet(seq)
        icmp_socket.sendto(packet, (dest_addr, 1))
        send_time = time.time()
        
        # 设置套接字超时时间为 1 秒
        icmp_socket.settimeout(1)
        recv_packet, addr = icmp_socket.recvfrom(1024)
        recv_time = time.time()
        rtt = (recv_time - send_time) * 1000  # 往返时间，单位毫秒
        
        # 解析 ICMP 报文
        icmp_header = recv_packet[20:28]
        icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq = struct.unpack('>BBHHH', icmp_header)
        
        # 检查收到的 ICMP 报文是否是回复报文
        if icmp_type == 0 and icmp_id == os.getpid() & 0xffff and icmp_seq == seq:
            return rtt
    except socket.timeout:
        pass
    finally:
        icmp_socket.close()

    return None

# Ping 函数def ping(host, count=4):
def ping(host, count=4):
    try:
        lost = 0
        min_rtt = float('inf')
        max_rtt = 0
        total_rtt = 0
        ping_info = ""

        for seq in range(1, count + 1):
            rtt = send_ping_request(host, seq)
            if rtt is None:
                print(f"请求超时")
                lost += 1
                ping_info += f"请求超时\n"
            else:
                min_rtt = min(min_rtt, rtt)
                max_rtt = max(max_rtt, rtt)
                total_rtt += rtt

        ping_info += f"\n与服务端 的 Ping 统计信息:\n"
        ping_info += f"\t数据包: 已发送 = {count}，已接收 = {count - lost}，丢失 = {lost} ({lost * 100 / count:.2f}% 丢失)\n"
        if count - lost > 0:
            ping_info += f"\t往返行程的估计时间(以毫秒为单位):\n"
            ping_info += f"\t最短 = {min_rtt:.2f}ms，最长 = {max_rtt:.2f}ms，平均 = {total_rtt / (count - lost):.2f}ms\n"

        return ping_info

    except PermissionError:
        return "请以管理员权限运行此程序"




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
        request_data = 'balance {}'.format(account_number)
        client_socket.send(request_data.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        # print(response)
        put_text(f"存款成功{amount}元，当前余额为：{response}元")
    elif action == '取款':
        amount = input("请输入取款金额：", type=FLOAT)
        request_data = 'withdrawal {} {}'.format(account_number, amount)
        client_socket.send(request_data.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        toast(response)
        if response == 'success':
            request_data = 'balance {}'.format(account_number)
            client_socket.send(request_data.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            put_text(f"取款成功{amount}元，当前余额为：{response}元")
        else:
            put_text("余额不足")
    elif action == '查询流水':
        request_data = 'transaction_history {}'.format(account_number)
        client_socket.send(request_data.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        put_text("交易记录：" + response)
    elif action == '转账':
        transfer_page(username)
    elif action == '链路质量':
        ping_result = ping(server_ip, 4)
        put_text("链路质量：" + ping_result)
    elif action == '清屏':
        account_page(username)
    elif action == '退出':
        main()
        # pass  # 退出循环


# # 账户界面
# def account_page(username):
#     clear()
#     put_text("请选择操作：")
#     # put_buttons(['查询余额', '存款', '取款', '查询流水', '退出'], onclick=lambda btn_val: handle_action(btn_val, client_socket, username))
#     put_buttons(['查询余额', '存款', '取款', '查询流水', '退出'], onclick=lambda btn_val: handle_action(btn_val, client_socket, username))

def account_page(username):
    clear()
    put_text("请选择操作：")
    put_buttons(['查询余额', '存款', '取款', '查询流水', '转账', '链路质量', '清屏', '退出'], onclick=lambda btn_val: handle_action(btn_val, client_socket, username))



# 主函数
def main():
    main_page()


if __name__ == '__main__':
    main()
