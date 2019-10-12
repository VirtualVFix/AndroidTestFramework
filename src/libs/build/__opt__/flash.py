# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "13/10/17 20:54"

import os
from config import CONFIG
from optparse import OptionGroup
from libs.core.options import Options
from libs.core.exceptions import RuntimeInterruptError


class Flash(Options):
    """
    Flash device and build download options.
    """
    def __init__(self):
        super(Flash, self).__init__()
        self.__flash = False  # flash device option in use
        self.__flash_erase = False  # flash and erase option in use

    def group(self, parser):
        group = OptionGroup(parser, 'Flash device and build download')
        group.add_option('--flash', dest='flash', action="store_true", default=False,
                         help='Flash device before testing started.')
        group.add_option('--flash-erase', dest='flash_erase', action="store_true", default=False,
                         help='Erase user data, cache and flash device before testing started.')
        group.add_option('--build-path', dest='build_path', default=None,
                         help='Path to build for flashing device. You can specify path to build folder '
                              + 'or .tr/.tgz/.tar build archive.')
        group.add_option('--build-tag', dest='build_tag', default=None,
                         help='Build tag or full build name. '
                              + '(Example: dev_oem, dev_vrz, dev_oem_user_7.1.1_NNN26.170_60_release-keys-oem).')
        group.add_option('--build-job', dest='build_job', default=None,
                         help='Jenkins or Artifactory build Job name. Used to find build on Jenkins/Atrifactiry '
                              + 'server and download it. '
                              + '(Example: NNN26_dev-retail_user_8998_release-keys)')
        return group

    async def validate(self, options):

        # build tag and job
        if options.build_tag:
            CONFIG.TEST.BUILD_TAGNAME = options.build_tag
        if options.build_job:
            CONFIG.TEST.BUILD_JOBNAME = options.build_job

        # --flash device
        if options.flash and options.flash_erase:
            raise RuntimeInterruptError('options [--flash] and [--flash-erase] are mutually exclusive')
        if options.flash:
            self.__flash = True

        # --flash-erase device
        if options.flash_erase:
            self.__flash_erase = True

        # --build option
        if options.build_path:
            # from libs.core.unittest.wait import Wait
            # wait for device
            # await Wait.wait_for_device()

            # if options.build_path.find(CONFIG.DEVICE.DEVICE_NAME) == -1 and options.build_path.find(
            #         CONFIG.DEVICE.DEVICE_PRODUCT) == -1:
            #     raise RuntimeInterruptError('Build specified in [--build-path] option is not valid for "%s" product !'
            #                                 % CONFIG.DEVICE.DEVICE_NAME.upper())
            if not os.path.exists(options.build_path):
                raise RuntimeInterruptError('Build path [%s] does not exists ! ' % options.build_path
                                            + 'Please validate path for [--build-path] option.')
            CONFIG.TEST.BUILD_PATH = options.build

        # clear registered functions
        if not self.__flash and not self.__flash_erase:
            self.CLEAN_OF_REGISTERED()

    def setup_frame(self):
        if self.__flash:
            from libs.build import Flash
            Flash(CONFIG.DEVICE.SERIAL).findBuildAndflash(jobname=CONFIG.TEST.BUILD_JOBNAME,
                                                          buildtag=CONFIG.TEST.BUILD_TAGNAME,
                                                          erase=False, waitidle=True)
        elif self.__flash_erase:
            from libs.build import Flash
            Flash(CONFIG.DEVICE.SERIAL).findBuildAndflash(jobname=CONFIG.TEST.BUILD_JOBNAME,
                                                          buildtag=CONFIG.TEST.BUILD_TAGNAME,
                                                          erase=True, waitidle=True)
