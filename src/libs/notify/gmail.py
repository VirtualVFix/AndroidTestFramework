# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/23/18 15:11"

import pytz
import base64
import smtplib
from config import CONFIG
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import format_datetime
from email.mime.multipart import MIMEMultipart
from libs.core.logger import getSysLogger, getLogger


class Gmail:
    """
    Email notify class base on GMail
    """
    def __init__(self, logger=None):
        self.logger = logger or getLogger(__file__, propagate=True)
        self.syslogger = getSysLogger()

    def send_email(self, subject, text, maillist=None, attachment=None, attachment_filename=None):
        """
        Send email to email list.

        Args:
             maillist (list): List of email addresses. Fist address from list will be added to "To" field,
                all other to "Cc"
             subject (str): Email subject
             text (str): Email body
             attachment (file, default None): Attachment file
             attachment_filename (str, default None): Attachment file name
        """
        if maillist is None:
            maillist = CONFIG.TEST.NOTIFICATION_MAIL_LIST
        assert isinstance(maillist, list) and len(maillist) > 0, 'You must pass a mail list as list'
        session = None
        try:
            self.logger.info('Initializing Email sender...', self.syslogger)
            session = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            session.ehlo()
            session.login(CONFIG.TEST.NOTIFICATION_EMAIL,
                          base64.urlsafe_b64decode(CONFIG.TEST.NOTIFICATION_PWD).decode())
            self.logger.done()

            self.logger.info('Sending Email notify to %s ...' % (', '.join(x for x in maillist)), self.syslogger)
            msg = MIMEMultipart()
            msg['From'] = CONFIG.TEST.NOTIFICATION_EMAIL
            msg['To'] = maillist[0]
            msg['Cc'] = ','.join(x for x in maillist[1:])
            msg['Date'] = format_datetime(datetime.now(pytz.timezone(CONFIG.SYSTEM.TIMEZONE)))
            msg['Subject'] = '%s %s' % (CONFIG.TEST.NOTIFICATION_TAG, subject)

            _cont = MIMEText(text, 'html')
            msg.attach(_cont)
            if attachment is not None:
                attachment_filename = attachment_filename if attachment_filename is not None else 'attachment_file'
                _att = MIMEText(attachment)
                _att.add_header('Content-Disposition', 'attachment',
                                filename=attachment_filename)
                msg.attach(_att)
            session.sendmail(msg["From"], msg["To"].split(",") + msg["Cc"].split(","), msg.as_string())

            self.syslogger.newline()
            self.syslogger.info('[From]: %s ' % msg['From'])
            self.syslogger.info('[To]: %s' % msg['To'])
            self.syslogger.info('[Cc]: %s' % msg['Cc'])
            self.syslogger.info('[Date]: %s' % msg['Date'])
            self.syslogger.info('[Subject]: %s' % msg['Subject'])
            self.syslogger.info('[Attachment]: %s' % attachment_filename)
            # self.syslogger.info('[Body]: %s' % text)
            self.syslogger.newline()
            self.logger.done(self.syslogger)
        except Exception as e:
            self.syslogger.exception(e)
            if CONFIG.SYSTEM.DEBUG:
                raise
            self.logger.error(e)
        finally:
            if session is not None:
                session.quit()
