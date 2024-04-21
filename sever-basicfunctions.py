import socket
import json
import mysql.connector

# 定义数据库连接参数
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'atm_accounts'
}

# 创建数据库连接
db_connection = mysql.connector.connect(**db_config)
db_cursor = db_connection.cursor()

# 定义服务器地址和端口
HOST = '127......'
PORT = 1111

# 处理登录请求
def handle_login(data):
    account_number = data['account_number']
    pin = data['pin']
    # 查询数据库获取账户信息
    db_cursor.execute("SELECT pin, balance FROM accounts WHERE account_number = %s", (account_number,))
    account_data = db_cursor.fetchone()
    if account_data and account_data[0] == pin:
        return {'status': 'success', 'message': 'Login successful'}
    else:
        return {'status': 'error', 'message': 'Invalid account number or PIN'}

# 处理查询余额请求
def handle_balance(data):
    account_number = data['account_number']
    # 查询数据库获取账户余额
    db_cursor.execute("SELECT balance FROM accounts WHERE account_number = %s", (account_number,))
    account_balance = db_cursor.fetchone()
    if account_balance:
        return {'status': 'success', 'balance': account_balance[0]}
    else:
        return {'status': 'error', 'message': 'Account not found'}

# 处理存款请求
def handle_deposit(data):
    account_number = data['account_number']
    amount = data['amount']
    # 更新账户余额
    db_cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_number = %s", (amount, account_number))
    db_connection.commit()
    # 记录存款交易
    db_cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, 'deposit', %s)", (account_number, amount))
    db_connection.commit()
    return {'status': 'success', 'message': 'Deposit successful'}

# 处理取款请求
def handle_withdrawal(data):
    account_number = data['account_number']
    amount = data['amount']
    # 检查账户余额是否足够
    db_cursor.execute("SELECT balance FROM accounts WHERE account_number = %s", (account_number,))
    account_balance = db_cursor.fetchone()
    if account_balance and account_balance[0] >= amount:
        # 更新账户余额
        db_cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_number = %s", (amount, account_number))
        db_connection.commit()
        # 记录取款交易
        db_cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, 'withdrawal', %s)", (account_number, amount))
        db_connection.commit()
        return {'status': 'success', 'message': 'Withdrawal successful'}
    else:
        return {'status': 'error', 'message': 'Insufficient funds'}

# 处理查询交易记录请求
def handle_transaction_history(data):
    account_number = data['account_number']
    # 查询数据库获取交易记录
    db_cursor.execute("SELECT * FROM transactions WHERE account_number = %s", (account_number,))
    transactions = db_cursor.fetchall()
    if transactions:
        transaction_history = [{'id': transaction[0], 'transaction_type': transaction[2], 'amount': transaction[3], 'transaction_time': transaction[4]} for transaction in transactions]
        return {'status': 'success', 'transaction_history': transaction_history}
    else:
        return {'status': 'error', 'message': 'No transaction history'}

# 创建套接字
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # 绑定地址和端口
    server_socket.bind((HOST, PORT))
    # 开始监听连接
    server_socket.listen()
    print('Server is listening on {}:{}'.format(HOST, PORT))
    # 接受客户端连接
    conn, addr = server_socket.accept()
    with conn:
        print('Connected to', addr)
        while True:
            # 接收客户端发送的数据
            data = conn.recv(1024)
            if not data:
                break
            # 解析JSON数据
            data = json.loads(data.decode())
            # 根据请求类型处理数据
            if data['type'] == 'login':
                response = handle_login(data)
            elif data['type'] == 'balance':
                response = handle_balance(data)
            elif data['type'] == 'deposit':
                response = handle_deposit(data)
            elif data['type'] == 'withdrawal':
                response = handle_withdrawal(data)
            elif data['type'] == 'transaction_history':
                response = handle_transaction_history(data)
            else:
                response = {'status': 'error', 'message': 'Invalid request'}
            # 将响应数据转换为JSON格式并发送给客户端
            conn.sendall(json.dumps(response).encode())

# 关闭数据库连接
db_cursor.close()
db_connection.close()
