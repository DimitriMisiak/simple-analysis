#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Read the SAMBA binary file, and extract the data stream along with
useful other metadata.

@author: misiak
"""

import re
import numpy as np

def read_ac_data(bin_path, channel):
    """ Read the SAMBA output cointaining the AC datastream.
    Return the sampling frequency and the raw_stream in volts.

    Parameters
    ==========
    bin_path : str
        Path of the binary file.

    channel : int
        Index of the channel to be read (usually 0 or 1)

    Return
    ======
    fe : int
        Sampling frequency of the stream

    l1 : numpy.ndarray
        Data stream in volts.
    """

    ElecKind = 'AC'

    ########## Extract run information from argument ##########
    PathRunFile = str(bin_path) #Directory with data
    split_index = PathRunFile.rfind('/') #Find last '/' to extract run name

    PathRun = PathRunFile[:split_index] #Path to binary file
    File = PathRunFile[split_index+1:]    #Binary file selected

#    ElecKind = str(sys.argv[2]) #AC or DC electronics

    if ElecKind == "AC":
        split_index = PathRun.rfind('/')
        Run = PathRun[split_index+1:] #Run name
    if ElecKind == "DC":
        split_index = File.rfind('.')
        Run = File[:split_index] #Run name

    print ' *  Path to binary file: ',PathRun
    print ' *  Run name: ',Run
    print ' *  Selected binary file: ',File

    ########## Input informations ##########
    print '\n * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *'
    ########
    ## DC ##
    ########
    if ElecKind == "DC":
        findchannel = re.findall('.BIN(\d+)', File)
        channel = int(findchannel[0]) #Channel number
        NumberChal = 1
        NumberDet = 1

        voie = channel

        det = raw_input(' *  Detector name: ')
        channel = 'NTD'

        fe = input(' *  Acquisition sampling frequency [Hz]: ')
        fe = float(fe)
        r = input(' *  Dynamic range (Vmax-Vmin) [V]: ')
        Gain = input(' *  Amplifier gain: ')

        ########## Load data from binary File ##########
        data = open(str(PathRun)+"/"+str(File))
        print ' *  Load binary file...'
        l0 = np.fromfile(data, dtype=np.int16, count=-1)

    ########
    ## AC ##
    ########
    if ElecKind == "AC":
        nPart = 0
        nOct = 0

        ## Get information for the selected partition in _log file
        for line in open(str(PathRun)+'/'+str(Run)+'_log'):
            if 'Creation' in line and 'streams/' in line and str(File) in line: ##Find selected partition in line
                nPart = 1
            if nPart==1 and nOct==0 and 'donnees' in line and 'commencent' in line:
                value_Line_octet = re.findall('octet (\d+)', line)
                Octet_offset = int(value_Line_octet[0]) #Octet where binary data start
                nOct = 1

            if nOct==1 and 'octets' in line and 'total' in line: #Total octet saved for the selected partition
                value_Line_TotOctet = re.findall('soit (\d+) octets', line)
                Total_Octet = int(value_Line_TotOctet[0])

            if nPart==1 and nOct == 1 and 'Creation' in line and 'streams/' in line and str(File) not in line:
                nPart = 2
                nOct = 2
            if nPart==1 and nOct == 1 and 'Creation' in line and 'events/' in line and str(Run) in line and '_0'+str(File[len(File)-2:]) in line:
                nPart = 1
                nOct = 1

        ## Get information from the header
        ListDetector = []
        ListChannel = []
        ListChannel_d = []
        ListChannel_gainVoieVol = []

        Demod = 0

        for line in open(str(PathRun)+'/'+str(File)):
            if '* Detecteur' in line: #List of detectors
                DetName = line[12]
                for i in range(13,len(line)): #Extract detector name without NULL character
                    if line[i] != ' ':
                        DetName = DetName + line[i]
                ListDetector.append(DetName)

            #Sampling frequency informations
            if 'd2A :' in line or 'd2B :' in line or 'd2C :' in line:
                value_Line_freqD2 = re.findall('= (\d+)', line)
                freqD2 = float(value_Line_freqD2[0]) #Frequency D2

            if 'd3A :' in line or 'd3B :' in line or 'd3C :' in line:
                value_Line_freqD3 = re.findall('= (\d+)', line)
                freqD3 = float(value_Line_freqD3[0]) #Frequency D3

            #Channel list
            if '* Voie' in line:
                split_index = line.find('"')
                line2 = line[split_index+1:]
                split_index = line2.find('"')
                line2 = line2[:split_index]

                if ' ' in line2:
                    split_index = line2.find(' ')
                    ChanName = line2[:split_index]
                    DetChanName = line2[split_index+1:]

                else:
                    ChanName =     line2[:split_index]
                    DetChanName = ListDetector[0]

                    DetChanName = DetChanName[:len(DetChanName)-1]

                ListChannel_d.append(DetChanName)
                ListChannel.append(ChanName)

            if 'Voie.au-vol =' in line and '= demodulation' in line: #Identify if demodulated measurement
                Demod = 1

            if 'Voie.au-vol.gain' in line: #Gain Voie au Vol
                value_Line_gainVol = re.findall('= (\d+)', line)

                if Demod == 1:
                    ListChannel_gainVoieVol.append(float(value_Line_gainVol[0]))
                if Demod == 0:
                    ListChannel_gainVoieVol.append(1)

            if '* Donnees' in line:
                break #Stop before binary part

        ##Sampling frequency
        if Demod == 0:
            fe = freqD2 * freqD3
        if Demod == 1:
            fe = freqD3

        ## Get channel gain in _log file
        ListChannel_Gain = []
        ListChannel_Gain = np.zeros(len(ListChannel))

        ng = 0

        for line in open(str(PathRun)+'/'+str(Run)+'_log'):
            if 'gains' and 'ADU(nV)' in line: ##Start of gain table
                ng = 1

            if ng == 1 and '|____________________________________________________________________________________|' in line: ##End of gain table
                ng = 0

            if ng == 1:
                for i in range(0,len(ListChannel)):
                    if ListChannel[i] in line and ListChannel_d[i] in line and 'x' in line:
                        indes_split = line.find('x')
                        line2 = line[indes_split+4:indes_split+14]

                        value_Line_Gain = re.findall('-(\d+\.\d+)', line2)

                        if not value_Line_Gain:
                            value_Line_Gain = re.findall('(\d+\.\d+)', line2)

                        ##
                        if Demod == 1:
                            value_Gain = float(value_Line_Gain[0]) / 2. / ListChannel_gainVoieVol[i]
                        if Demod == 0:
                            value_Gain = float(value_Line_Gain[0]) / ListChannel_gainVoieVol[i]

                        ListChannel_Gain[i] = value_Gain

        ##
        NumberChal = len(ListChannel)
        NumberDet = len(ListDetector)

        length_l0 = (Total_Octet - Octet_offset) / 2. / NumberChal ##Estimate total time of the acquisition

        ########## Load data from binary part ##########
        print ' *  Load binary file...'
        l0 = np.memmap(str(PathRun)+'/'+str(File), dtype='int16', mode='r', offset=Octet_offset, shape=(int(length_l0),NumberChal))
        ##End AC
    print ' * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *\n'
    ########## Introduction to the measurement ##########
    total_time = len(l0)/fe

    print ' *  File ', File, ', Number of detectors ', NumberDet, ', Number of channels ', NumberChal
    print ' *  Sampling frequency, fe = ',fe, 'Hz'
    print ' *  Total time = ', "%.3f" % total_time, 'sec (', "%.3f" % (total_time/3600.),'hrs )'
    if ElecKind == 'AC':
        print ' *  Octet offset = ', Octet_offset
        if Demod == 1:
            print ' *  Demodulated measurement'

    print '\n * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *'
    ########## Data to treat ##########
#    Select_time = input(' *  Consider all acquisition time (1-Yes ; 0-No) ? ')
    Select_time = 1

    if Select_time == 0:
        Start_time = input(' *  Start time [s]: ')
        End_time = input(' *  End time [s]: ')

    ########## Time window size ##########
#    dt = input(' *  Size of time division of the stream (time window [s]): ')

    ## Heat channel
    AnaHeat_d = []
    AnaHeat = []
    AnaHeat_Gain = []

    if NumberChal == 1:
        if ElecKind == 'AC':
            AnaHeat_d = ListChannel_d
            AnaHeat = ListChannel
            AnaHeat_Gain = ListChannel_Gain

            Select_voie = 0

        if ElecKind == 'DC':
            AnaHeat_d.append(det)
            AnaHeat.append(channel)
            AnaHeat_Gain.append(float(Gain))

        Select_Channel = 0

    if NumberChal > 1:
#        Select_Channel = input(' *  Analyse all heat channels (1-Yes ; 0-No) ? ')
        Select_Channel = 0

        if Select_Channel == 1:
            AnaHeat_d = ListChannel_d
            AnaHeat = ListChannel
            AnaHeat_Gain = ListChannel_Gain

        if Select_Channel == 0:
            print ' *  Choose one heat channel:'
            for i in range(0,len(ListChannel)):
                print '    ->', i, ListChannel_d[i], ListChannel[i]

#            Select_voie = input(' *  ID of selected channel: ')
            Select_voie = channel

            AnaHeat_d.append(ListChannel_d[Select_voie])
            AnaHeat.append(ListChannel[Select_voie])
            AnaHeat_Gain.append(ListChannel_Gain[Select_voie])

    ## Automatic running method or manual input
#    Select_Auto = input(' *  Automatic selection method (1-Yes ; 0-No) ? ')

    print '\n * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *'
#    ##############################################################
#    ########## Creation of directory to save results ##########
#    Path2 = str(PathRun)+'/../Analysis_HAPPy_'+str(Run)
#    if ElecKind == 'AC':
#        Path2 = str(PathRun)+'/../../Analysis_HAPPy_'+str(Run)
#
#    if not os.path.exists(str(Path2)):
#        os.mkdir(str(Path2))
#
#    File_id = File
#    if ElecKind == 'DC':
#        File_id = Run
    ##############################################################
    for ich in range(0,len(AnaHeat)):
        if ElecKind == 'AC' and Select_Channel == 0:
            voie = Select_voie
        if ElecKind == 'AC' and Select_Channel == 1:
            voie = ich
        if ElecKind == 'DC':
            voie = voie

        ## Only heat channels
        if 'chal' in AnaHeat[ich] or 'lumiere' in AnaHeat[ich] or 'NTD' in AnaHeat[ich]:
            print '\n * ',AnaHeat_d[ich], 'channel', voie, AnaHeat[ich],' gain=',AnaHeat_Gain[ich]
            Gain = AnaHeat_Gain[ich]
            det = AnaHeat_d[ich]
            chan = AnaHeat[ich]

            ##DC
            if ElecKind == 'DC' and Select_time == 1:
                l1 = l0 / (2.**16) *(r/Gain)
            if ElecKind == 'DC' and Select_time == 0:
                l1 = l0[int(Start_time*fe):int(End_time*fe)] / (2.**16) *(r/Gain)

            ##AC
            if ElecKind == 'AC' and Select_time == 1:
                l1 = l0[:,voie] * Gain * 1e-9
            if ElecKind == 'AC' and Select_time == 0:
                l1 = l0[int(Start_time*fe):int(End_time*fe),voie] * Gain * 1e-9

    return fe, l1