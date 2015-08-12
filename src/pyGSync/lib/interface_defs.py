# Copyright (c) 2008 Roi Dayan
# This file is part of the pyGSync project.
# http://pygsync.googlecode.com

import appuifw,socket
app=appuifw.app

class MyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        #return repr(self.value)
        return self.value

def harness(oldlock=None,txtLog=None):
    import sys
    import traceback
    import e32
    import appuifw
    if oldlock!=None:
        oldlock.signal()
    appuifw.app.screen='normal'
    appuifw.app.focus=None
    appuifw.app.title=u'Error occured'
    body = appuifw.app.body = appuifw.Text()
    if txtLog!=None:
        def tab(idx):
            if idx==0:
                appuifw.app.body=body;
            elif idx==1:
                appuifw.app.body=txtLog;
        appuifw.app.set_tabs([u"Error",u"Log"],tab)
    harnesslock=e32.Ao_lock()
    def quit():
        harnesslock.signal()
    appuifw.app.exit_key_handler=quit
    appuifw.app.menu=[(u'Exit', quit)]
    body.set(unicode('\n'.join(traceback.format_exception(*sys.exc_info()))))
    harnesslock.wait()
    appuifw.app.set_exit()

def msgbox(text,type='info'):
    #type: info, conf, error
    appuifw.note(unicode(text),type)

def selection_list(title,choices,search=0):
    old_title=app.title
    app.title=unicode(title)
    idx=appuifw.selection_list(choices, search)
    app.title=old_title
    return idx

def multi_selection_list(title,choices,style='checkbox',search=0):
    #style: checkbox, checkmark
    old_title=app.title
    app.title=unicode(title)
    idxs=appuifw.multi_selection_list(choices, style, search)
    app.title=old_title
    return idxs

def listbox(list,label):
    return appuifw.popup_menu(list,unicode(label))

def query(label,type='text',value=''):
    #type: text, code, number, date, time, query, float
    #(type query is yes/no)
    return appuifw.query(unicode(label),type,value)

def reverse(str):
    len=str.__len__()
    idx=len-1
    res=u''
    while(idx>=0):
        res=res+str[idx]
        idx-=1
    return res

def apid_name(apid):
    if apid==None:
        return None
    lst=socket.access_points()
    for i in lst:
        if i['iapid']==apid:
            return i['name']
    return None
