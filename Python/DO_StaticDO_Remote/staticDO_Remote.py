#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
/*******************************************************************************
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
*    StaticDO_Remote.py
*
* Example Category:
*    DIO
*
* Description:
*    This example demonstrates how to use Static DO function.
*
* Instructions for Running:
*    1  Login the edge by hostName. If you'd like to handle a local device 
*       (i.e. USB or PCI/PCIe interfaced device in your PC), please bypass
*       this step.
*    2  Set the 'deviceDescription' for opening the device.
*    3  Set the 'profilePath' to save the profile path of being initialized
*       device.
*    4  Set the 'startPort'as the first port for Do .
*    5  Set the 'portCount'to decide how many sequential ports to operate Do.
*
* I/O Connections Overview:
*    Please refer to your hardware reference manual.
*
******************************************************************************/
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.path.pardir)))

from Automation.BDaq import *
from Automation.BDaq.InstantDoCtrl import InstantDoCtrl
from Automation.BDaq.BDaqApi import AdxEnumToString, BioFailed

deviceDescription = "DemoDevice,BID#0"
profilePath = u"../../profile/DemoDevice.xml"

startPort = 0
portCount = 1

def AdvInstantDO():
    ret = ErrorCode.Success

    # Step 1: Create a instantDoCtrl for DO function.
    # Login an Edge Server by hostname for remote control
    # Select a device by device number or device description and specify the
    # access mode.
    # In this example we use ModeWrite mode so that we can fully control the
    # device,
    # including configuring, sampling, etc.
    instantDoCtrl = InstantDoCtrl(deviceDescription, "IDAQ974Bid00")
	
    for _ in range(1):
        # Loads a profile to initialize the device
        instantDoCtrl.loadProfile = profilePath

        # Step 2: Write DO ports
        dataBuffer = [0] * portCount
        for i in range(startPort, portCount + startPort):
            inputVal = input("Input a 16 hex number for D0 port %d to output"
                             "(for example, 0x00): " % i)
            if not isinstance(inputVal, int):
                inputVal = int(inputVal, 16)

            dataBuffer[i-startPort] = inputVal

        ret = instantDoCtrl.writeAny(startPort, portCount, dataBuffer)
        if BioFailed(ret):
            break

        print("DO output completed!")

    # Step 3: Logout from server.
    instantDoCtrl.logout()
    
    # Step 4: Close device and release any allocated resource.
    instantDoCtrl.dispose()

    # If something wrong in this execution, print the error code on screen for
    # tracking.
    if BioFailed(ret):
        enumStr = AdxEnumToString("ErrorCode", ret.value, 256)
        print("Some error occurred. And the last error code is %#x. [%s]" %
              (ret.value, enumStr))

    return 0


if __name__ == "__main__":
    AdvInstantDO()
