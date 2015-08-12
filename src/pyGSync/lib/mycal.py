# Copyright (c) 2008 Roi Dayan
# This file is part of the pyGSync project.
# http://pygsync.googlecode.com

#calendar database defs

def readPhoneEntries(start,end,type=''):
    import calendar
    cal=calendar.open()
    entries=readEntries(cal,start,end,type)
    return entries

def readEntries(cal,start,end,type=''):
    instances=cal.find_instances(start,end,'',type)
    entries=[]
    for item in instances:
        entry={}
        ent=cal.__getitem__(item['id'])
        entry['id']=ent.id
        entry['title']=ent.content
        entry['location']=ent.location
        entry['start_time']=ent.start_time
        entry['end_time']=ent.end_time
        entry['last_modified']=ent.last_modified
        entry['start_time']=ent.start_time
        entry['repeat']=ent.get_repeat()
        #alarm, priority, crossed out
        entries.append(entry)
    if entries==[]:
        return None
    return entries
