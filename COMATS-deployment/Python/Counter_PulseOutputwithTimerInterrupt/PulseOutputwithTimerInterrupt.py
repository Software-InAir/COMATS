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
* Windows  Example:
*    PulseOutputwithTimerInterrupt.py
*
* Example Category:
*    Counter
*
* Description:
*    This example demonstrates how to use Pulse Output with Timer Interrupt function.
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
*    6  set the 'frequency' to decide the frequency of pulse for selected
*       channel.
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
from Automation.BDaq.TimerPulseCtrl import TimerPulseCtrl

deviceDescription = "DemoDevice,BID#0"
profilePath = u"../../profile/DemoDevice.xml"

startChannel = 0
channelCount = 1

frequency = 10.0

def AdvTimerPulse():
    # Step 1: Create a 'TimerPulseCtrl' for Pulse Output with Timer Interrupt
    # function
    # Login an Edge Server by hostname for remote control
    # Select a device by device number or device description and specify the
    # access mode.
    # In this example we use ModeWrite mode so that we can fully control the
    # device, including configuring, sampling, etc.
    timerPulseCtrl = TimerPulseCtrl(deviceDescription)
    #timerPulseCtrl = TimerPulseCtrl(deviceDescription, "IDAQ974Bid00")

    # Loads a profile to initialize the device
    timerPulseCtrl.loadProfile = profilePath

    # Step 2: Set necessary parameters
    #  # get channel max number for timer pulse
    channelCountMax = timerPulseCtrl.features.channelCountMax

    # set start channel number and channel count for timer pulse
    timerPulseCtrl.channelStart = startChannel
    timerPulseCtrl.channelCount = channelCount

    # set all channels
    for i in range(startChannel, startChannel + channelCount):
        timerPulseCtrl.channels[i % channelCountMax].frequency = frequency

    # Step 3: Start PulseOutputWithTimerInterrupt
    print("PulseOutputWithTimerInterrupt is in progress..")
    print("Test signal to the Out pin!")
    print("Any key to quit !")
    timerPulseCtrl.enabled = True

    while not kbhit():
        time.sleep(1)

    # Step 4: Stop PulseOutputWithTimerInterrup
    timerPulseCtrl.enabled = False

    # Step 5: Logout from server.
    #timerPulseCtrl.logout()
    
    # Step 6: Close device and release any allocated resource
    timerPulseCtrl.dispose()

    return 0


if __name__ == "__main__":
    AdvTimerPulse()
