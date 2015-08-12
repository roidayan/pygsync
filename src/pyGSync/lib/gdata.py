# Copyright (c) 2008 Roi Dayan
# This file is part of the pyGSync project.
# http://pygsync.googlecode.com

#import httplib
import urllib, urlparse
#moved to parseXML def - import XmlParser
import appuifw
#import calendar
#from time import *

from interface import *
from httpUrl import *

www_google='www.google.com'

def allCalendarsUrl(user):
    return 'http://www.google.com/calendar/feeds/'+user+'/allcalendars/full'

def GoogleAuth( u, p):
    params = urllib.urlencode({'Email':u,'Passwd':p,'service':'cl','source':'%s-%s' %(my_title,my_version)})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    #conn = httplib.HTTPSConnection("www.google.com")
    #conn.request("POST", "/accounts/ClientLogin", params, headers)
    try:
        conn = httpsUrl(www_google,"POST","/accounts/ClientLogin",params,headers)
    except:
        harness(applock,txtLog)
        raise MyError('error gdata google auth')
    response = conn.getresponse()
    status = response.status
    body = response.read()
    conn.close()
    #print u'status: '+unicode(str(status))
    #print unicode(body)
    log(body.decode('utf-8'))
    log(unicode(str(status)))
    vals = dict([x.split('=') for x in body.splitlines()])
    if status!=200:
        raise MyError(vals)
    return vals['Auth']

def GetCalendarXml(auth,url):
#    allcalendars_uri='/calendar/feeds/'+u+'/allcalendars/full'
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", 'Authorization': 'GoogleLogin auth='+auth}
    #conn = httplib.HTTPSConnection("www.google.com")
    #conn.request("GET", url, None, headers)
    conn = httpUrl(www_google,"GET",url,None,headers)
    #conn = httpsUrl("www.google.com","GET",url,None,headers)
#    response = conn.getresponse()
#    c=response.getheader('Set-Cookie')
#    l=response.getheader('Location')
#    body = response.read()
#    conn.close()
#    print c
#    print l
#    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", 'Authorization': 'GoogleLogin auth='+auth, "Set-Cookie": c}
#    conn = httplib.HTTPSConnection(l)
#    conn.request("GET", allcalendars_uri, None, headers)
    response = conn.getresponse()
    body = response.read()
    status = response.status
    conn.close()
    if status!=200:
        log2(body)
        raise MyError('SessionError, return status: %s' %status)
    #print body
    #log2(body.decode('utf-8'))
    return body

def SessionUrl( auth, url ):
    headers = {"Accept": "text/plain", 'Authorization': 'GoogleLogin auth='+auth}
    #conn = httplib.HTTPConnection("www.google.com")
    #conn.request("GET", url, None, headers)
    conn = httpUrl(www_google,"GET",url,None,headers)
    #conn = httpsUrl("www.google.com","GET",url,None,headers)
    response = conn.getresponse()
    sessionurl = response.getheader('Location')
    body = response.read().decode('utf-8')
    status = response.status
    conn.close()
    #print unicode(body)
    #print unicode(sessionurl)
    log(unicode(body))
    log(unicode(sessionurl))
    log(unicode(str(status)))
    #if status!=200:  302 ?
    #    raise Exception, body
    parts = urlparse.urlsplit(sessionurl)
    #print parts[3]
    #return parts[2] + '?' + parts[3]
    return parts[3]

def dictFromS60Event(event):
    title = event.content
    #python calendar module cant get description yet
    descr = ''
    where = event.location
    start = strftime('%Y-%m-%dT%H:%M:%SZ', gmtime(event.start_time))
    end = strftime('%Y-%m-%dT%H:%M:%SZ', gmtime(event.end_time))
    return {'title':title,'descr':descr,'where':where,'start':start,'end':end}

def atomEntryFromDict(d):
    entry = """
<entry xmlns='http://www.w3.org/2005/Atom'
    xmlns:gd='http://schemas.google.com/g/2005'>
  <category scheme='http://schemas.google.com/g/2005#kind'
    term='http://schemas.google.com/g/2005#event'></category>
  <title type='text'>%s</title>
  <content type='text'>%s</content>
  <gd:transparency
    value='http://schemas.google.com/g/2005#event.opaque'>
  </gd:transparency>
  <gd:eventStatus
    value='http://schemas.google.com/g/2005#event.confirmed'>
  </gd:eventStatus>
  <gd:where valueString='%s'></gd:where>
  <gd:when startTime='%s'
     endTime= '%s'></gd:when>
</entry>""" % (d['title'],d['descr'],d['where'],d['start'],d['end'])
#  <author>
#    <name>NAME</name>
#    <email>USERNAME</email>
#  </author>
    return entry

def insertGcal(atomEntry, calUrl, auth):
    headers = {'Content-Type': 'application/atom+xml','Authorization': 'GoogleLogin auth='+auth} 
    #conn = httplib.HTTPConnection("www.google.com")
    #conn.request("POST", sessionUrl, atomEntry, headers)
    conn = httpUrl(www_google,"POST",calUrl,atomEntry,headers)
    response = conn.getresponse()
    body = response.read()
    status = response.status
    conn.close()
    if status!=201:
        raise MyError(status)

#feedloc = '/calendar/feeds/'+u+'/private/full'


#cal = calendar.open()
#entries = cal.daily_instances(time(),appointments=1,events=1)
#
#auth = GoogleAuth( u, p )
#sess = SessionUrl( auth, feedloc )


#for entry in entries:
#    event = cal[entry['id']]
#    dict = dictFromS60Event(event)
#    entry = atomEntryFromDict(dict)
#    insertGcal(entry,sess,auth)
#    print "Added : " + event.content
#

def parseXML(xml_doc):
    import XmlParser
    parser = XmlParser.XMLParser()
    parser.parseXML(xml_doc)
    rootNode = parser.root
    if 'entry' not in rootNode.childnodes:
        return None
    return rootNode.childnodes['entry']

def readCalendars(xml_doc):
    try:
        entries = parseXML(xml_doc)
        if entries==None:
            return None
    except:
        log(xml_doc)
        #raise Exception, "readCalendars error"
        raise MyError('readCalendars error')
    ret=[]
    for node in entries:
        if "gCal:accesslevel" not in node.childnodes:
            continue
        
        val={}
        #for a in node.childnodes:
        #print a,
        #print
        
        accesslevel = node.childnodes['gCal:accesslevel'][0].properties['value']
        val['accesslevel'] = accesslevel
        
        title = node.childnodes['title'][0].content
        val['title'] = title.decode('utf-8')
        #print "Title: " + title
        
        gid = node.childnodes['id'][0].content
        val['gid'] = gid
        
        updated = node.childnodes['updated'][0].content
        val['updated'] = updated
        
        link = node.childnodes['link'][0].properties['href']
        #print "Link: " + link
        #cals.append(link)
        val['link'] = link
            
        #print "---"
        ret.append(val)
    return ret

def readCalendarEntries(xml_doc):
    try:
        entries = parseXML(xml_doc)
        if entries==None:
            return None
    except:
        log(xml_doc)
        #raise Exception, "readCalendarEntries error"
        raise MyError('readCalendarEntries error')
    ret=[]
    for node in entries:
        #for a in node.childnodes:
            #print a,
        #print
        
        val={}
        
        title = node.childnodes['title'][0].content
        #print "Title: " + title
        val['title'] = title.decode('utf-8')
        
        tid = node.childnodes['id'][0].content
        #print "ID: " + tid
        val['id'] = tid
        
        gcaluid = node.childnodes['gCal:uid'][0].properties['value'].split('@')[0]
        #print "gcaluid: " + gcaluid
        val['gcid'] = gcaluid
        
        #if "gCal:accesslevel" in node.childnodes:
        #    link = node.childnodes['link'][0].properties['href']
        #    print "Link: " + link
        #    cals.append(link)
        #    continue
        
        desc = node.childnodes['content'][0]
        if desc.content != None:
            #print "Description: " + desc.content
            val['desc'] = desc.content.decode('utf-8')
        
        if "gd:when" in node.childnodes:
            when = node.childnodes['gd:when'][0]
            startTime = when.properties['startTime']
            endTime = when.properties['endTime']
        #    print "Time: " + startTime+" -> "+endTime
            val['startTime'] = startTime
            val['endTime'] = endTime
        
        if "gd:recurrence" in node.childnodes:
            recur = node.childnodes['gd:recurrence'][0].content
            #print recur.splitlines()
            val['recurrence'] = recur
        
        if "gd:originalEvent" in node.childnodes:
            orgev = node.childnodes['gd:originalEvent'][0].properties['id']
            val['originalEvent'] = orgev
        
        seq = node.childnodes['gCal:sequence'][0].properties
        val['sequence'] = seq
        #print seq
        
        status = node.childnodes['gd:eventStatus'][0].properties['value'].split('.')[-1]
        val['status'] = status
        #print status

        updated = node.childnodes['updated'][0].content
        val['updated'] = updated
        
        where = node.childnodes['gd:where'][0].properties
        if "valueString" in where:
            where = where["valueString"]
            #print "Where: " + where
            val['where'] = where.decode('utf-8')
            
        #author = node.childnodes['author'][0]
        #author.childnodes can be empty {}
        #authorName = author.childnodes['name'][0].content.decode('utf-8')
        #authorEmail = author.childnodes['email'][0].content.decode('utf-8')
        ##print "Author: " + authorName + " ("+authorEmail+")"
        #val['author'] = {'name': authorName, 'email': authorEmail}
        
        #print "---"
        ret.append(val)
    return ret
