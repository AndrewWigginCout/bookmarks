# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 10:30:52 2021

@author: X
"""
import json
import lz4.frame, lz4.block
import os
import copy

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
def readbookmarkfile(fn):            
    file_content=readfile(fn)
    #print(len(file_content))
    if file_content[0:8]==bytes("mozLz40\x00".encode('ascii')):
        file_content = lz4.block.decompress(file_content[8:])
    #y = ac(file_content)
    #print(decompressed)
    return json.loads(file_content)
def readbookmarkfilejson(fn):
    file_content=readfile(fn)
    return json.loads(file_content)
def export(j,fn):
    with open(fn,"w") as fh:
        fh.write(json.dumps(j))
def count_links(j,count=0):
    #print(type(j))
    if type(j)==dict:
        if "children" in j:
            for e in j["children"]:
                count+=count_links(e)
            #print("subcount=",count)
            return count
        else:#if no children then it's a link
            return 1
    assert False
def all_links(j,rv=[]):
    if "children" in j:
        for e in j["children"]:
            rv.append(all_links(e))
    else:
        return j
    assert False
def uris_of_v(v):
    return [bm["uri"] for bm in v["children"]]
def uris_of_jfolder(v):
    return [bm["uri"] for bm in v["children"]]

    
    
def merge(link,folder_name,rv):
    assert link["type"]=="text/x-moz-place"
    destination=merge_destination(e,j,rv)
    if destination != None:
        destination.append(e)
def flatten10(j,rv,depth=0):
    links=[]
    folders=[]
    if "children" in j:
        for i,e in enumerate(j["children"]):
            if e["type"]=="text/x-moz-place":
                links.append(e)
            elif e["type"]=="text/x-moz-place-container":
                folders.append(e)
            else:
                assert False
        j["children"]=links
        rv.append(j)
        for subj in folders:
            flatten10(subj,rv,depth+1)
    else:#empty folder
        pass
        #printkeys(j)
        #print("EMPTY FOLDER")
        pass
        #rv.append(j)
        #j["children"]=[]
def compare(e,rv):
    bv=[]
    for folder in rv:
        for link in folder["children"]:
            assert type(link)==dict
            if link["uri"]==e["uri"]:
                #printkeys(e)
                #printkeys(link)
                bvc=[]
                for k,v in e.items():
                    if k not in link:
                        bvc.append(False)
                        continue
                    if link[k]==e[k]:
                        bvc.append(True)
                    else:
                        bvc.append(False)
                bv.append(bvc)
    return bv
def allbool2d(n):
    for each in n:
        if not each:
            return False
    return True
def merge10(rv,rv2,unique):
    for f in rv2:
        for e in f["children"]:
            if e["type"]=="text/x-moz-place":
                bv=compare(e,rv)
                #print(e["uri"],bv)
                if bv==[]:#indentical link
                    pass
                else:
                    pass
                    #print("merged")
                    printkeys(e)
                    unique.append((e,f["title"]))
            else:#
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
def count_and_validate_flatj(j):
    count=0
    for sj in j["children"]:
        if sj["type"]!="text/x-moz-place":
            return False, count
        count+=1
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
def all_guids(j):
    rv=[]
    if "children" in j:
        for e in j["children"]:
            rv.extend(all_guids(e))
        return rv
    else:
        return[j["guid"]]
    return rv                
def all_ids(j):
    rv=[]
    if "children" in j:
        for e in j["children"]:
            rv.extend(all_ids(e))
        return rv
    else:
        return[j["id"]]
    return rv                
def has_same_name_as_any_in(folder,v):
    for e in v:
        if folder["title"]==e["title"]:
            return True
    return False
def title_exists_in(title,f):
    for e in f:
        if title==e["title"]:
            return True
    return False
def merge_folders(v):
    rv = []
    for folder in v:
        if title_exists_in(folder["title"],rv):
            index = index_of_title(folder)
            # RETURN ATTENTION HERE
def consolidate_bookmarks_all_profiles():
    rv=[]
    files = bookmarkbackups()
    for file in files:
        rv.append(flatten8(readbookmarkfile(file)))
def printkeys(j):
    for k,v in j.items():
        if k!="children":
            print(k,"=",v,sep="")
        else:
            print(len(v),"children")
    print()
def find_uri(u,v):
    for j in v:
        if u in uris_of_jfolder(j):
            print( j["title"] )
            return True
    return False
def gen_guid():
    LETTERS="ABCDEFGHIJKSMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz012345679_-"
    from random import choice
    return "".join([choice(LETTERS) for i in range(12)])
gen_id = 1400
def gen_folder(title,):
    import time
    global gen_id
    gen_id+=1
    return {"dateAdded":int(time.time()),
            "guid":gen_guid(),
            "id":gen_id,
            "title":title,
            "type":"text/x-moz-place-container",
            "typeCode":2,
            "children":[],
            }
def clean_folder_names(v):
    for i in range(len(v)):
        if "root" in v[i]:
            replacement=gen_folder(v[i]["title"])
            replacement["children"]=v[i]["children"]
            v[i]=replacement
def uri_anywhere_in_v(uri,v):
    for f in v:
        for link in f["children"]:
            if link["uri"]==uri:
                return True
    return False
def build_exportable(files):
    global j
    mutsubj=readbookmarkfilejson("mutsub.json")
    rv=[e for e in mutsubj["children"]]
    rv.pop()
    for e in rv:
        e["children"]=[]
    for file in files:
        j=readbookmarkfile(file)
        joriginal=copy.deepcopy(j)
        flatten10_merge_folders(j,rv)
    finalj=readbookmarkfile("default empty bookmarks.json")
    finalj["children"][0]["children"]=rv
    #export(finalj,"finalj.json")
    return finalj
def look_for_empty_folders(j):
    if j["typeCode"]==2:
        if "children" in j:
            return any([look_for_empty_folders(s) for s in j["children"]])
        else:
            printkeys(j)
            return True
    else:
        return False
def change_guids(rv):
    three=["menu________","unfiled_____","toolbar_____"]
    for f in rv:
        if f["guid"] in three:
            f["guid"] = gen_guid()
            del f["root"]
def write_pretty(j,fn):
    with open(fn, "w") as write_file:
        json.dump(j, write_file, indent=4)
def link_anywhere_in_rv(j,rv):
    for folder in rv:
        for link in folder["children"]:
            if j["uri"]==link["uri"]:
                return True
    return False
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
def fix_all_ids(n,id=100):
    n["id"]=id
    id+=1
    if "children" in n:
        for sub in n["children"]:
            id=fix_all_ids(sub,id)
    return id
def change_id(link,idd):
    id=100
    while id in idd:
        id+=1
    link["id"]=id
def merge_link_folder(link,folder,rv,idd):
    assert link["type"]=="text/x-moz-place"
    assert folder["type"]=="text/x-moz-place-container"
    assert type(rv)==list
    b = already_in_rv(link,folder["title"],rv)
    if b==False:
        if link["id"] in idd:
            change_id(link,idd)
        idd[link["id"]]=1        
        rv.append(remove_children(folder))
        rv[-1]["children"]=[link]
    elif type(b)==dict:
        if "children" not in b:
            b["children"]=[]
        if link["id"] in idd:
            change_id(link,idd)
        idd[link["id"]]=1        
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
def remove_children(j):
    rv={}
    for k,v in j.items():
        if k=="children": continue
        rv[k]=v
    return rv
def build_mut():
    mut=readbookmarkfile("empty mut.json")
    mut["children"][0]["children"][0]["children"]=[]
    mut["children"][0]["children"][1]["children"]=[]
    mut["children"][0]["children"][2]["children"]=[]
    return mut["children"][0]["children"]
def process_alts():
    files=[]
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
def create_merged_json():
    v=process_alts()
    mut=readbookmarkfile("empty mut.json")
    mut["children"][0]["children"]=v
    print("count =",count_links(mut))
    fix_all_ids(mut)
    write_pretty(mut,"export9.json")
    return mut
nmut=create_merged_json()
