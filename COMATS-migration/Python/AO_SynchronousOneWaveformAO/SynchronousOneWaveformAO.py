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
*    SynchronousOneWaveformAO.py
*
* Example Category:
*    AO
*
* Description:
*    This example demonstrates how to use Synchronous One Waveform AO voltage
*    function.
*
* Instructions for Running:
*    1  Login the edge by hostName. If you'd like to handle a local device 
*       (i.e. USB or PCI/PCIe interfaced device in your PC), please bypass this
*       step.
*    2  Set the 'deviceDescription' for opening the device.
*    3  Set the 'profilePath' to save the profile path of being initialized
*       device.
*    4  Set the 'channelStart' as the first channel for analog data Output.
*    5  Set the 'channelCount' to decide how many sequential channels to output
*       analog data.
*
* I/O Connections Overview:
*    Please refer to your hardware reference manual.
*
******************************************************************************/
"""
import math, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.path.pardir)))

from Automation.BDaq import *
from Automation.BDaq.Utils import CreateArray
from Automation.BDaq.BufferedAoCtrl import BufferedAoCtrl
from Automation.BDaq.BDaqApi import AdxGetValueRangeInformation, BioFailed, AdxEnumToString

ONE_WAVE_POINT_COUNT = 2048

samples = ONE_WAVE_POINT_COUNT

deviceDescription = "DemoDevice,BID#0"
profilePath = u"../../profile/DemoDevice.xml"

startChannel = 0
channelCount = 2

class WaveStyle(object):
    Sine = 0
    Sawtooth = 1
    Square = 2

def GenerateWaveform(bfdAoCtrlObj, channelStart, channelCount, samplesCount, waveStyle):
    ret = ErrorCode.Success
    waveBuffer = [0.0] * samplesCount

    # ranges is a MathInterval array which size is 64
    mathIntervalRanges = CreateArray(MathInterval, 64)
    channelCountMax = bfdAoCtrlObj.features.channelCountMax

    for i in range(channelCountMax):
        aoChannel = bfdAoCtrlObj.channels[i]
        valRange = aoChannel.valueRange

        if ValueRange.V_ExternalRefBipolar == valRange or valRange == ValueRange.V_ExternalRefUnipolar:
            if bfdAoCtrlObj.features.externalRefAntiPolar:
                if valRange == ValueRange.V_ExternalRefBipolar:
                    referenceValue = aoChannel.extRefBipolar
                    if referenceValue >= 0:
                        mathIntervalRanges[i].Max = referenceValue
                        mathIntervalRanges[i].Min = 0 - referenceValue
                    else:
                        mathIntervalRanges[i].Max = 0 - referenceValue
                        mathIntervalRanges[i].Min = referenceValue
                else:
                    referenceValue = aoChannel.extRefUnipolar
                    if referenceValue >= 0:
                        mathIntervalRanges[i].Max = 0
                        mathIntervalRanges[i].Min = 0 - referenceValue
                    else:
                        mathIntervalRanges[i].Max = 0 - referenceValue
                        mathIntervalRanges[i].Min = 0
            else:
                if valRange == ValueRange.V_ExternalRefBipolar:
                    referenceValue = aoChannel.extRefBipolar
                    if referenceValue >= 0:
                        mathIntervalRanges[i].Max = referenceValue
                        mathIntervalRanges[i].Min = 0 - referenceValue
                    else:
                        mathIntervalRanges[i].Max = 0 - referenceValue
                        mathIntervalRanges[i].Min = referenceValue
                else:
                    referenceValue = aoChannel.extRefUnipolar
                    if referenceValue >= 0:
                        mathIntervalRanges[i].Max = referenceValue
                        mathIntervalRanges[i].Min = 0
                    else:
                        mathIntervalRanges[i].Max = 0
                        mathIntervalRanges[i].Min = referenceValue
        else:
            ret = AdxGetValueRangeInformation(valRange, 0, None, mathIntervalRanges[i], None)
            if BioFailed(ret):
                return ret, None

    # generate waveform data and put them into the buffer which the parameter
    # 'waveBuffer' give in, the Amplitude these waveform
    oneWaveSamplesCount = samplesCount // channelCount
    waveBufferIndex = 0

    for i in range(oneWaveSamplesCount):
        for j in range(channelStart, channelStart + channelCount):
            channel = j % channelCountMax
            amplitude = (mathIntervalRanges[channel].Max - mathIntervalRanges[channel].Min) / 2
            offset = (mathIntervalRanges[channel].Max + mathIntervalRanges[channel].Min) / 2

            if waveStyle == WaveStyle.Sine:
                waveBuffer[waveBufferIndex] = amplitude * (math.sin((i * 2.0 * 3.14159) / oneWaveSamplesCount)) + offset
                waveBufferIndex += 1
            elif waveStyle == WaveStyle.Sawtooth:
                if (i >= 0) and (i < (oneWaveSamplesCount / 4.0)):
                    waveBuffer[waveBufferIndex] = amplitude * (math.sin((i * 2.0 * 3.14159) / oneWaveSamplesCount)) + offset
                    waveBufferIndex += 1
                else:
                    if (i >= (oneWaveSamplesCount / 4.0)) and (i < 3 * (oneWaveSamplesCount / 4.0)):
                        waveBuffer[waveBufferIndex] = amplitude * ((2.0 * (oneWaveSamplesCount / 4.0) - i) / (oneWaveSamplesCount / 4.0)) + offset
                        waveBufferIndex += 1
                    else:
                        waveBuffer[waveBufferIndex] = amplitude * ((i - oneWaveSamplesCount) / (oneWaveSamplesCount / 4.0)) + offset
                        waveBufferIndex += 1
            elif waveStyle == WaveStyle.Square:
                if (i >= 0) and (i < (oneWaveSamplesCount / 2)):
                    waveBuffer[waveBufferIndex] = amplitude * 1 + offset
                    waveBufferIndex += 1
                else:
                    waveBuffer[waveBufferIndex] = amplitude * (-1) + offset
                    waveBufferIndex += 1
            else:
                print("invalid wave style, generate waveform error!")
                ret = ErrorCode.ErrorUndefined
    return ret, waveBuffer

def AdvBufferedAO():
    ret = ErrorCode.Success

    # Step 1: Create a BfdAoCtrl for buffered AO function
    # Login an Edge Server by hostname for remote control
    # Select a device by device number or device description and specify the
    # access mode.
    # In the example we use ModeWrite mode so that we can fully control the
    # device, including configuring, sampling, etc.
    bfdAoCtrlObj = BufferedAoCtrl(deviceDescription)
    #bfdAoCtrlObj = BufferedAoCtrl(deviceDescription, "IDAQ974Bid00")

    for loop in range(1):
        # Loads a profile to initialize the device
        bfdAoCtrlObj.loadProfile = profilePath

        # Step 2: Set necessary parameters
        # get scan channel instance and set the start channel number and scan
        # channel count
        bfdAoCtrlObj.scanChannel.channelStart = startChannel
        bfdAoCtrlObj.scanChannel.channelCount = channelCount

        # set samples number
        bfdAoCtrlObj.scanChannel.samples = samples

        # Step 3: prepare the buffered AO
        ret = bfdAoCtrlObj.prepare()
        if BioFailed(ret):
            break

        # Generate waveform data
        ret, waveformBuf = GenerateWaveform(bfdAoCtrlObj, startChannel,
                                            channelCount,
                                            channelCount * ONE_WAVE_POINT_COUNT,
                                            WaveStyle.Sine)
        if BioFailed(ret):
            break

        ret = bfdAoCtrlObj.setData(channelCount * ONE_WAVE_POINT_COUNT,
                                   waveformBuf)
        if BioFailed(ret):
            break

        # Step 4: Start a Synchronous One Waveform AO, 'Synchronous' indicates
        # using synchronous mode, which means the method will not return
        # until the operation is completed.
        print("Synchronous finite acquisition is in progress.")
        print("Please wait, until acquisition complete.")
        ret = bfdAoCtrlObj.runOnce()
        if BioFailed(ret):
            break
        
        print("Buffered AO is over!")

        # Step 5: Release any allocated resource
        bfdAoCtrlObj.release()

    # Step 6: Logout from server.
    #bfdAoCtrlObj.logout()

    # Step 7: Close device, release any allocated resource
    bfdAoCtrlObj.dispose()

    if BioFailed(ret):
        enumStr = AdxEnumToString("ErrorCode", ret.value, 256)
        print("Some error occurred. And the last error code is %#x. [%s]" %
              (ret.value, enumStr))

    return 0


if __name__ == '__main__':
    AdvBufferedAO()
