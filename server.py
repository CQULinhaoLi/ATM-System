import pymysql.cursors
import hashlib

# 连接数据库
def connect_db():
    return pymysql.connect(host='localhost',
                           user='root',
                           password='dsy20030820',
                           database='user',
                           cursorclass=pymysql.cursors.DictCursor)

#查询邮件
def emailnum(username):
    with connect_db() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE username = %s", (username))
            return cursor.fetchone()
        
#查询余额
def balance(username):
    with connect_db() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT balance FROM users WHERE username = %s", (username))
            return cursor.fetchone()


#用户注册
def register(username, password, email):
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()  # 加密密码
    with connect_db() as connection:
        with connection.cursor() as cursor:
            # 检查用户名是否已经存在
            cursor.execute("SELECT username FROM users WHERE username = %s", (username))
            existing_user = cursor.fetchone()
            if existing_user:
                print("用户名已经存在，请选择其他用户名。")
                return False

            # 执行用户插入操作
            sql = "INSERT INTO users (username, possword, email) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, hashed_password, email))
            connection.commit()
            print("用户注册成功。")
            return True

# 用户登录验证
def authenticate(username, password):
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    with connect_db() as connection:
        with connection.cursor() as cursor:
            sql = "SELECT username FROM users WHERE username = %s AND possword = %s"
            cursor.execute(sql, (username, hashed_password))
            result = cursor.fetchone()
            if result:
                print("登录成功!")
                return True
            else:
                print("登录失败!")
                return False

# 存款
def deposit(username, amount):
    with connect_db() as connection:
        with connection.cursor() as cursor:
            if amount <= 0:
                return False
            else:
                # 更新余额
                sql = "UPDATE users SET balance = balance + %s WHERE username = %s"
                cursor.execute(sql, (amount, username))
                connection.commit()
                #记录交易
                sqlt = "INSERT INTO transfer (username, transtype, amount) VALUES (%s, '存款', %s)"
                cursor.execute(sqlt,(username, amount))
                connection.commit()
                return True

# 取款
def withdraw(username, amount):
    with connect_db() as connection:
        with connection.cursor() as cursor:
            # 查询当前用户余额
            cursor.execute("SELECT balance FROM users WHERE username = %s", (username))
            current_balance = cursor.fetchone()['balance']

            # 如果取款金额大于余额，则不执行取款，并打印错误信息
            if amount > current_balance:
                print("取款失败: 余额不足.")
                return False
            else:
                # 更新余额
                sql = "UPDATE users SET balance = balance - %s WHERE username = %s"
                cursor.execute(sql, (amount, username))
                connection.commit()
                #记录交易
                sqlt = "INSERT INTO transfer (username, transtype, amount) VALUES (%s, '取款', %s)"
                cursor.execute(sqlt,(username, amount))
                connection.commit()
                print("取款成功.")
                return True

#查询存取记录
def select(username):
     print("select")
     with connect_db() as connection:
        with connection.cursor() as cursor:
            sql = "select * from transfer where username = %s"
            cursor.execute(sql,username)
            return cursor.fetchall()

#查询转账记录
def interselect(username):
     print("interselect")
     with connect_db() as connection:
        with connection.cursor() as cursor:       
            sql = "select * from intertransfer where sender_username = %s or receiver_username = %s"
            u1 = username 
            u2 = username
            cursor.execute(sql,(u1, u2))
            return cursor.fetchall()
        

#转账
def intertransfer(sender_username, receiver_username, amount):
    with connect_db() as connection:
        with connection.cursor() as cursor:
            # 开始事务
            connection.begin()
            
            try:
                # 查询发送者当前余额
                cursor.execute("SELECT balance FROM users WHERE username = %s", (sender_username,))
                sender_balance = cursor.fetchone()['balance']
                if sender_balance < amount:
                    print("转账失败: 发送者余额不足。")
                    return False

                # 扣除发送者的余额
                cursor.execute("UPDATE users SET balance = balance - %s WHERE username = %s",
                               (amount, sender_username))

                # 查询接收者是否存在
                cursor.execute("SELECT username FROM users WHERE username = %s", (receiver_username,))
                if not cursor.fetchone():
                    print("转账失败: 接收者不存在。")
                    return False

                # 为接收者增加余额
                cursor.execute("UPDATE users SET balance = balance + %s WHERE username = %s",
                               (amount, receiver_username))

                # 记录交易
                cursor.execute("INSERT INTO intertransfer (sender_username, receiver_username, amount) VALUES (%s, %s, %s)",
                               (sender_username, receiver_username, amount))

                # 提交事务
                connection.commit()
                print("转账成功。")
                return True
            except Exception as e:
                # 出现任何异常时回滚事务
                connection.rollback()
                print(f"转账失败: {e}")
                return False