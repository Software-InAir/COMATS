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
*    InstantAI.py
*
* Example Category:
*    AI
*
* Description:
*    This example demonstrates how to use Instant AI function.
*
* Instructions for Running:
*    1. Login the edge by hostName. If you'd like to handle a local device 
*       (i.e. USB or PCI/PCIe interfaced device in your PC), please bypass this
*        step.
*    2. Set the 'deviceDescription' for opening the device.
*    3. Set the 'profilePath' to save the profile path of being initialized
*       device.
*    4. Set the 'startChannel' as the first channel for scan analog samples
*    5. Set the 'channelCount' to decide how many sequential channels to scan
*       analog samples.
*
* I/O Connections Overview:
*    Please refer to your hardware reference manual.
*
******************************************************************************/
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.path.pardir)))

from CommonUtils import kbhit

import time

from Automation.BDaq import *
from Automation.BDaq.InstantAiCtrl import InstantAiCtrl
from Automation.BDaq.BDaqApi import AdxEnumToString, BioFailed

deviceDescription = "DemoDevice,BID#0"
profilePath       = u"../../profile/DemoDevice.xml"

channelCount = 2
startChannel = 0

def AdvInstantAI():
    ret = ErrorCode.Success

    # Step 1: Create a 'instantAiCtrl' for InstantAI function
    # Login an Edge Server by hostname for remote control
    # Select a device by device number or device description and specify the
    # access mode.
    # In this example we use ModeWrite mode so that we can fully control the
    # device,
    # including configuring, sampling, etc.
    instanceAiObj = InstantAiCtrl(deviceDescription)
    #instanceAiObj = InstantAiCtrl(deviceDescription, "IDAQ974Bid00")
    
    for _ in range(1):
        
        # Loads a profile to initialize the device
        instanceAiObj.loadProfile = profilePath 

        # Step 2: Read samples and do post-process, we show data here.
        print("Acquisition is in progress, any key to quit!")
        while not kbhit():
            ret, scaledData = instanceAiObj.readData(startChannel, channelCount)
            if BioFailed(ret):
                break
            
            for i in range(startChannel, startChannel + channelCount):
                print("Channel %d data: %10.6f" % (i, scaledData[i-startChannel]))

            time.sleep(1)
            
    # Step 3: Logout from server.
    #instanceAiObj.logout()
    
    # Step 4: Close device, release any allocated resource
    instanceAiObj.dispose()

    if BioFailed(ret):
        enumStr = AdxEnumToString("ErrorCode", ret.value, 256)
        print("Some error occurred. And the last error code is %#x. [%s]" %
              (ret.value, enumStr))
    return 0


if __name__ == '__main__':
    AdvInstantAI()
