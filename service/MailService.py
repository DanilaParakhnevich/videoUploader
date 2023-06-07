import os
import smtplib
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path


class MailService(object):

    def __init__(self):
        self.mail = 'buxarvideouploader.info@gmail.com'
        self.password = 'sdczswgxhthwzhml'
        self.receiver_mail = 'buxarvideouploader.info@gmail.com'

    def send_mail(self, msg):
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.starttls()
        smtpObj.login(self.mail, self.password)
        smtpObj.sendmail(self.mail, self.mail, msg)
        smtpObj.quit()

    def send_log(self):
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.starttls()


        msg = MIMEMultipart()
        msg['From'] = self.mail
        msg['To'] = self.mail
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'BuxarVideoUploader bug attachment'

        part = MIMEBase('application', "octet-stream")
        with open(f'{os.path.abspath("log/app.log")}', 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename={}'.format('app.log'))
        msg.attach(part)

        smtpObj.login(self.mail, self.password)
        smtpObj.sendmail(self.mail, self.mail, msg.as_string())
        smtpObj.quit()
