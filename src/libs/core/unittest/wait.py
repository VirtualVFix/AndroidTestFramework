# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "11/30/2017 10:32 AM"

import asyncio
from config import CONFIG
from .config import FILTERS_NAMES


class Wait:
    """
    Unittest await help tools
    """

    @staticmethod
    async def wait_for_available_cases():
        """
        Waiting till TestCases are loaded to CONFIG
        """
        while True:
            if CONFIG.UNITTEST.AVAILABLE_TEST_CASES is not None:
                break
            await asyncio.sleep(0)

    @staticmethod
    async def wait_for_selected_cases():
        """
        Waiting till TestCases are filtered according to selection criteria
        """
        while True:
            if CONFIG.UNITTEST.SELECTED_TEST_CASES is not None:
                break
            await asyncio.sleep(0)

    @staticmethod
    async def wait_for_selected_suites():
        """
        Waiting till TestSuites are filtered according to selection criteria
        """
        # wait selected cases
        await Wait.wait_for_selected_cases()

        while True:
            if False not in [True if FILTERS_NAMES['suite_select'] in x['filters'] else False
                             for x in CONFIG.UNITTEST.SELECTED_TEST_CASES]:
                break
            await asyncio.sleep(0)

    @staticmethod
    async def wait_for_load_tests():
        """
        Waiting till Tests are loaded for selected TestSuites
        """
        # wait selected TestSuites
        await Wait.wait_for_selected_suites()
        while True:
            if False not in [True if FILTERS_NAMES['test_load'] in x['filters'] else False
                             for x in CONFIG.UNITTEST.SELECTED_TEST_CASES]:
                break
            await asyncio.sleep(0)

    @staticmethod
    async def wait_for_selected_tests():
        """
        Waiting till Tests are filtered according to selection criteria
        """
        # wait selected suites
        await Wait.wait_for_load_tests()

        while True:
            if False not in [True if FILTERS_NAMES['test_select'] in x['filters'] else False
                             for x in CONFIG.UNITTEST.SELECTED_TEST_CASES]:
                break
            await asyncio.sleep(0)

    @staticmethod
    async def wait_for_device():
        """
        Waiting till device detected
        """
        pass
