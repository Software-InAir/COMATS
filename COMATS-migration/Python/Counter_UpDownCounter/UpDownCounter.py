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
*     UpDownCounter.py
*
* Example Category:
*    Counter
*
* Description:
*    This example demonstrates how to use UpDown Counter function.
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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.path.pardir)))
from CommonUtils import kbhit

from Automation.BDaq import ErrorCode, DeviceInformation, AccessMode
from Automation.BDaq import CountingType
from Automation.BDaq.UdCounterCtrl import UdCounterCtrl
from Automation.BDaq.BDaqApi import AdxEnumToString, BioFailed

deviceDescription = "DemoDevice,BID#0"
profilePath = u"../../profile/DemoDevice.xml"

channelStart = 0
channelCount = 1

def AdvUdCounter():
    # Step 1: Create a 'UdCounterCtrl' for UpDown Counter function
    # Login an Edge Server by hostname for remote control
    # Select a device by device number or device description and specify the
    # access mode.
    # In this example we use ModeWrite mode so that we can fully control the
    # device, including configuring, sampling, etc.
    udCounterCtrl = UdCounterCtrl(deviceDescription)
    #udCounterCtrl = UdCounterCtrl(deviceDescription, "IDAQ974Bid00")

    # Loads a profile to initialize the device
    udCounterCtrl.loadProfile = profilePath

    # Step 2: Set necessary parameters
    # set start channel number and channel count for UpDown Counter
    udCounterCtrl.channelStart = channelStart
    udCounterCtrl.channelCount = channelCount

    # Step 3: Set counting type for UpDown Counter
    for i in range(channelStart, channelStart + channelCount):
        udCounterCtrl.channels[i].countingType = CountingType.PulseDirection

    # Step 4: Start UpDown Counter
    udCounterCtrl.enabled = True

    # Step 5: Read counting value: connect the input signal to channels you
    # selected to get UpDown counter value.
    print("UpDown counter is in progress.. connect the input signal")
    print("Any key will stop UpDown counter!")
    while not kbhit():
        time.sleep(1)
        ret, value = udCounterCtrl.read()
        if BioFailed(ret):
            break
        print(" channel %u Current UpDown count: %u" % (channelStart, value[0]))

    # Step 6: stop UpDown Counter
    udCounterCtrl.enabled = False

    # Step 7: Logout from server.
    #udCounterCtrl.logout()
    
    # Step 8: Close device and release any allocated resource
    udCounterCtrl.dispose()

    # If something wrong in this execution, print the error code on screen for
    # tracking
    if BioFailed(ret):
        enumStr = AdxEnumToString("ErrorCode", ret.value, 256)
        print("Some error occurred. And the last error code is %#x. [%s]" %
              (ret.value, enumStr))

    return 0


if __name__ == '__main__':
    AdvUdCounter()
