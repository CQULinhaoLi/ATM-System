import socket
import threading
import server
import post
#链表转字符串
def list_of_dicts_to_string(transactions):
    if not transactions:
        return "Empty list"

    result = ""
    for transaction in transactions:
        transaction_str = (
            f"ID: {transaction['id']}, "
            f"Username: {transaction['username']}, "
            f"Transaction Type: {transaction['transtype']}, "
            f"Amount: {transaction['amount']}"
        )
        result += transaction_str + "\n"

    result = str(result)
    return result

# 服务器端处理客户端请求的函数
def client_handler(connection, address):
    print(f"Connected by {address}")
    try:
        while True:
            # 读取客户端发送的数据
            data = connection.recv(1024)
            if not data:
                break  # 如果没有数据，退出循环
            message = data.decode()
            print(f"Received from {address}: {message}")
            
            # 解析收到的命令（假设客户端发送的是文本指令）
            command_parts = message.split(' ')
            command = command_parts[0].lower()
            print(command)
            
            if command == 'register':
                # 用户注册逻辑
                if len(command_parts) < 4:
                    response = "注册命令格式错误。正确格式：register <username> <password> <email>"
                else:
                    username = command_parts[1]
                    password = command_parts[2]
                    email = command_parts[3]
                    result = server.register(username, password, email)
                    if result:
                        # 发送邮件的参数
                        sender_email = '1577535969@qq.com'
                        sender_password = 'mtifqgnharcxghhf'
                        receiver_email = email
                        print(email)
                        subject = '注册'
                        message = '你已注册用户名为{}的账户'.format(username)
                        # 调用函数发送邮件
                        post.send_email(sender_email, sender_password, receiver_email, subject, message)

                        response = "success"                       
                    else:
                        response = "false"
            
            elif command == 'login':
                # 用户登录验证
                if len(command_parts) < 3:
                    response = "登录命令格式错误。正确格式：login <username> <password>"
                else:
                    username = command_parts[1]
                    password = command_parts[2]
                    success = server.authenticate(username, password)
                    response = "success" if success else "false"
            
            elif command == 'deposit':
                # 存款逻辑
                if len(command_parts) < 2:
                    response = "存款命令格式错误。正确格式：deposit <username> <amount>"
                else:
                    username = command_parts[1]
                    amount = float(command_parts[2])
                    server.deposit(username, amount)
                    # 发送邮件的参数
                    sender_email = '1577535969@qq.com'
                    sender_password = 'mtifqgnharcxghhf'
                    receiver_email = server.emailnum(username)['email']
                    print(receiver_email)
                    subject = '存款'
                    message = '你已成功存款{}元'.format(amount)
                    # 调用函数发送邮件
                    post.send_email(sender_email, sender_password, receiver_email, subject, message)
                    response = "success"
            
            elif command == 'withdrawal':
                # 取款逻辑
                if len(command_parts) < 2:
                    response = "取款命令格式错误。正确格式：withdraw <username> <amount>"
                else:
                    username = command_parts[1]
                    amount = float(command_parts[2])
                    result = server.withdraw(username, amount)
                    if result:
                        # 发送邮件的参数
                        sender_email = '1577535969@qq.com'
                        sender_password = 'mtifqgnharcxghhf'
                        receiver_email = server.emailnum(username)['email']
                        subject = '取款'
                        message = '你已成功取款{}元'.format(amount)
                        # 调用函数发送邮件
                        post.send_email(sender_email, sender_password, receiver_email, subject, message)
                        response = "success"
                    else:
                        response = "false"

            elif command == "transaction_history":
                if len(command_parts) < 1:
                    response = "取款命令格式错误。正确格式：select <username>"
                else:
                    username = command_parts[1]
                    response = server.select(username)
                    response = list_of_dicts_to_string(response)
                    print(response)
            
            elif command == "balance":
                if len(command_parts) < 1:
                    response = "取款命令格式错误。正确格式：select <username>"
                else:
                    username = command_parts[1]
                    response = server.balance(username)["balance"]
                    response = str(response)
                    
            else:
                response = "未知命令。"

            # 向客户端发送响应
            connection.sendall(response.encode())
            
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        # 关闭连接
        connection.close()

# 启动ATM服务器，监听端口
def start_atm_server(host='0.0.0.0', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server is listening on {host}:{port}")

    try:
        while True:
            # 接受一个新的连接
            conn, addr = server_socket.accept()
            # 创建一个新的线程来处理连接
            thread = threading.Thread(target=client_handler, args=(conn, addr))
            thread.start()
            print(f"Active connections: {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_atm_server()