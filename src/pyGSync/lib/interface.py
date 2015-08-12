# Copyright (c) 2008 Roi Dayan
# This file is part of the pyGSync project.
# http://pygsync.googlecode.com

import e32, appuifw, sys
from graphics import Image
#import socket
app=appuifw.app

#   Set main title
my_title = u'pyGSync'
my_version = u'0.1.5c'
my_about=[(u"python Google Sync v%s (c) Roi Dayan" %my_version),
    (u"http://pygsync.googlecode.com")]

#   Import settings
from settings import *
from interface_defs import *
from interface_settings import *

applock=None

def exit_key_handler():
    applock.signal()
    app.exit_key_handler = None
    #app.set_exit()
    #if not e32.in_emulator():
    #    app.set_exit()
    #global running
    #running=0

def post_load():
    msg(None)
    welcome_msg="Hello."
    msg(welcome_msg,'blue')
    log('<LOG>')
    
    if settings['username']==None:
        msg("Username not setted.",'red')
    else:
        msg("Username: "+settings['username'],'blue')

def save_main():
    global app, main_body
    save={'exit_key': app.exit_key_handler, 'body': main_body, 'title': app.title, 'menu': app.menu}
    return save

def restore_main(saved):
    global app, main_body
    app.exit_key_handler=saved['exit_key']
    main_body = app.body = saved['body']
    app.title=saved['title']
    app.menu=saved['menu']

def main_screen(body):
    global app, main_body
    main_body = app.body = body

def welcome():
    msg(None)
    msg("Hello "+settings['username'],'blue')

def syncToPhone():
    log('Synchronize google calendar to phone.')
    msg(None)
    welcome()
    try:
        gcal.syncToPhone()
    except:
        harness(applock, txtLog)

def syncToGoogle():
    log('Synchronize phone calendar to google.')
    msg(None)
    welcome()
    try:
        gcal.syncToGoogle()
    except:
        harness(applock, txtLog)

def select_font():
    fontlist = appuifw.available_fonts()
    index = appuifw.selection_list(choices=fontlist , search_field=1)
    appuifw.note(index);

def redraw_callback(arg):
    canvas.blit(mainimage)
"""
def settingsForm_hook(arg):
    global settings
    username = arg[0][2]
    password = arg[1][2]
    proxy = arg[2][2]
    log('username: ' + username)
    update_settings('username', username)
    log('password: ' + password)
    update_settings('password', password)
    if proxy != '':
        log(u'proxy: ' + proxy)
        update_settings('proxy', proxy)
    #if username=='' or password=='': return False
    if username=='' or password=='': log('Warning: username and/or password are blank.')
    write_settings()
    return True

def create_settings_form():
    global settings, settingsForm
    formData = [(u'Username','text',settings['username']),(u'Password','text',settings['password']),(u'Proxy','text',settings['proxy'])]
    formFlags = appuifw.FFormEditModeOnly
    settingsForm = appuifw.Form(formData, formFlags)
    settingsForm.save_hook = settingsForm_hook
"""

def callback_tabs(index):
    if index == 0:
        show('main')
    elif index == 1:
        show('log')
    elif index == 2:
        show('txt2')

def set_interface_menu_and_tabs():
    menu = [(u"Synchronize", ((u"ToPhone", syncToPhone), (u"ToGoogle", syncToGoogle))),
            (u"Settings", config_settings),
            (u"About", about), (u'Exit', exit_key_handler)]
    app.menu = menu
    tabs = [u"Main",u"Log",u"txt2"]
    app.set_tabs(tabs,callback_tabs)

def closeabout():
    aboutw.hide()
    set_interface_menu_and_tabs()
    appuifw.app.exit_key_handler=exit_key_handler

def about():
    #checking if about window created as if TopWindow loaded since its the only place I'm using it.
    if not sys.modules.__contains__('TopWindow'):
        create_about();
    aboutw.show()
    appuifw.app.menu=[(u'Back', closeabout)]
    appuifw.app.set_tabs([],None)
    appuifw.app.exit_key_handler=closeabout

def create_about():
    global aboutw,aboutimg,TopWindow
    from TopWindow import TopWindow
    aboutw = TopWindow()
    aboutimg = Image.new(canvas.size)
    background=0xdd9fff
    aboutimg.clear(background)
    txt1=my_about[0]
    txt2=my_about[1]
    aboutimg.text((5,15),txt1, imgcolor('blue'))
    aboutimg.text((5,30),txt2, imgcolor('blue'))
    sz=aboutimg.measure_text(txt1)[0]
    w=screensize[1]
    h=(sz[3]-sz[1]+15)*2
    x=0
    y=center[1]
    aboutw.size=(w,h)
    aboutw.add_image(aboutimg,(5,5))
    aboutw.corent_type='square'
    aboutw.position=(x,y)
    aboutw.background_color=background
    #aboutw.show()
    aboutw.hide()

def init_interface():
    global appname, txtLog, font, applock
    #print appuifw.available_fonts()
    font=u'Series 60 J'
    app.screen = 'normal'
    app.title=my_title
    appname = app.full_name()
    txtLog = appuifw.Text()
    txtLog.font = font
    txtLog.color = 0
    applock = e32.Ao_lock()
    app.exit_key_handler = exit_key_handler
    return applock

def create_interface():
    global canvas, mainimage, screensize, center, textloc, main_body
    global txt2
    txt2 = appuifw.Text()
    txt2.font = font
    txt2.color = 0
    main_body = canvas = appuifw.Canvas(redraw_callback)
    mainimage = Image.new(canvas.size)
    canvas.clear()
    mainimage.clear()
    app.body=canvas
    screensize = canvas.size
    center = (screensize[0]*.3,screensize[1]*.5)
    textloc = (1,0)
    load_interface()
    #create_settings_form()
    #create_about() will be called on first about show
    set_interface_menu_and_tabs()

def load_interface():
    global socket, gcal, httpUrl
    show('main')
    msg("Loading.")
    import socket, gcal, httpUrl

def imgcolor(color=(0,0,0)):
    if color=='red':
        color=(255,0,0)
    elif color=='blue':
        color=(0,0,255)
    return color

def msg(text,color=(0,0,0)):
    global textloc
    if text == None:
        mainimage.clear()
        xy=textloc=(textloc[0],0)
    else:
        xy=measure_text(text)
        y=xy[3]-xy[1]+4
        textloc=(textloc[0],textloc[1]+y)
        #textloc=(textloc[0],15)
        color=imgcolor(color)
        mainimage.text(textloc,unicode(text), color, (font, None))
        x=xy[2]-xy[0]+5
        xy=(x,textloc[1])
    redraw_callback(None)
    return xy

def msg_xy(xy,text,color=(0,0,0)):
    color=imgcolor(color)
    mainimage.text(xy,unicode(text),color,(font,None))
    redraw_callback(None)

def measure_text(text):
    return mainimage.measure_text(unicode(text),font)[0]

def show(win):
    if win == '':
        appuifw.note(u'error')
    elif win == 'main':
        app.body = main_body
    elif win == 'log':
        app.body = txtLog
    elif win == 'txt2':
        app.body = txt2

def log(text):
    txtLog.add(unicode(text) + '\n')

def log2(text):
    txt2.add(unicode(text) + '\n')

def set_access_point():
    if settings['default_ap']==None:
        apo=query_access_point()
    else:
        apo=use_access_point(settings['default_ap'])
    return apo

def query_access_point(title='Access point:'):
    apcs = socket.access_points()
    clist=[]
    for i in apcs:
       clist.append(i['name'])
    index=listbox(clist,title)
    if index==None:
        return None
    apid=apcs[index]['iapid']
    apname=apcs[index]['name']
    apo=use_access_point(apid,apname)
    return apo

def use_access_point(apid,apname=None):
    if apname==None:
        apname=apid_name(apid)
    msg('Access point: %s' %apname)
    if apid==settings['proxy_ap']:
        httpUrl.setProxy(settings['proxy'])
        msg('Proxy: %s' %settings['proxy'])
    else:
        httpUrl.setProxy(None)
    apo=socket.access_point(apid)
    socket.set_default_access_point(apo)
    return apo
