#!/usr/bin/python -u
# See the file 'LICENSE' for copying permission.
# Author: Sebastian Garcia. eldraco@gmail.com , sebastian.garcia@agents.fel.cvut.cz

import sys
from datetime import datetime
from datetime import timedelta
import argparse
import time
from os.path import isfile, join
import json
from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
#import pandas as pd

version = '0.1'

timewindows = {}
timeStampFormat = '%Y-%m-%dT%H:%M:%S.%f'
csvfile = ''



###################
# TimeWindow
class TimeWindow(object):
    """ Store info about the time window """
    def __init__(self, hourstring):
        self.hour = hourstring
        self.start_time = hourstring
        self.categories = {}
        self.severities = {}
        self.severities[1] = 0
        self.severities[2] = 0
        self.severities[3] = 0
        self.severities[4] = 0
        self.categories['Not Suspicious Traffic'] = 0
        self.categories['Generic Protocol Command Decode'] = 0
        self.categories['Unknown Traffic'] = 0
        self.categories['Potentially Bad Traffic'] = 0
        self.categories['Attempted Information Leak'] = 0
        self.categories['Information Leak'] = 0
        self.categories['Large Scale Information Leak'] = 0
        self.categories['Attempted Denial of Service'] = 0
        self.categories['Denial of Service'] = 0
        self.categories['Attempted User Privilege Gain'] = 0
        self.categories['Access to a Potentially Vulnerable Web Application'] = 0
        self.categories['Generic Protocol Command Decode'] = 0
        self.categories['Detection of a Non-Standard Protocol or Event'] = 0
        self.categories['Detection of a Denial of Service Attack'] = 0
        self.categories['Detection of a Network Scan'] = 0
        self.categories['A Client was Using an Unusual Port'] = 0
        self.categories['A Network Trojan was Detected'] = 0
        self.categories['A TCP Connection was Detected'] = 0
        self.categories['A System Call was Detected'] = 0
        self.categories['An Attempted Login Using a Suspicious Username was Detected'] = 0
        self.categories['A Suspicious Filename was Detected'] = 0
        self.categories['A Suspicious String was Detected'] = 0
        self.categories['Executable Code was Detected'] = 0
        self.categories['Decode of an RPC Query'] = 0
        self.categories['Successful Administrator Privilege Gain'] = 0
        self.categories['Attempted Administrator Privilege Gain'] = 0
        self.categories['Successful User Privilege Gain'] = 0
        self.categories['Unsuccessful User Privilege Gain'] = 0
        self.categories['Inappropriate Content was Detected'] = 0
        self.categories['Generic ICMP event'] = 0
        self.categories['Misc Attack'] = 0
        self.categories['Misc activity'] = 0
        self.categories['Web Application Attack'] = 0
        self.categories['Attempt to Login By a Default Username and Password'] = 0
        self.categories['Potential Corporate Privacy Violation'] = 0
        self.signatures = {}
        self.src_ips = {}
        self.dst_ips = {}

    def add_alert(self, category, severity, signature, src_ip, dst_ip):
        try:
            self.categories[category] += 1
        except KeyError:
            self.categories[category] = 1
        try:
            self.severities[int(severity)] += 1
        except KeyError:
            self.severities[int(severity)] = 1
        try:
            self.signatures[signature] += 1
        except KeyError:
            self.signatures[signature] = 1
        try:
            self.src_ips[src_ip] += 1
        except KeyError:
            self.src_ips[src_ip] = 1
        try:
            self.dst_ips[dst_ip] += 1
        except KeyError:
            self.dst_ips[dst_ip] = 1

    def get_csv(self):
        #return '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}'.format(str(self.hour), len(self.categories), len(self.severities), len(self.signatures), len(self.src_ips), len(self.dst_ips))
        return '{},{},{},{},{},{},{},{},{},{},{}'.format(str(self.hour), len(self.categories), len(self.signatures), len(self.src_ips), len(self.dst_ips), self.severities[self.severities.keys()[0]], self.severities[self.severities.keys()[1]], self.severities[self.severities.keys()[2]], self.severities[self.severities.keys()[3]], self.categories['Not Suspicious Traffic'], self.categories['Generic Protocol Command Decode'])
        #, Unknown Traffic, Potentially Bad Traffic, Attempted Information Leak, Information Leak, Large Scale Information Leak, Attempted Denial of Service, Denial of Service, Attempted User Privilege Gain, Unsuccessful User Privilege Gain, Successful User Privilege Gain, Attempted Administrator Privilege Gain, Successful Administrator Privilege Gain, Decode of an RPC Query, Executable Code was Detected, A Suspicious String was Detected, A Suspicious Filename was Detected, An Attempted Login Using a Suspicious Username was Detected, A System Call was Detected, A TCP Connection was Detected, A Network Trojan was Detected, A Client was Using an Unusual Port, Detection of a Network Scan, Detection of a Denial of Service Attack, Detection of a Non-Standard Protocol or Event, Generic Protocol Command Decode, Access to a Potentially Vulnerable Web Application, Web Application Attack, Misc activity, Misc Attack, Generic ICMP event, Inappropriate Content was Detected, Potential Corporate Privacy Violation, Attempt to Login By a Default Username and Password' + '\n')

    def __repr__(self):
        return 'TW: {}. #Categories: {}. #Signatures: {}. #SrcIp: {}. #DstIP: {}. #Severities: 1:{},2:{},3:{},4:{}'.format(str(self.hour), len(self.categories), len(self.signatures), len(self.src_ips), len(self.dst_ips), self.severities[self.severities.keys()[0]], self.severities[self.severities.keys()[1]], self.severities[self.severities.keys()[2]], self.severities[self.severities.keys()[3]])

def get_tw(col_time):
    """
    """
    timestamp = datetime.strptime(col_time, timeStampFormat)
    # Get the closest down time rounded
    round_down_timestamp = roundTime(timestamp,timedelta(minutes=args.width), 'down')
    str_round_down_timestamp = round_down_timestamp.strftime(timeStampFormat)
    try:
        tw = timewindows[str_round_down_timestamp]
        if args.verbose > 1:
            print 'Getting an old tw {}'.format(tw)
    except KeyError:
        # New tw
        # Get the previous TW id
        prev_tw_date = round_down_timestamp - timedelta(minutes=int(args.width))
        str_prev_round_down_timestamp = prev_tw_date.strftime(timeStampFormat)
        output_tw(str_prev_round_down_timestamp)
        tw = TimeWindow(str_round_down_timestamp)
        tw.set_start_time = timestamp
        timewindows[str_round_down_timestamp] = tw
        if args.verbose > 2:
            print 'New tw created at {}'.format(str_round_down_timestamp)
    return tw

def output_tw(time_tw):
    """
    Print the TW
    """
    try:
        tw = timewindows[time_tw]
        if args.verbose > 1:
            print 'Printing TW that started in: {}'.format(time_tw)
        print tw
    except KeyError:
        return False
    print '\tCategories:'
    for cat in tw.categories:
        print '\t\t{}: {}'.format(cat, tw.categories[cat])
    print '\tSeverities:'
    for sev in tw.severities:
        print '\t\t{}: {}'.format(sev, tw.severities[sev])
    #print '\tSignatures:'
    #for sig in tw.signatures:
        #print '\t\t{}: {}'.format(sig, tw.signatures[sig])
    #CSV
    if args.csv:
        csvline = tw.get_csv()
        csvfile.write(csvline + '\n')
        csvfile.flush()

def plot():
    """
    """
    if args.verbose > 1:
        print 'Plotting'
    plt.figure(1)
    cat1val = []
    cat2val = []
    sev1val = []
    sev2val = []
    sev3val = []
    sev4val = []
    sigval = []
    srcipval = []
    dstipval = []
    labels = []
    #self.signatures = {}
    #self.src_ips = {}
    #self.dst_ips = {}
    #csvfile.write( 'timestamp,#categories,#signatures,#srcip,#dstip,sev1,sev2,sev3,sev4,Not Suspicious Traffic, Unknown Traffic, Potentially Bad Traffic, Attempted Information Leak, Information Leak, Large Scale Information Leak, Attempted Denial of Service, Denial of Service, Attempted User Privilege Gain, Unsuccessful User Privilege Gain, Successful User Privilege Gain, Attempted Administrator Privilege Gain, Successful Administrator Privilege Gain, Decode of an RPC Query, Executable Code was Detected, A Suspicious String was Detected, A Suspicious Filename was Detected, An Attempted Login Using a Suspicious Username was Detected, A System Call was Detected, A TCP Connection was Detected, A Network Trojan was Detected, A Client was Using an Unusual Port, Detection of a Network Scan, Detection of a Denial of Service Attack, Detection of a Non-Standard Protocol or Event, Generic Protocol Command Decode, Access to a Potentially Vulnerable Web Application, Web Application Attack, Misc activity, Misc Attack, Generic ICMP event, Inappropriate Content was Detected, Potential Corporate Privacy Violation, Attempt to Login By a Default Username and Password' + '\n')
    for tw in timewindows:
        labels.append(tw)
        cat1val.append(timewindows[tw].categories['Not Suspicious Traffic'])
        cat2val.append(timewindows[tw].categories['Generic Protocol Command Decode'])
        sev1val.append(timewindows[tw].severities[1])
        sev2val.append(timewindows[tw].severities[2])
        sev3val.append(timewindows[tw].severities[3])
        sev3val.append(timewindows[tw].severities[4])
        sigval.append(len(timewindows[tw].signatures))
        srcipval.append(len(timewindows[tw].src_ips))
        dstipval.append(len(timewindows[tw].dst_ips))
    plt.plot(cat1val, 'b-', label='Not Suspicious Traffic')
    plt.plot(cat2val, 'r-', label='Generic Protocol Command Decode')
    plt.plot(sev1val, 'c-', label='Severity 1')
    plt.plot(sev2val, 'c.', label='Severity 2')
    plt.plot(sev3val, 'c+', label='Severity 3')
    plt.plot(sev4val, 'c*', label='Severity 4')
    plt.plot(sigval, 'm-', label='Signatures')
    plt.plot(srcipval, 'm-', label='Signatures')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    #plt.xticks(range(1,len(labels)), labels)
    plt.legend(loc=0)
    plt.ylabel('Amount')
    plt.show()

def process_line(line):
    """
    """
    if args.verbose > 3:
        print 'Processing line {}'.format(line)
    json_line = json.loads(line)
    if json_line['event_type'] != 'alert':
        return False
    if args.dstnet and args.dstnet not in json_line['dest_ip']:
        return False
    if args.verbose > 2:
        print 'Accepted line {}'.format(line)
    # forget the timezone for now with split
    col_time = json_line['timestamp'].split('+')[0]
    col_category = json_line['alert']['category']
    #if not col_category:
        #pprint(json_line['alert']['signature'])
    col_severity = json_line['alert']['severity']
    col_signature = json_line['alert']['signature']
    col_srcip = json_line['src_ip']
    col_dstip = json_line['dest_ip']
    # Get the time window object
    current_tw = get_tw(col_time)
    current_tw.add_alert(col_category, col_severity, col_signature, col_srcip, col_dstip)
    return current_tw

def roundTime(dt=None, date_delta=timedelta(minutes=1), to='average'):
    """
    Round a datetime object to a multiple of a timedelta
    dt : datetime.datetime object, default now.
    dateDelta : timedelta object, we round to a multiple of this, default 1 minute.
    from:  http://stackoverflow.com/questions/3463930/how-to-round-the-minute-of-a-datetime-object-python
    """
    round_to = date_delta.total_seconds()
    if dt is None:
        dt = datetime.now()
    seconds = (dt - dt.min).seconds
    if to == 'up':
        # // is a floor division, not a comment on following line (like in javascript):
        rounding = (seconds + round_to) // round_to * round_to
    elif to == 'down':
        rounding = seconds // round_to * round_to
    else:
        rounding = (seconds + round_to / 2) // round_to * round_to
    return dt + timedelta(0, rounding - seconds, -dt.microsecond)

####################
# Main
####################
if __name__ == '__main__':  
    print 'Suricata Extractor. Version {} (https://stratosphereips.org)'.format(version)
    print

    # Parse the parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='Amount of verbosity. This shows more info about the results.', action='store', required=False, type=int, default=1)
    parser.add_argument('-e', '--debug', help='Amount of debugging. This shows inner information about the flows.', action='store', required=False, type=int, default=0)
    parser.add_argument('-f', '--file', help='Suricata eve.json file.', action='store', required=False)
    parser.add_argument('-w', '--width', help='Width of the time window to process. In minutes.', action='store', required=False, type=int, default=60)
    parser.add_argument('-d', '--dstnet', help='Destination net to monitor. Ex: 192.168 to search everything attacking 192.168.0.0/16 network', action='store', required=False)
    parser.add_argument('-c', '--csv', help='CSV output file', action='store', type=str, required=False)
    parser.add_argument('-p', '--plot', help='Plot', action='store_true', required=False)
    args = parser.parse_args()

    # Get the verbosity, if it was not specified as a parameter 
    if args.verbose < 1:
        args.verbose = 1

    # Limit any debuggisity to > 0
    if args.debug < 0:
        args.debug = 0

    # If csv
    if args.csv:
        csvfile = open(args.csv, 'w')
        # Not Suspicious Traffic
        # Unknown Traffic
        # Potentially Bad Traffic
        # Attempted Information Leak
        # Information Leak
        # Large Scale Information Leak
        # Attempted Denial of Service
        # Denial of Service
        # Attempted User Privilege Gain
        # Unsuccessful User Privilege Gain
        # Successful User Privilege Gain
        # Attempted Administrator Privilege Gain
        # Successful Administrator Privilege Gain
        # Decode of an RPC Query
        # Executable Code was Detected
        # A Suspicious String was Detected
        # A Suspicious Filename was Detected
        # An Attempted Login Using a Suspicious Username was Detected
        # A System Call was Detected
        # A TCP Connection was Detected
        # A Network Trojan was Detected
        # A Client was Using an Unusual Port
        # Detection of a Network Scan
        # Detection of a Denial of Service Attack
        # Detection of a Non-Standard Protocol or Event
        # Generic Protocol Command Decode
        # Access to a Potentially Vulnerable Web Application
        # Web Application Attack
        # Misc activity
        # Misc Attack
        # Generic ICMP event
        # Inappropriate Content was Detected
        # Potential Corporate Privacy Violation
        # Attempt to Login By a Default Username and Password
        #csvfile.write( 'timestamp,#categories,#signatures,#srcip,#dstip,sev1,sev2,sev3,sev4' + '\n')
        csvfile.write( 'timestamp,#categories,#signatures,#srcip,#dstip,sev1,sev2,sev3,sev4,Not Suspicious Traffic,Generic Protocol Command Decode' + '\n')
        #csvfile.write( 'timestamp,#categories,#signatures,#srcip,#dstip,sev1,sev2,sev3,sev4,Not Suspicious Traffic, Unknown Traffic, Potentially Bad Traffic, Attempted Information Leak, Information Leak, Large Scale Information Leak, Attempted Denial of Service, Denial of Service, Attempted User Privilege Gain, Unsuccessful User Privilege Gain, Successful User Privilege Gain, Attempted Administrator Privilege Gain, Successful Administrator Privilege Gain, Decode of an RPC Query, Executable Code was Detected, A Suspicious String was Detected, A Suspicious Filename was Detected, An Attempted Login Using a Suspicious Username was Detected, A System Call was Detected, A TCP Connection was Detected, A Network Trojan was Detected, A Client was Using an Unusual Port, Detection of a Network Scan, Detection of a Denial of Service Attack, Detection of a Non-Standard Protocol or Event, Generic Protocol Command Decode, Access to a Potentially Vulnerable Web Application, Web Application Attack, Misc activity, Misc Attack, Generic ICMP event, Inappropriate Content was Detected, Potential Corporate Privacy Violation, Attempt to Login By a Default Username and Password' + '\n')
        csvfile.flush()

    current_tw = ''
    try:
        if args.file:
            if args.verbose > 1:
                print 'Working with the file {} as parameter'.format(args.file)
            f = open(args.file)
            line = f.readline()
            while line:
                tw = process_line(line)
                if tw:
                    current_tw = tw
                line = f.readline()
            f.close()
        else:
            for line in sys.stdin:
                tw = process_line(line)
                if tw:
                    current_tw = tw
    except KeyboardInterrupt:
        pass

    ## Print last tw
    timestamp = datetime.strptime(current_tw.start_time, timeStampFormat)
    round_down_timestamp = roundTime(timestamp,timedelta(minutes=args.width), 'down')
    str_round_down_timestamp = round_down_timestamp.strftime(timeStampFormat)
    output_tw(str_round_down_timestamp)

    if args.csv:
        csvfile.close()

    if args.plot:
        plot()

