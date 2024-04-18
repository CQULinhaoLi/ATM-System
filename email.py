import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(sender_email, sender_password, receiver_email, subject, message):
    # 设置 SMTP 服务器地址和端口
    smtp_server = 'smtp.qq.com'
    smtp_port = 465  # 一般是 587 或 465

    # 创建 MIMEMultipart 对象
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # 将邮件正文添加到 MIMEMultipart 对象中
    msg.attach(MIMEText(message, 'plain'))

    # 开启 SMTP 连接
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)  # 使用 SSL 加密连接
        # 登录邮箱
        server.login(sender_email, sender_password)
        # 发送邮件
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print('邮件发送成功')
    except Exception as e:
        print('邮件发送失败:', e)
    finally:
        # 关闭 SMTP 连接
        server.quit()


# 发送邮件的参数
sender_email = '1577535969@qq.com'
sender_password = 'mtifqgnharcxghhf'
receiver_email = '2867296002@qq.com'
subject = '测试邮件'
message = '这是一封测试邮件，请勿回复。'

# 调用函数发送邮件
send_email(sender_email, sender_password, receiver_email, subject, message)
