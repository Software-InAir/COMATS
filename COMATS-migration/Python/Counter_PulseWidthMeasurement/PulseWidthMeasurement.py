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
*     PulseWidthMeasurement.py
*
* Example Category:
*    Counter
*
* Description:
*    This example demonstrates how to use Pulse Width Measurement function.
*
* Instructions for Running:
*    1  Login the edge by hostName. If you'd like to handle a local device 
*       (i.e. USB or PCI/PCIe interfaced device in your PC), please bypass this
*       step.
*    2  Set the 'deviceDescription' for opening the device.
*    3  Set the 'profilePath' to save the profile path of being initialized
*       device.
*    4  Set the 'channelStart' as the start channel of the counter to operate
*    5  Set the 'channelCount' as the channel count of the counter to operate.
*
* I/O Connections Overview:
*    Please refer to your hardware reference manual.
*
******************************************************************************/
"""
import time, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from CommonUtils import kbhit

from Automation.BDaq import *
from Automation.BDaq.PwMeterCtrl import PwMeterCtrl
from Automation.BDaq.BDaqApi import BioFailed, AdxEnumToString

deviceDescription = "DemoDevice,BID#0"
profilePath = u"../../profile/DemoDevice.xml"

startChannel = 0
channelCount = 1

def AdvPwMeter():
    ret = ErrorCode.Success

    # Step 1: Create a 'PwMeterCtrl' for PulseWidthMeasurement function
    # Login an Edge Server by hostname for remote control
    # Select a device by device number or device description and specify the
    # access mode.
    # In this example we use ModeWrite mode so that we can fully control the
    # device, including configuring, sampling, etc.
    pwMeterCtrl = PwMeterCtrl(deviceDescription)
    #pwMeterCtrl = PwMeterCtrl(deviceDescription, "IDAQ974Bid00")
	
    for _ in range(1):
        # Loads a profile to initialize the device
        pwMeterCtrl.loadProfile = profilePath

        # Step 2: Set necessary parameters
        # set the channel start number and channel count for PulseWidthMeasurement
        pwMeterCtrl.channelStart = startChannel
        pwMeterCtrl.channelCount = channelCount

        # Step 3: Start PulseWidthMeasurement
        pwMeterCtrl.enabled = True

        # Step 4: Get Pulse Width value
        print("Pulse Width Measurement is in progress... any key to quit !")
        while not kbhit():
            time.sleep(1)
            ret, pwValueList = pwMeterCtrl.read()
            if BioFailed(ret):
                break
            for i, pwValue in enumerate(pwValueList):
                print("Channel %u Current Pulse Width:HiPeriod=%f s  "
                      "LoPeriod=%f s" %
                      (startChannel + i, pwValue.HiPeriod, pwValue.LoPeriod))

        # Step 5: Stop PulseWidthMeasurement
        pwMeterCtrl.enabled = False

    # Step 6: Logout from server.
    #pwMeterCtrl.logout()
    
    # Step 7: Close device and release any allocated resource
    pwMeterCtrl.dispose()

    # If something wrong in this execution, print the error code on screen for
    # tracking.
    if BioFailed(ret):
        enumStr = AdxEnumToString("ErrorCode", ret.value, 256)
        print("Some error occurred. And the last error code is 0x%X. [%s]" %
              (ret.value, enumStr))
    return 0


if __name__ == '__main__':
    AdvPwMeter()
