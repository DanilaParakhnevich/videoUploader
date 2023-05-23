import smtplib


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
