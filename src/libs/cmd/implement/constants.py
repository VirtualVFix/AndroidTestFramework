# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/26/17 12:01"

#: Default wait timeout in seconds for kill/terminate command
DEFAULT_WAIT_KILL_TIMEOUT = 2
#: Default timeout for any commands in seconds
DEFAULT_COMMAND_TIMEOUT = 120
#: Default wait for device timeout in seconds
DEFAULT_WAIT_DEVICE_TIMEOUT = 240
#: Default root wait device timeout in seconds
DEFAULT_WAIT_ROOT_TIMEOUT = 120
#: Default remount timeout in seconds
DEFAULT_REMOUNT_TIMEOUT = 160
#: Default wait for IDLE timeout in seconds
DEFAULT_WAIT_IDLE_TIMEOUT = 900
#: Default wait for Service timeout in seconds
DEFAULT_WAIT_SERVICE_TIMEOUT = 300
#: Default first device detect timeout in seconds
DEFAULT_FIRST_DEVICE_DETECT_TIMEOUT = 120
#: Default pull timeout in seconds
DEFAULT_PULL_TIMEOUT = 120
#: Default push timeout in seconds
DEFAULT_PUSH_TIMEOUT = 120
#: Command verbose by default for some commands like root, restart_adb etc from Manager.
DEFAULT_MANAGER_COMMAND_VERBOSE = True
#: Is adb server kill allowed
DEFAULT_ADB_SERVER_KILL_ALLOWED = False
# Default minimal windows count for detect Idle state
DEFAULT_WINDOWS_THRESHOLD_FOR_DETECT_IDLE = 3
#: Default sleep time in seconds after detect windows
DEFAULT_SLEEP_FOR_WAIT_IDLE = 2
#: Default sleep time in seconds when device was detected in ADB
DEFAULT_SLEEP_FOR_WAIT_ADB = 2
#: Default sleep time in seconds when service was detected
DEFAULT_SLEEP_FOR_WAIT_SERVICE = 2

#: Remove line special symbols "\n\r\t" from each command output line. Affect all execute commands
DEFAULT_REMOVE_SPECIAL_SYMBOLS = False
#: Print command output in interactive mode. Affect all execute commands
DEFAULT_VERBOSE_COMMAND = False
#: run command thread as daemon
RUN_COMMAND_THREAD_AS_DAEMON = False

#: Default cache property timeout in seconds
PROPERTY_CACHE_TIMEOUT = 30

#: CMD default logger name
CMD_LOG_NAME = 'cmd'
#: Cmd default logger file name
CMD_LOG_FILE_NAME = CMD_LOG_NAME

#: ADB aliases
ADB_MODE_ALIASES = ['adb']
#: Fastboot aliases
FASTBOOT_MODE_ALIASES = ['fastboot', 'fb', 'bootloader']

#: Command retry counter. Allow command retry when > 0
CMD_RETRY_COUNT = 3
#: Switch board reconnect after each N retry. Allow switch reconnect when > 0. Should be <=  CMD_RETRY_COUNT
CMD_SWITCH_RECONNECT_AFTER = 3
#: Switch reconnect delay in seconds
CMD_SWITCH_RECONNECT_DELAY = 20
#: Allow retry after TimeoutExpired error
CMD_RETRY_AFTER_TIMEOUT_ERROR = False
#: Retry delay in seconds
CMD_RETRY_DELAY = 30

#: How many line prints from output if error found in non debug mode
CMD_ERROR_PRINT_LINES = 5

#: Serial numbers to launch command emulation
EMULATOR_SERIAL_LIST = ['emulator', 'fake']
