import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import socket
import json

class Main:
    def __init__(self):
        self.success_list = []
        self.fail_list = []

        self.host_list_path = None
        self.smtp_server = None
        self.smtp_port = None
        self.smtp_username = None
        self.smtp_password = None
        self.from_email = None
        self.to_email = None
        self.email_subject = None

        self.get_config()
    
    def get_config(self):
        with open('config.json') as config_file:
            data = json.load(config_file)
        
        self.host_list_path = data['host_list_path']
        self.smtp_server = data['smtp_server']
        self.smtp_port = data['smtp_port']
        self.smtp_username = data['smtp_username']
        self.smtp_password = data['smtp_password']
        self.from_email = data['from_email']
        self.to_email = data['to_email']
        self.email_subject = data['email_subject']
    
    def check_list(self):
        start = datetime.now()
        ip_list = open(self.host_list_path).read().splitlines()

        for ip in ip_list:
            data = self.ping_test(ip)
            if(data['status']):
                self.success_list.append(data['ip'])
            else:
                self.fail_list.append(data['ip'])

        end = datetime.now()
        execution_time = end - start
        print("Execution time: {}".format(end - start))

        if(len(self.fail_list)>0):
            self.notify()


    def ping_test(self, ip):
        payload = {
            "ip": ip,
            "status": True if os.system("ping -c 1 " + ip) is 0 else False
        }
        return payload
    
    def notify(self):
        try:
            source_info = os.popen("uname -a").read()
            source_ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]

            sender = self.from_email
            receivers = self.to_email

            smtpObj = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            smtpObj.login(self.smtp_username, self.smtp_password)

            msg = MIMEMultipart("alternative")
            msg['From'] = sender
            msg['Subject'] = self.email_subject
        
            html = """\
            <html>
            <head></head>
            <body>
                <p>Source IP : """+str(source_ip)+"""
                <p>Source Info : """+str(source_info)+"""

                <p>Success List : """+str(self.success_list)+"""
                <p>Fail List : """+str(self.fail_list)+"""
            </body>
            </html>
            """

            msg.attach(MIMEText(html, 'html'))

            smtpObj.sendmail(sender, receivers, msg.as_string())         
            print ("Successfully sent email")
        except:
            print ("Error: unable to send email")

monitor = Main()
monitor.check_list()