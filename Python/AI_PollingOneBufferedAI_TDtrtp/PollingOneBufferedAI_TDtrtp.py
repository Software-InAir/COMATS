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
*    PollingOneBufferedAI_TDtrtp.py
*
* Example Category:
*    AI
*
* Description:
*    This example demonstrates how to use Polling One Buffered AI with Trigger
*    delay to Start and delay to stop function.
*
* Instructions for Running:
*    1. Login the edge by hostName. If you'd like to handle a local device 
*       (i.e. USB or PCI/PCIe interfaced device in your PC), please bypass this
*       step.
*    2. Set the 'deviceDescription' which can get from system device manager for
*       opening the device.
*    3. Set the 'profilePath' to save the profile path of being initialized
*       device.
*    4. Set the 'startChannel' as the first channel for scan analog samples
*    5. Set the 'channelCount' to decide how many sequential channels to scan
*       analog samples.
*    6. Set the 'sectionLength' as the length of data section for Buffered AI.
*    7. Set the 'sectionCount' as the count of data section for Buffered AI.
*    8. Set 'trigger parameters' to decide trigger property.
* I/O Connections Overview:
*    Please refer to your hardware reference manual.
*
******************************************************************************/
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.path.pardir)))

from Automation.BDaq import *
from Automation.BDaq.WaveformAiCtrl import WaveformAiCtrl
from Automation.BDaq.BDaqApi import AdxEnumToString, BioFailed

# Configure the following parameters before running the demo
deviceDescription = "PCIE-1810,BID#0"
profilePath = u"../../profile/PCIE-1810.xml"

startChannel = 0
channelCount = 2

sectionLength = 1024
sectionCount = 1

# user buffer size should be equal or greater than raw data buffer length,
# because data ready count is equal or more than smallest section of raw data
# buffer and up to raw data buffer length. users can set 'USER_BUFFER_SIZE'
# according to demand.
USER_BUFFER_SIZE = channelCount * sectionLength * sectionCount

# Set trigger parameters
triggerAction = TriggerAction.DelayToStart
triggerEdge = ActiveSignal.RisingEdge
triggerDelayCount = 1000
triggerLevel = 3.0

# Set trigger1 parameters
trigger1Action = TriggerAction.DelayToStop
trigger1Edge = ActiveSignal.RisingEdge
trigger1DelayCount = 1000
trigger1Level = 3.0

def AdvPollingOnBufferedAI_TDtrtp():
    ret = ErrorCode.Success

    # Step 1: Create a 'WaveformAiCtrl' for buffered AI function
    # Login an Edge Server by hostname for remote control
    # Select a device by device number pr device description and specify the
    # access mode.
    # In this example we use ModeWrite mode so that we can use fully control the
    # device,
    # including configuring, sampling, etc
    wfAiCtrl = WaveformAiCtrl(deviceDescription)
    #wfAiCtrl = WaveformAiCtrl(deviceDescription, "IDAQ974Bid00")
	
    for _ in range(1):
        # Loads a profile to initialize the device
        wfAiCtrl.loadProfile = profilePath

        if wfAiCtrl.features.triggerCount < 1:
            print("The device does not supported this demo!")
            break

        # Step 2: Set necessary parameters for Buffered AI operation
        # get the Conversion instance and set the start channel and scan channel
        # number
        wfAiCtrl.conversion.channelStart = startChannel
        wfAiCtrl.conversion.channelCount = channelCount

        # get the record instance and set record count and section length
        # The sectionCount is nonzero value, which means 'One Buffered' mode.
        wfAiCtrl.record.sectionCount = sectionCount
        wfAiCtrl.record.sectionLength = sectionLength

        # Step 3: Trigger parameters setting
        trgCount = wfAiCtrl.features.triggerCount
        if trgCount:
            # ##################################################################
            # The different kinds of device have different trigger source. The
            # details see manul.
            # In this example, we use the PCIE-1810 and set 'SigExtDigClock' as
            # the default trigger source.
            ####################################################################
            wfAiCtrl.trigger[0].source = wfAiCtrl.features.getTriggerSources(0)[1] # To PCIE-1810, the 1 means 'SigExtDigClock'.

            wfAiCtrl.trigger[0].action = triggerAction
            wfAiCtrl.trigger[0].delayCount = triggerDelayCount
            wfAiCtrl.trigger[0].edge = triggerEdge
            wfAiCtrl.trigger[0].level = triggerLevel
        if trgCount > 1:
            wfAiCtrl.trigger[1].source = wfAiCtrl.features.getTriggerSources(1)[1]

            wfAiCtrl.trigger[1].action = trigger1Action
            wfAiCtrl.trigger[1].delayCount = trigger1DelayCount
            wfAiCtrl.trigger[1].edge = trigger1Edge
            wfAiCtrl.trigger[1].level = trigger1Level
            
        # Step 4: The acquisition has been started
        print("Polling finite acquisition is in progress!")
        ret = wfAiCtrl.prepare()
        if BioFailed(ret):
            break
        
        ret = wfAiCtrl.start()
        if BioFailed(ret):
            break

        # Step 5: GetData with Polling Style
        result = wfAiCtrl.getData(USER_BUFFER_SIZE, -1)
        ret, returnedCount, data, = result[0], result[1], result[2]
        if BioFailed(ret):
            break

        print("Polling One Buffered AI get data count is %d" % returnedCount)
        if ret == ErrorCode.Success:
            print("The first sample each channel are: ")
            for i in range(channelCount):
                print("channel %d: %10.6f " % (i + startChannel, data[i]))
                
        delayCount = wfAiCtrl.trigger[trgCount - 1].delayCount
        triggerPointIndex = returnedCount // channelCount - delayCount
        print("trigger point each channel: %d" % triggerPointIndex)
        
        print("Acquisition has completed!")

        # Step 6: stop the operation if it is running
        ret = wfAiCtrl.stop()

        # Step 7: release any allocated resource before quit
        wfAiCtrl.release()

    # Step 8: Logout from server.
    #wfAiCtrl.logout()
    
    # Step 9: close device, release any allocated resource before quit
    wfAiCtrl.dispose()

    # if something wrong in this execution, print the error code on screen for
    # tracking
    if BioFailed(ret):
        enumStr = AdxEnumToString("ErrorCode", ret.value, 256)
        print("Some error occurred. And the last error code is %#x. [%s]" %
              (ret.value, enumStr))

    return 0


if __name__ == '__main__':
    AdvPollingOnBufferedAI_TDtrtp()
