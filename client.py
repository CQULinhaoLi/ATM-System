import socket

def main():
    # 服务器的IP地址和端口号
    server_ip = '127.0.0.1'  # 如果服务器在本地，请使用 '127.0.0.1'，否则使用服务器的IP地址
    server_port = 5000  # 服务器监听的端口号
    
    try:
        # 创建socket对象
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 连接到服务器
        client_socket.connect((server_ip, server_port))
        print("Connected to the server.")

        while True:
            # 输入命令
            command = input("Enter command (e.g., 'register username password email', 'deposit username amount'): ")

            # 发送命令到服务器
            client_socket.sendall(command.encode())

            # 接收服务器的响应
            response = client_socket.recv(1024).decode()
            print("Response:", response)

            # 如果收到退出信号，退出循环
            if command.lower() == 'exit':
                break

    except Exception as e:
        print("Error:", e)
    finally:
        # 关闭socket连接
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
