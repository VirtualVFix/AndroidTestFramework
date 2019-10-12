# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/23/18 15:11"

from config import CONFIG
from optparse import OptionGroup
from libs.core.options import Options


class Email(Options):
    """
    Email notifications
    """

    def __init__(self):
        super(Email, self).__init__()

    def group(self, parser):
        group = OptionGroup(parser, 'Email notifications')
        group.add_option('-e', '--email', dest='email', default=None,
                         help='Add addresses to Framework Email notifications system. '
                              + '@host may be skipped in address. '
                              + '"%s" Email host will be used if host not specified. ' % CONFIG.TEST.NOTIFICATION_HOST
                              + 'To specify a list of recipients, separate them via commas and surround '
                              + 'with double quotes. '
                              + 'Example: -e "mail1@gmail.com,mail2@gmail.com" or --email "ID1,ID2"')
        group.add_option('--comment', dest='comment', default=None,
                         help='Add comment to notify during testing and to Email.')
        # group.add_option('--email-cycle', dest='email_cycle', default=None,
        #                  help='Send Email notifications after each test cycle.')
        # group.add_option('--email-per-error', dest='email_per_error', action="store_true", default=False,
        #                  help='Send Email notifications after each error.')
        return group

    async def validate(self, options):
        # email
        if options.email is not None:
            # add email class
            from libs.notify import Gmail
            CONFIG.TEST.NOTIFICATION_CLASS = Gmail
            # add email addresses
            CONFIG.TEST.NOTIFICATION_MAIL_LIST = [x.strip() if x.find('@') != -1
                                                  else x.strip() + CONFIG.TEST.NOTIFICATION_HOST
                                                  for x in options.email.split(',') if x.strip() != '']
        else:
            self.CLEAN_OF_REGISTERED()

        # comment
        if options.comment is not None:
            # keep comment
            CONFIG.TEST.NOTIFICATION_COMMENT = options.comment.strip()
