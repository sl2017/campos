import requests
from xml.dom import minidom
import sys

cookie = None

MAXREPEATREAD = 2

def is_authenticated(doc):

    try:
        access_xml = doc.getElementsByTagName("Access")[0]
    except:
        return False

    try:
        authenticated = access_xml.getElementsByTagName("a:IsAuthenticated")[0]
    except:
        print sys.exc_info()[0]
        return False

    return authenticated.firstChild.data == "true"

def login(_url,_key):
    global cookie

    login_url = _url + _key

    response = requests.get(login_url,data=None)

    doc = minidom.parseString(response.content)

    authenticated = doc.getElementsByTagName("a:IsAuthenticated")[0]

    if authenticated.firstChild.data == "true":
        cookie = response.cookies

def get(_url,_key,req):
    global cookie

    def do_req():
        do_url = _url + req

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = response.content

        return doc

    repeat_read = MAXREPEATREAD

    while repeat_read:
        doc = do_req()

        if is_authenticated(minidom.parseString(doc)):
            repeat_read = False
        else:
            login(_url,_key)
            repeat_read = repeat_read -1

    return doc

def usgroup_getall(_url,_key):
    global cookie

    def do_usgroup_getall():
        do_url = _url + "usgroup/GetAll/"

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = MAXREPEATREAD

    while repeat_read:
        doc = do_usgroup_getall()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login(_url,_key)
            repeat_read = repeat_read -1

    return doc

def usgroup_getbyname(_url,_key,groupname):
    global cookie

    def do_usgroup_getbyname():
        do_url = _url + "usGroup/GetByName/?Name=" + groupname

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = MAXREPEATREAD

    while repeat_read:
        doc = do_usgroup_getbyname()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login(_url,_key)
            repeat_read = repeat_read -1

    if cookie is not None:
        idno = doc.getElementsByTagName("a:IDno")[0]

        return idno.firstChild.data

def usgroup_create(_url,_key,groupname):
    global cookie

    def do_usgroup_create():
        do_url = _url + "usGroup/Create/?Name=" + groupname

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = MAXREPEATREAD

    while repeat_read:
        doc = do_usgroup_create()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login(_url,_key)
            repeat_read = repeat_read -1
            
    if cookie is not None:
        idno = doc.getElementsByTagName("a:IDno")[0]

        return idno.firstChild.data

def ususer_getbygroupidno(_url,_key,groupidno):
    global cookie

    def do_ususer__getbygroupidno():
        do_url = _url + "usUser/GetAll/GroupIDno/?GroupIDno=" + groupidno

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = MAXREPEATREAD

    while repeat_read:
        doc = do_ususer__getbygroupidno()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login(_url,_key)
            repeat_read = repeat_read -1             

    if cookie is not None:
            return doc

def ususer_getbygroupidnoList(_url,_key,groupidno):
    response_doc=ususer_getbygroupidno(_url,_key,groupidno)
    qty = response_doc.getElementsByTagName("Total")[0].firstChild.data
    ususerlist=[]
    if qty <> '0':
        idno = response_doc.getElementsByTagName("a:IDno")

        for u in idno:
            ususerlist.append(str(u.firstChild.data))
    
    return ususerlist

def ususer_getbyexternalid(_url,_key,externalid):
    global cookie

    def do_ususer_getbyexternalid():
        do_url = _url + "usUser/Get/ExternalID/?ExternalID=" + externalid

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = MAXREPEATREAD

    while repeat_read:
        doc = do_ususer_getbyexternalid()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login(_url,_key)
            repeat_read = repeat_read -1             

    if cookie is not None:
        idno = doc.getElementsByTagName("a:IDno")[0]

        return idno.firstChild.data

def ususer_create(_url,_key,externalid, groupidno, firstname, lastname):
    global cookie

    def do_ususer_create():
        do_url = _url + "usUser/Create/WithGroupIDno/?FirstName=" + firstname + "&LastName=" + lastname + "&ExternalID=" + externalid + "&GroupIDno=" + groupidno

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = MAXREPEATREAD

    while repeat_read:
        doc = do_ususer_create()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login(_url,_key)
            repeat_read = repeat_read -1
            
    if cookie is not None:
        idno = doc.getElementsByTagName("a:IDno")[0]

        return idno.firstChild.data

def usneed_create(_url,_key,request):
    global cookie

    def do_usneed_create():
        do_url = _url + "usNeed/Create/?" + request

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = MAXREPEATREAD

    while repeat_read:
        doc = do_usneed_create()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login(_url,_key)
            repeat_read = repeat_read -1

    return doc

def usneed_getbyidno(_url,_key,request):
    global cookie

    def do_usneed_getbyidno():
        do_url = _url + "usNeed/GetByIDno/?IDno=" + request

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = MAXREPEATREAD

    while repeat_read:
        doc = do_usneed_getbyidno()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login(_url,_key)
            repeat_read = repeat_read -1
    return doc

def usneed_getbyidno1(_url,_key,request):
    global cookie

    def do_usneed_getbyidno():
        do_url = _url + "usNeed/GetByIDno/?IDno=" + request

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = response.content

        return doc

    repeat_read = MAXREPEATREAD

    while repeat_read:
        doc = do_usneed_getbyidno()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login(_url,_key)
            repeat_read = repeat_read -1
    return doc


def usneed_delete(_url,_key,request):
    global cookie

    def do_usneed_delete():
        do_url = _url + "usNeed/Delete/?NeedIDno=" + request

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = MAXREPEATREAD

    while repeat_read:
        doc = do_usneed_delete()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login(_url,_key)
            repeat_read = repeat_read -1
            
    return doc

def usneed_GetByGroupIDno(_url,_key,request):
    global cookie

    def do_usneed_getbygroupidno():
        do_url = _url + "usNeed/GetByGroupIDno/?GroupIDno=" + request

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = MAXREPEATREAD

    while repeat_read:
        doc = do_usneed_getbygroupidno()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login(_url,_key)
            repeat_read = repeat_read -1
            
    return doc

def usneed_GetPending_ByIDno(_url,_key,request):
    global cookie

    def do_usneed_getpendingbyidno():
        do_url = _url + "usNeed/GetPending_ByIDno/?IDno=" + request

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = MAXREPEATREAD

    while repeat_read:
        doc = do_usneed_getpendingbyidno()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login(_url,_key)
            repeat_read = repeat_read -1

    return doc

def usneed_update(_url,_key,request):
    global cookie

    def do_usneed_update():
        do_url = _url + "usNeed/Update/?" + request

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = MAXREPEATREAD

    while repeat_read:
        doc = do_usneed_update()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login(_url,_key)
            repeat_read = repeat_read -1
            
    return doc

def usdestinations_getall(_url,_key):
    global cookie

    def do_usdestinations_getall():
        do_url = _url + "usDestination/GetAll/"

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = MAXREPEATREAD

    while repeat_read:
        doc = do_usdestinations_getall()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login(_url,_key)
            repeat_read = repeat_read -1
            
    return doc
