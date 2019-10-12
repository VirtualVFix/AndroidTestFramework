# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Feb 7, 2017 5:28:44 PM$"


# battery capacity in dumpsys
DUMPSYS_BATTERY_CAPACITY = 'dumpsys battery | grep level:'
# battery voltage in dumpsys
DUMPSYS_BATTERY_VOLTAGE = 'dumpsys battery | grep voltage:'
# battery temperature in dumpsys
DUMPSYS_BATTERY_TEMPERATURE = 'dumpsys battery | grep temperature:'

# Wake Locks and Suspend Blockers in dumpsys
DUMPSYS_WAKE_LOCK = 'dumpsys power'
# power wake lock 
POWER_WAKE_LOCK = '/sys/power/wake_lock'

# delay between check battery status
BATTERY_STATUS_CHECK_DELAY = 5*60 
# battery charging timeout. Exception will raise when expired
BATTERY_CHARGING_TIMEOUT = 30*60 
# warning massage wiil displayed when battery level not increased to this value during BATTERY_CHARGING_TIMEOUT
BATTERY_PERCENTAGE_THESHOLD_WARNING = 1 
BATTERY_PERCENTAGE_THESHOLD_TIMEOUT = 2 

# list off all device power up reasons
DEVICE_POWER_UP_REASONS = {
                '00000010': 'USB_CABLE',
                '00000020': 'FACTORY_CABLE',
                '00000080': 'POWER_KEY_PRESS',
                '00000100': 'CHARGER',
                '00000200': 'POWER_CUT',
                '00000800': 'SYSTEM_RESTART',
                '00004000': 'SW_AP_RESET',
                '00008000': 'WDOG_AP_RESET',
                '00010000': 'CLKMON_CKIH_RESET',
                '00020000': 'AP_KERNEL_PANIC',
                '00200000': 'BP_PANIC',
        }
# normal power up reasons
DEVICE_NORMAL_POWER_UP_REASONS = ['USB_CABLE','FACTORY_CABLE','POWER_KEY_PRESS','CHARGER','POWER_CUT','SW_AP_RESET']
# suspend state path
SUSPEND_STATE_FILE = '/d/suspend_stats'
# suspend min voltage path
SUSPEND_MIN_VOLTAGE_FILE = '/d/rpm_stats'

# Sorted memory measure units
MEMORY_MEASURE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']