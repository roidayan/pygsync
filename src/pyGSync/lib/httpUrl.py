# httpUrl class
# Copyright (c) 2008 Roi Dayan
# Used with pys60 scripts

# date: May 1, 2008
# created for easy using wap/gprs connection

proxy=None

import sys

def httpUrl(url,method='GET',request='/',params=None,headers={"Accept": "text/plain"},ssl=0,sslhostname=None):
    import httplib
    if proxy!=None:
        if ssl>0:
            if request[0:5]=='https':
                #remove https://
                request=url+request[8:]
            else:
                request=url+request
        else:
            if request[0:4]!='http':
                request = 'http://'+url+request
        url=proxy
    if ssl>0 and proxy==None:
        if sslhostname==None:
            conn = httplib.HTTPSConnection(url)
        else:
            conn = httplib.HTTPSConnection(url,sslhostname)
    else:
        conn = httplib.HTTPConnection(url)
    try:
        conn.request(method, request, params, headers)
    except:
        raise "(httpUrl) Unexpected error: %s" %sys.exc_info()[:2]
    return conn

def httpsUrl(url,method='GET',request='/',params=None,headers={"Accept": "text/plain"},sslhostname=None):
    tmp=url.split('.')
    if len(tmp)==4 and tmp[0].isdigit() and tmp[1].isdigit() and tmp[2].isdigit() and tmp[3].isdigit():
        sslhostname='bla.com'
    return httpUrl(url,method,request,params,headers,1,sslhostname)

def setProxy(addr):
    global proxy
    proxy=addr
