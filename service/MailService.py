import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate


class MailService(object):

    def __init__(self):
        self.mail = 'buxarnet@gmail.com'
        self.password = 'qvznovxklvhktlsy'
        self.receiver_mail = 'buxarnet@yandex.com'

    def send_mail(self, msg):
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.starttls()
        smtpObj.login(self.mail, self.password)
        smtpObj.sendmail(self.mail, self.receiver_mail, msg)
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
        with open(f'{os.path.abspath("log/BuxarVideoUploader.log")}', 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename={}'.format('BuxarVideoUploader.log'))
        msg.attach(part)

        smtpObj.login(self.mail, self.password)
        smtpObj.sendmail(self.mail, self.receiver_mail, msg.as_string())
        smtpObj.quit()
