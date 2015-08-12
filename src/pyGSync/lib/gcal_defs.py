# Copyright (c) 2008 Roi Dayan
# This file is part of the pyGSync project.
# http://pygsync.googlecode.com

import time, sys
import mycal
from settings import *
from interface import *

rx_time=None
def _loadre():
    global rx_time
    if rx_time==None:
        global re, rx_fullday, rx_intchar
        import re
        rx_time=re.compile('(\d\d\d\d)-?(\d\d)-?(\d\d)T(\d\d):?(\d\d):?(\d\d)')
        #rx_timedt=re.compile('(\d\d\d\d)(\d\d)(\d\d)T(\d\d)(\d\d)(\d\d)')
        rx_fullday=re.compile('^\d\d\d\d-\d\d-\d\d$')
        rx_intchar=re.compile('^([0-9]+)([A-Z]+)$')

#zone can be hh:mm to add to timestr when converting
def str2time(timestr,zone=None):
    _loadre()
    #start_time = time.strptime(ent['startTime'].split('.000')[0]+' GMT','%Y-%m-%dT%H:%M:%S %Z')
    if len(timestr.split('T'))==1:
        timestr+='T00:00:00'
    timestr1=rx_time.match(timestr)
    timestr=timestr1.groups()
    timeint=map(int,timestr+(0,0,0))
    if zone!=None:
        zone=zone.split(':')
        timeint[3]+=int(zone[0])
        timeint[4]+=int(zone[1])
    timefloat = time.mktime(timeint)
    return timefloat

#entry found and already updated.
FOUND=1
#entry does not exists.
NOT_FOUND=2
#time diffrences and calendar updated with the entry (modified last) times.
UPDATED=3
#time diffrences and calendar not updated (calendar entry modified last).
NOT_UPDATED=4

#phoneEntries=mycal.readPhoneEntries(range[0],range[1])
def update_phone_entry(ge, pcal):
    #start_time = str2time(ent['startTime'])
    #end_time = str2time(ent['endTime'])
    dblist = pcal.daily_instances(ge['startTime'],appointments=1,events=1)
    for item in dblist:
        pe = pcal.__getitem__(item['id'])
        if ge['title']==pe.content:
            log('ge: %s , pe: %s' %(ge['updated'],pe.last_modified))
            if ge['startTime']==pe.start_time and ge['endTime']==pe.end_time:
                return FOUND
            elif ge['updated']>pe.last_modified:
                pe.set_time(ge['startTime'],ge['endTime'])
                return UPDATED
            elif ge['updated']<pe.last_modified:
                return NOT_UPDATED
    #ugly check till they fix it
    #res=exists_ugly_lastday(ge, pcal)
    #if res!=False:
    #    return res
    return NOT_FOUND

#ugly workarround for daily/monthly skipping last day of the month
#will check days 28,29,30,31
def exists_ugly_lastday(ge, pcal):
    day=ge['startTime']
    if time.gmtime(day)[2]<28:
        return False
    st=day-24*60*60
    en=day+24*60*60
    log('ugly_lastday: %s -> %s' %(st,en))
    #find_instances fails on long text searches so i'll cut it to 10 chars
    srch=ge['title'][0:10]
    dblist=pcal.find_instances(st,en,srch)
    for item in dblist:
        pe = pcal.__getitem__(item['id'])
        if ge['title']==pe.content:
            if ge['startTime']==pe.start_time and ge['endTime']==pe.end_time:
                return FOUND
            elif ge['updated']>pe.last_modified:
                pe.set_time(ge['startTime'],ge['endTime'])
                return UPDATED
            elif ge['updated']<pe.last_modified:
                return NOT_UPDATED
    return NOT_FOUND

def fullday(start,end):
    #_loadre()
    #if rx_fullday.match(date):
    #    return True
    #return False
    if start-end==86400:
        return True
    return False

#convert timestr to float
def convertGoogleTimes(gcale):
    zone=gcale[0]['startTime'].split('+')[-1]
    if zone==gcale[0]['startTime']:
        zone=None
    log('zone: %s' %zone)
    for ge in gcale:
        ge['startTime']=str2time(ge['startTime'])
        ge['endTime']=str2time(ge['endTime'])
        ge['updated']=str2time(ge['updated'],zone)

def testme(gcale):
    import calendar
    pcal = calendar.open()
    count_skip=0
    count_adds=0
    count_updates=0
    count_recur=0
    count_canceled=0
    convertGoogleTimes(gcale)
    for ge in gcale:
        log2(ge['title'])
        if 'recurrence' in ge:
            count_recur+=1
            log2(ge['title']+'->recurrence'+'\n')
        elif ge['status']=='canceled':
            #originalEvent
            count_canceled+=1
        else:
            #start_time = str2time(ent['startTime'])
            #end_time = str2time(ent['endTime'])
            #log2(ent['title']+'->'+ent['startTime']+'\n')
            res=update_phone_entry(ge,pcal)
            #if not entry_exists(pcal,start_time,ent['title']):
            if res==NOT_FOUND:
                if fullday(ge['startTime'],ge['endTime']) and settings['sync_fullday']=='Event':
                    new=pcal.add_event()
                else:
                    new=pcal.add_appointment()
                new.content = ge['title']
                if 'where' in ge:
                    new.location = ge['where']
                #new.set_time(start_time, end_time)
                new.set_time(ge['startTime'],ge['endTime'])
                new.commit()
                count_adds+=1
            elif res==UPDATED:
                count_updates+=1
            else:
                count_skip+=1
    #msg("done. skipped:"+str(count_skip)+" / canceled:"+str(count_canceled)+
    #    " / added:"+str(count_add)+" / recur:"+str(count_recur))
    return (count_adds, count_updates)

def make_repeat(recurence):
    stopfor=False
    item={}
    for line in recurence:
        if not stopfor:
            if line.startswith('DTSTART'):
                item['dtstart']=line.split(':')[1]
            elif line.startswith('DTEND'):
                item['dtend']=line.split(':')[1]
            elif line.startswith('DURATION'):
                item['duration']=line.split(':')[1]
            elif line.startswith('RRULE'):
                rrule=line.split(':')[1].split(';')
                item['rrule']={}
                for rline in rrule:
                    ritem=rline.split('=')
                    item['rrule'][ritem[0]]=ritem[1]
            elif line.startswith('BEGIN'):
                stopfor=True
    #only supporting daily and weekly for now, added monthly
    SUPPORT=['DAILY', 'WEEKLY', 'MONTHLY']
    if not SUPPORT.__contains__(item['rrule']['FREQ']):
        raise MyError('FREQ NOT SUPPORTED YET')
    if 'UNTIL' not in item['rrule']:
        raise MyError('not supporting forever events')
    if 'INTERVAL' not in item['rrule']:
        item['rrule']['INTERVAL']=1
    repeat={'type': item['rrule']['FREQ'].lower(), 'exceptions': None,
            'start': str2time(item['dtstart']), 'end': str2time(item['rrule']['UNTIL']),
            'interval': item['rrule']['INTERVAL']}
    if repeat['type']=='daily':
        return repeat
    DAYS=['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    bydays=[]
    if 'BYDAY' in item['rrule']:
        for d in item['rrule']['BYDAY'].split(','):
            d=rx.intchar.match(d).groups()
            bydays.append({'week': d[0], 'day': DAYS.index(d[1])})
        repeat['days']=bydays
        repeat['type']='monthly_by_days'
        return repeat
    if 'BYMONTHDAY' in item['rrule']:
        repeat['type']='monthly_by_dates'
        repeat['days']=[item['rrule']['BYMONTHDAY']]
        return repeat
    raise MyError('ERROR FREQ - MISSING SUPPORT')
