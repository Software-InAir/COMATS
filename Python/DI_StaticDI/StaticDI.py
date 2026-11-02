#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
********************************************************************************
Copyright (c) 1983-2024 Advantech Co., Ltd.
********************************************************************************
Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in  
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so,  subject to the following conditions: 
 
The above copyright notice and this permission notice shall be included in all  
copies or substantial portions of the Software. 
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.  

================================================================================
REVISION HISTORY
--------------------------------------------------------------------------------
$Log:  $
--------------------------------------------------------------------------------
$NoKeywords:  $
*/
/******************************************************************************
*
* Windows Example:
*    StaticDI.py
*
* Example Category:
*    DIO
*
* Description:
*    This example demonstrates how to use Static DI function.
*
* Instructions for Running:
*    1  Login the edge by hostName. If you'd like to handle a local device 
*       (i.e. USB or PCI/PCIe interfaced device in your PC), please bypass this
*       step.
*    2  Set the 'deviceDescription' for opening the device. 
*    3  Set the 'profilePath' to save the profile path of being initialized
*       device. 
*    4  Set the 'startPort' as the first port for Di scanning.
*    5  Set the 'portCount' to decide how many sequential ports to operate Di
*       scanning.
*
* I/O Connections Overview:
*    Please refer to your hardware reference manual.
*
******************************************************************************/
"""
import time, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.path.pardir)))
from CommonUtils import kbhit

from Automation.BDaq import *
from Automation.BDaq.InstantDiCtrl import InstantDiCtrl
from Automation.BDaq.BDaqApi import AdxEnumToString, BioFailed

deviceDescription = "DemoDevice,BID#0"
profilePath = u"../../profile/DemoDevice.xml"

startPort = 0
portCount = 1

def AdvInstantDI():
    ret = ErrorCode.Success

    # Step 1: Create a 'InstantDiCtrl' for DI function.
    # Login an Edge Server by hostname for remote control
    # Select a device by device number or device description and specify the
    # access mode.
    # In this example we use ModeWrite mode so that we can fully control the
    # device,
    # including configuring, sampling, etc.
    instantDiCtrl = InstantDiCtrl(deviceDescription)
    #instantDiCtrl = InstantDiCtrl(deviceDescription, "IDAQ974Bid00")
	
    for _ in range(1):
        # Loads a profile to initialize the device
        instantDiCtrl.loadProfile = profilePath

        # Step 2: Read DI ports' status and show.
        print("Reading ports status is in progress, any key to quit!")
        while not kbhit():
            ret, data = instantDiCtrl.readAny(startPort, portCount)
            if BioFailed(ret):
                break

            for i in range(startPort, startPort + portCount):
                print("DI port %d status is %#x" % (i, data[i-startPort]))
            time.sleep(1)

        print("\n DI output completed !")

    # Step 3: Logout from server.
    #instantDiCtrl.logout()
 
    # Step 4: Close device and release any allocated resource
    instantDiCtrl.dispose()

    # If something wrong in this execution, print the error code on screen for
    # tracking.
    if BioFailed(ret):
        enumStr = AdxEnumToString("ErrorCode", ret.value, 256)
        print("Some error occurred. And the last error code is %#x. [%s]" %
              (ret.value, enumStr))
    return 0


if __name__ == '__main__':
    AdvInstantDI()
