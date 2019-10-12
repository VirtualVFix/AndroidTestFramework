# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/21/18 17:15"

""" 
Switchboard implementation depends of selected options. Switchbarod class after Framework initialization keep in
**CONFIG.SWITCH.CLASS** config variable. Also **CONFIG.SWTICH.SERIAL** keep switchboard serial number. 

Usage: 

.. code-block:: python

    from config import CONFIG
    
    if CONFIG.SWITCH.CLASS is not None:
        switch = CONFIG.SWITCH.CLASS(CONFIG.SWITCH.SERIAL)  #create switch board class object
        switch.connect(port=0)  # connect port 0
"""

from libs.switch.arconame.acroname import Acroname


__all__ = ['Acroname']
