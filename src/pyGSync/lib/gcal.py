# Copyright (c) 2008 Roi Dayan
# This file is part of the pyGSync project.
# http://pygsync.googlecode.com

import time, gcal_defs, mycal
from settings import *
from interface import *

authLogin={}

def authenticate():
    global authLogin
    try:
        checkAuth()
        if not authLogin.has_key('authorization'):
            apo=set_access_point()
            if apo==None:
                syncAborted('User didnt select access point')
                return
            authLogin['apo']=apo
            loginGoogle()
    except MyError, err:
        msg("Authentication error.")
        log(err.value)
        raise MyError(err.value)

def checkAuth():
    global authLogin
    #Check if already got authorization
    if authLogin.has_key('authorization'):
        oldauth=query('Use current authorization ?','query')
        if oldauth==1:
            return
    #Check for username
    if settings['username']==None:
        raise MyError('username not setted')
    user=settings['username']
    #Check for password
    if settings['password']!=None:
        password=settings['password']
    else:
        password=query('Passowrd:','code')
        if password==None:
            raise MyError('password not setted')
    pw=password
    #Add @gmail.com to username
    if user.find('@')==-1:
        user=user+'@gmail.com'
    authLogin={'username': user, 'password': pw}

def loginGoogle():
    #load rest of needed data
    global gdata
    import gdata
    ##
    global authLogin
    #Get google auth
    cor=msg("Authenticating... ")
    try:
        auth = gdata.GoogleAuth( authLogin['username'], authLogin['password'] )
    except MyError, err:
        raise MyError(err.value)
    msg_xy(cor,"ok")
    authLogin['authorization']=auth

def sessionGoogle():
    global authLogin
    cor=msg("Session id... ")
    #Get google session
    url = gdata.allCalendarsUrl(authLogin['username'])
    try:
        gsessionid = gdata.SessionUrl(authLogin['authorization'], url)
    except MyError, err:
        msg('Session error.')
        log(err.value)
        raise MyError(err.value)
    msg_xy(cor,"ok")
    authLogin['allCalendarsUrl']=url
    authLogin['gsessionid']=gsessionid

def retriveCalendars():
    global authLogin
    cor=msg("Retrieving calendars list... ")
    authLogin['allCalendarsUrl'] = authLogin['allCalendarsUrl'] + '?' + authLogin['gsessionid']
    allcalendars_xml = gdata.GetCalendarXml(authLogin['authorization'],authLogin['allCalendarsUrl'])
    msg_xy(cor,"ok")
    cals = gdata.readCalendars(allcalendars_xml)
    #print b
    #parser = XmlParser.XMLParser()
    #parser.parseXML(b)
    #rootNode = parser.root
    #entries = rootNode.childnodes['entry']
    #cals = gdata.readCalendars(entries)
    authLogin['calendars']=cals
    log(cals)

def chooseCalendar(multi=0):
    global authLogin
    calList=[]
    for cl in authLogin['calendars']:
        calList.append(cl['title'])
    if multi==1:
        res=multi_selection_list('Choose calendar:',calList)
        authLogin['chosenCalendars']=res
    else:
        res=selection_list('Choose calendar:',calList)
        authLogin['chosenCalendars']=[res]
    return res

def readCalendarEntries(calIndex=None):
    global authLogin
    if calIndex==None:
        calIndex=chooseCalendar()
    if calIndex==None:
        syncAborted('User aborted.')
        raise MyError('UserAbort')
    cor=msg("Calendar '%s'... " %authLogin['calendars'][calIndex]['title'])
    calUrl = authLogin['calendars'][calIndex]['link']+'?'+authLogin['gsessionid']+'&'+authLogin['queryRange']
    calXml = gdata.GetCalendarXml(authLogin['authorization'],calUrl)
    msg_xy(cor,"ok")
    calEntries = gdata.readCalendarEntries(calXml)
    if 'calendarEntries' not in authLogin:
        authLogin['calendarEntries']={}
    authLogin['calendarEntries'][calIndex]=calEntries
    return calIndex

def readCalendarsEntries(calsIndex=None):
    global authLogin
    if calsIndex==None:
        calsIndex=chooseCalendar(1)
    if calsIndex==None:
        syncAborted('User aborted.')
        raise MyError('UserAbort')
    for idx in calsIndex:
        readCalendarEntries(idx)
    return calsIndex

def syncAborted(logmsg=None):
    msg("Aborted.")
    if logmsg!=None:
        log(logmsg)

def doubleDigit(digit):
    if digit<10:
        digit='0%s' %digit
    return digit

def moveDays(timefloat, sign, days):
    days=days*24*60*60
    newtime=eval('%s%s%s' %(timefloat,sign,days))
    return newtime

def floatDateRange():
    curfloat=time.mktime(time.gmtime())
    #backwards
    bwdfloat=moveDays(curfloat,'-',settings['sync_backwards'])
    #forwards
    fwdfloat=moveDays(curfloat,'+',settings['sync_forwards'])
    return (bwdfloat, fwdfloat)

#default queryRange 30 days backwards and 120 days forwards.
#also includes max-results here.
def queryRange():
    global authLogin
    range=floatDateRange()
    #backwards
    bwdfloat=range[0]
    bwd=time.gmtime(bwdfloat)
    bwd_day=doubleDigit(bwd[2])
    bwd_month=doubleDigit(bwd[1])
    str_bwd='%s-%s-%sT00:00:00' %(bwd[0],bwd_month,bwd_day)
    #forwards
    fwdfloat=range[1]
    fwd=time.gmtime(fwdfloat)
    fwd_day=doubleDigit(fwd[2])
    fwd_month=doubleDigit(fwd[1])
    str_fwd='%s-%s-%sT00:00:00' %(fwd[0],fwd_month,fwd_day)
    #if str_cur<str_range:
    #    #res="start-min=%s&start-max=%s" %(str_cur,str_range)
    #    res="start-min=%s" %str_cur
    #else:
    #    #res="start-min=%s&start-max=%s" %(str_range,str_cur)
    #    res="start-min=%s" %str_range
    res="start-min=%s&start-max=%s" %(str_bwd,str_fwd)
    res="max-results=%s&%s" %(settings['max_results'], res)
    authLogin['queryRange']=res

def syncToPhone():
    global authLogin
    try:
        authenticate()
        sessionGoogle()
        retriveCalendars()
        if authLogin['calendars']==None:
            msg('No calendars found.')
            return
        queryRange()
        calIdxs=readCalendarsEntries()
        authLogin['apo'].stop()
        if authLogin['calendarEntries']==None:
            msg("Calendar does not have any entries.")
            return
    except MyError:
        return
    count_adds=0
    count_updates=0
    for calIndex in calIdxs:
        count=gcal_defs.testme(authLogin['calendarEntries'][calIndex])
        count_adds+=count[0]
        count_updates+=count[1]
    msg('Done, add=%d , updated:%d.' %(count_adds,count_updates))

def removeGoogleRecurrences():
    global authLogin
    google_idxs=authLogin['calendarEntries']
    for gidx in google_idxs:
        gc=google_idxs[gidx]
        gc_clean=[]
        for ge in gc:
            if 'recurrence' not in ge and ge['status']!='canceled':
                gc_clean.append(ge)
        google_idxs[gidx]=gc_clean
    authLogin['calendarEntries']=google_idxs

def removePhoneRecurrences():
    global authLogin
    ent_clean=[]
    for e in authLogin['phoneEntries']:
        if e['repeat']==None:
            ent_clean.append(e)
    authLogin['phoneEntries']=ent_clean

#convert timestr to float
def fixGoogleCalendarsTimes():
    global authLogin
    google_idxs=authLogin['calendarEntries']
    for gidx in google_idxs:
        gcale=google_idxs[gidx]
        gcal_defs.convertGoogleTimes(gcale)

#if entry exists in google calenadrs - after fixing google times to float.
def entryGoogleExists(e):
    google_idxs=authLogin['calendarEntries']
    for gidx in google_idxs:
            gc=google_idxs[gidx]
            if _entryGoogleExists(e,gc):
                return True
    return False

def _entryGoogleExists(e,gc):
    for ge in gc:
        if e['title']==ge['title'] and e['start_time']==ge['startTime'] and e['end_time']==ge['endTime']:
            return True
    return False

def removeExistingEntries():
    #I dont do recurrence yet
    removeGoogleRecurrences()
    removePhoneRecurrences()
    #now fix strtime of google stuff
    fixGoogleCalendarsTimes()
    ##
    count_add=0
    count_skip=0
    for pe in authLogin['phoneEntries']:
        if not entryGoogleExists(pe):
            count_add+=1
            log2('------')
            log2(pe['title'])
            log2(pe['start_time'])
            log2(str(time.gmtime(pe['start_time'])))
        else:
            count_skip+=1
    msg('found to add: %d' %count_add)
    msg('found to skip: %d' %count_skip)

def checkCalendarsWriteable():
    for ci in authLogin['chosenCalendars']:
        c=authLogin['calendars'][ci]
        if c['accesslevel']!='owner' and c['accesslevel']!='contributor':
            return c['title']
    return None

def syncToGoogle():
    global authLogin
    range=floatDateRange()
    try:
        phoneEntries=mycal.readPhoneEntries(range[0],range[1])
        if phoneEntries==None:
            msg('No entries found.')
            return
        authenticate()
        sessionGoogle()
        retriveCalendars()
        calsIndex=chooseCalendar(1)
        if calsIndex==None:
            syncAborted('User aborted.')
            raise MyError('UserAbort')
        #Its not writeable but I sync others calendars, like holidays.
        #tmp=checkCalendarsWriteable()
        #if tmp!=None:
        #    msg("Calendar not writeable: '%s'." %tmp)
        #    return
        queryRange()
        readCalendarsEntries(calsIndex)
        authLogin['phoneEntries']=phoneEntries
        removeExistingEntries()
        #
        authLogin['apo'].stop()
        msgbox('todo :)')
        #
    except MyError:
        return
    
    #todo
