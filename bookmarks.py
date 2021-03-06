# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 10:30:52 2021

@author: X
"""
import json
import lz4.frame, lz4.block
import os
import copy

# The full path to the Firefox folders is:
# C:\Users\USERNAME\AppData\Roaming\Mozilla\Firefox\Profiles
# Each profile gets its own folder and from there, the bookmark files are saved
#  in "bookmarksbackups".
def bookmarkbackups():
    USERS=r"C:\Users"
    users=os.listdir(USERS)
    MOZAPPDATA=r"AppData\Roaming\Mozilla\Firefox\Profiles"
    REMOVE=['All Users', 'Default', 'Default User', 'desktop.ini', 'Public']
    rv=[]
    for each in REMOVE:
        users.remove(each)
    for user in users:
        for profile_folder in os.listdir(os.path.join(USERS,user,MOZAPPDATA)):
            for bookmark_file in os.listdir(os.path.join(USERS,user,MOZAPPDATA,
                                            profile_folder,"bookmarkbackups")):
                rv.append(os.path.join(USERS,user,MOZAPPDATA,profile_folder,
                                       "bookmarkbackups",bookmark_file))
    return rv
def readfile(fn):
    with open(fn,'rb') as fh:
        return fh.read()
# The backup files are lz4 compressed and start with "mozLz40"
def readbookmarkfile(fn):            
    file_content=readfile(fn)
    if file_content[0:8]==bytes("mozLz40\x00".encode('ascii')):
        file_content = lz4.block.decompress(file_content[8:])
    return json.loads(file_content)
def count_links(j,count=0):
    if type(j)==dict:
        if "children" in j:
            for e in j["children"]:
                count+=count_links(e)
            return count
        else:#if no children then it's a link
            return 1
    assert False
def count_and_validate_flatv(v):
    count=0
    for j in v:
        if "children" in j:
            for e in j["children"]:
                if e["type"]!="text/x-moz-place": return False, count
                count+=1
        else:
            assert False
    return True,count
def grab_all_links(j,depth=0):
    rv=[]
    if "children" in j:
        for e in j["children"]:
            if e["type"]=="text/x-moz-place":
                rv.append(e)
            elif e["type"]=="text/x-moz-place-container":
                rv.extend(grab_all_links(e,depth+1))
            else:
                assert False
    return rv
def printkeys(j):
    for k,v in j.items():
        if k!="children":
            print(k,"=",v,sep="")
        else:
            print(len(v),"children")
    print()
def write_pretty(j,fn):
    with open(fn, "w") as write_file:
        json.dump(j, write_file, indent=4)
# I had a bug where if every item didn't have its own unique id it would fail
# to load in Firefox. I created this dictionary making function to discover
# duplicate ids. In the end I just change all the ids in the big data structure
# rather than trying to keep track during the process of merging.
def id_dict(n,d):
    id = n["id"]
    if n["type"]=="text/x-moz-place":
        if id in d:
            d[id]+=1
        else:
            d[id]=1
    elif n["type"]=="text/x-moz-place-container":
        if id in d:
            d[id]+=1
        else:
            d[id]=1
        if "children" in n:
            for sub in n["children"]:
                id_dict(sub,d)
    else:
        assert False
def return_id_dict(n):
    d={}
    id_dict(n,d)
    return d
def fix_all_ids(n,id=100):
    n["id"]=id
    id+=1
    if "children" in n:
        for sub in n["children"]:
            id=fix_all_ids(sub,id)
    return id
def remove_children(j):
    rv={}
    for k,v in j.items():
        if k=="children": continue
        rv[k]=v
    return rv
def link_anywhere_in_rv(j,rv):
    for folder in rv:
        for link in folder["children"]:
            if j["uri"]==link["uri"]:
                return True
    return False
# There are a few contradictory ideas here. It is possible to comment out
# if link_anywhere_in_rv() to only search folders with the same name
# first it searches if the link exists anywhere, leave that in to not have dupe
# then it looks for a place for the link to go
# it looks for a matching folder name
# then compares all links. If the folder name matches then it first checks the
# uris for a match. If already in folder skips
# but if not then it returns the destination folder
# if the uri is unique then it returns False signaling to create a place for it
def already_in_rv(link,title,rv):
    if link_anywhere_in_rv(link,rv):
        #print(link["title"])
        return True
    for i,j in enumerate(rv):
        dest=None
        if j["title"]==title:
            dest = i
            if "children" in j:
                for sub in j["children"]:
                    if sub["uri"]==link["uri"]:
                        return True
        if dest!=None:
            return rv[dest]
    return False
def merge_link_folder(link,folder,rv,idd):
    assert link["type"]=="text/x-moz-place"
    assert "children" not in link
    assert folder["type"]=="text/x-moz-place-container"
    assert type(rv)==list
    b = already_in_rv(link,folder["title"],rv)
    if b==False:
        rv.append(remove_children(folder))
        rv[-1]["children"]=[link]
    elif type(b)==dict:
        if "children" not in b:
            b["children"]=[]
        b["children"].append(link)
    else:
        assert b==True
def merge_link_folder_all(folder,rv,idd):
    assert folder["type"]=="text/x-moz-place-container"
    if "children" not in folder: return
    for sub in folder["children"]:
        if sub["type"]=="text/x-moz-place":
            merge_link_folder(sub,folder,rv,idd)
        elif sub["type"]=="text/x-moz-place-container":
            merge_link_folder_all(sub,rv,idd)
        else:
            assert False
# mut is a name for the template structure that has a "menu" "unfiled" and
# "toolbar" folder. I actually later include "mobile" as well.
# This stucture is the empty structure that I merge all the links into since I
# don't want links to fall into those orignal folders and instead to fall into
# alternate ones that are under the root menu folder
def build_mut():
    mut=readbookmarkfile("empty_pretty.json")
    for each in mut["children"][0]["children"]:
        each["children"]=[]
    return mut["children"][0]["children"]
def process_alts(first=None):
    if first==None:
        files=[]
    else:
        files=[first]
    files.extend(bookmarkbackups())

    rv=build_mut()
    idd={}
    for fn in files:
        j=readbookmarkfile(fn)
        if count_links(j)<10000:
            merge_link_folder_all(j,rv,idd)
        else:
            print(fn)
    return rv
def create_merged_json(first=None):
    v=process_alts(first)
    merged=readbookmarkfile("empty_pretty.json")
    merged["children"][0]["children"]=v
    print("count =",count_links(merged))
    fix_all_ids(merged)
    write_pretty(merged,"merged.json")
    return merged
merged=create_merged_json(input("Primary bookmark file: "))
