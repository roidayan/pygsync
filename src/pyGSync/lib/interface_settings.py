# Copyright (c) 2008 Roi Dayan
# This file is part of the pyGSync project.
# http://pygsync.googlecode.com

import appuifw,e32,socket
app=appuifw.app

from settings import *
from interface_defs import *
import interface

def config_settings():
    try:
        config_settings1()
    except:
        harness(interface.applock,interface.txtLog)

def config_settings1():
    idx=0
    choices=[u'Username',u'Password',u'Default access point',u'Proxy settings',u'Calendar settings']
    while idx!=None:
        tmp=None
        idx=selection_list("Settings",choices)
        if idx==0:
            tmp=query('Username:','text',settings['username'])
            if tmp!=None:
                settings['username']=tmp
                interface.welcome()
        elif idx==1:
            tmp=query('Password:','code',settings['password'])
            if tmp==None:
                tmp=query('To clear password?','query')
                if tmp==1:
                    settings['password']=None
                    msgbox('Password cleared.','conf')
            else:
                settings['password']=tmp
        elif idx==2:
            tmp=config_settings_defaccesspoint()
        elif idx==3:
            config_settings_proxy()
        elif idx==4:
            config_settings_calendar()
        #write configuration if needed
        if tmp!=None:
            write_settings()

class calendar_settings:
    def __init__(self):
        self.choices=[(u'',u'')]
        self.lb=appuifw.Listbox(self.choices,self.callback)
        self.lock=e32.Ao_lock()
        
    def run(self):
        self.refresh()
        app.body=self.lb
        app.title=u"Calendar settings:"
        app.exit_key_handler=self.exit_key_handler
        app.menu=[(u'Back', self.exit_key_handler)]
        self.lock.wait()
        self.lb=None
        
    def refresh(self,idx=0):
        self.choices=[(u'Store fullday as:', settings['sync_fullday']), (u'Sync days backwards:', unicode(str(settings['sync_backwards']))),
         (u'Sync days forwards:', unicode(str(settings['sync_forwards']))), (u'Max results', unicode(str(settings['max_results'])))]
        self.lb.set_list(self.choices,idx)
        
    def exit_key_handler(self):
        self.lock.signal()
        
    def callback(self, idx=None):
        if idx==None:
            idx=self.lb.current()
        tmp=None
        if idx==0:
            lst2=[u'Event', u'Appointment']
            tmp=listbox(lst2,"Store fullday events as:")
            if tmp==0:
                settings['sync_fullday']=u'Event'
            elif tmp==1:
                settings['sync_fullday']=u'Appointment'
        elif idx==1:
            tmp=query('Sync days backwards:','number',settings['sync_backwards'])
            #if tmp>settings['sync_forwards']:
            if tmp<1:
                msgbox('This value cant be higher than sync_forwards.','error')
                tmp=None
            else:
                settings['sync_backwards']=tmp
        elif idx==2:
            tmp=query('Sync days forwards:','number',settings['sync_forwards'])
            #if tmp<settings['sync_backwards']:
            if tmp<1:
                msgbox('This value cant be lower than sync_backwards.','error')
                tmp=None
            else:
                settings['sync_forwards']=tmp
        elif idx==3:
            tmp=query('Max results:','number',settings['max_results'])
            if tmp<25:
                msgbox('This value cant be lower than 25.','error')
                tmp=None
            else:
                settings['max_results']=tmp
        if tmp!=None:
            write_settings()
            self.refresh(idx)

def config_settings_calendar():
    calset=calendar_settings()
    saved=interface.save_main()
    interface.main_screen(calset.lb)
    calset.run()
    interface.restore_main(saved)

class proxy_settings:
    def __init__(self):
        self.choices=[(u'',u'')]
        self.lb=appuifw.Listbox(self.choices,self.callback)
        self.lock=e32.Ao_lock()
        
    def run(self):
        self.refresh()
        app.body=self.lb
        app.title=u"Proxy settings:"
        app.exit_key_handler=self.exit_key_handler
        app.menu=[(u'Back', self.exit_key_handler)]
        self.lock.wait()
        self.lb=None
        
    def refresh(self, idx=0):
        self.choices=[(u'Proxy access point:', unicode(apid_name(settings['proxy_ap']))), (u'Proxy:', unicode(settings['proxy'])),
            (u'Disable',u'Clear proxy access point')]
        self.lb.set_list(self.choices,idx)
        
    def exit_key_handler(self):
        self.lock.signal()
        
    def callback(self, idx=None):
        if idx==None:
            idx=self.lb.current()
        tmp=None
        if idx==0:
            tmp=socket.select_access_point()
            if tmp!=None:
                settings['proxy_ap']=tmp
        elif idx==1:
            tmp=config_settings_setproxy()
            if tmp!=None:
                settings['proxy']=tmp
        elif idx==2:
            settings['proxy_ap']=None
            tmp=1
        if tmp!=None:
            write_settings()
            self.refresh(idx)

def config_settings_proxy():
    proxyset=proxy_settings()
    saved=interface.save_main()
    interface.main_screen(proxyset.lb)
    proxyset.run()
    interface.restore_main(saved)

def config_settings_setproxy():
    lst=[u'IL Orange',u'IL Cellcom',u'Manual']
    idx=listbox(lst,'Set proxy:')
    if idx==0:
        return u'192.118.11.56:8080'
    elif idx==1:
        return u'172.31.29.37:8080'
    elif idx==2:
        tmp=query('Proxy: (ip:port)','text',settings['proxy'])
        return tmp

def config_settings_defaccesspoint():
    lst=[u'Set',u'Clear']
    idx=listbox(lst,'Default access point:')
    tmp=None
    if idx==0:
        tmp=socket.select_access_point()
        if tmp!=None:
            settings['default_ap']=tmp
    elif idx==1:
        settings['default_ap']=None
        tmp=1
        msgbox('Default access point cleared.','conf')
    return tmp
