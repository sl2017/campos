import requests
from xml.dom import minidom
import sys
#from urllib3.util import response
#from __builtin__ import None

cookie = None

_url = "https://services.techhouse.dk/webTourManager/1.3/SL2017.svc/rest/xml/"

def is_authenticated(doc):

    access_xml = doc.getElementsByTagName("Access")[0]

    try:
        authenticated = access_xml.getElementsByTagName("a:IsAuthenticated")[0]
    except:
        print sys.exc_info()[0]
        return False

    return authenticated.firstChild.data == "true"

def login():
    global cookie
    login_url = _url + "Login?OwnerIDno=107&Alias=testonly&AuthKey=F3ACDD1A-046D-42D7-A3B8-8A20488AA016"

    response = requests.get(login_url,data=None)

    doc = minidom.parseString(response.content)

    authenticated = doc.getElementsByTagName("a:IsAuthenticated")[0]

    if authenticated.firstChild.data == "true":
        cookie = response.cookies

def usgroup_getall():
    global cookie

    def do_usgroup_getall():
        do_url = _url + "usgroup/GetAll/"

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = True

    while repeat_read:
        doc = do_usgroup_getall()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login()

    return doc

def usgroup_getbyname(groupname):
    global cookie

    def do_usgroup_getbyname():
        do_url = _url + "usGroup/GetByName/?Name=" + groupname

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = True

    while repeat_read:
        doc = do_usgroup_getbyname()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login()

    if cookie is not None:
        idno = doc.getElementsByTagName("a:IDno")[0]

        return idno.firstChild.data

def usgroup_create(groupname):
    global cookie

    def do_usgroup_create():
        do_url = _url + "usGroup/Create/?Name=" + groupname

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = True

    while repeat_read:
        doc = do_usgroup_create()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login()

    if cookie is not None:
        idno = doc.getElementsByTagName("a:IDno")[0]

        return idno.firstChild.data

def ususer_getbygroupidno(groupidno):
    global cookie

    def do_ususer__getbygroupidno():
        do_url = _url + "usUser/GetAll/GroupIDno/?GroupIDno=" + groupidno

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = True

    while repeat_read:
        doc = do_ususer__getbygroupidno()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login()

    if cookie is not None:
            return doc

def ususer_getbygroupidnoList(groupidno):
    response_doc=ususer_getbygroupidno(groupidno)
    qty = response_doc.getElementsByTagName("Total")[0].firstChild.data
    ususerlist=[]
    if qty <> '0':
        idno = response_doc.getElementsByTagName("a:IDno")

        for u in idno:
            ususerlist.append(str(u.firstChild.data))
    
    return ususerlist

def ususer_getbyexternalid(externalid):
    global cookie

    def do_ususer_getbyexternalid():
        do_url = _url + "usUser/Get/ExternalID/?ExternalID=" + externalid

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = True

    while repeat_read:
        doc = do_ususer_getbyexternalid()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login()

    if cookie is not None:
        idno = doc.getElementsByTagName("a:IDno")[0]

        return idno.firstChild.data

def ususer_create(externalid, groupidno, firstname, lastname):
    global cookie

    def do_ususer_create():
        do_url = _url + "usUser/Create/WithGroupIDno/?FirstName=" + firstname + "&LastName=" + lastname + "&ExternalID=" + externalid + "&GroupIDno=" + groupidno

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = True

    while repeat_read:
        doc = do_ususer_create()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login()

    if cookie is not None:
        idno = doc.getElementsByTagName("a:IDno")[0]

        return idno.firstChild.data

def usneed_create(request):
    global cookie

    def do_usneed_create():
        do_url = _url + "usNeed/Create/?" + request

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = True

    while repeat_read:
        doc = do_usneed_create()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login()

    return doc

def usneed_getbyidno(request):
    global cookie

    def do_usneed_getbyidno():
        do_url = _url + "usNeed/GetByIDno/?IDno=" + request

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = True

    while repeat_read:
        doc = do_usneed_getbyidno()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login()

    return doc

def usneed_GetByGroupIDno(request):
    global cookie

    def do_usneed_getbygroupidno():
        do_url = _url + "usNeed/GetByGroupIDno/?GroupIDno=" + request

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = True

    while repeat_read:
        doc = do_usneed_getbygroupidno()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login()

    return doc

def usneed_update(request):
    global cookie

    def do_usneed_update():
        do_url = _url + "usNeed/Update/?" + request

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = True

    while repeat_read:
        doc = do_usneed_update()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login()

    return doc

def usdestinations_getall():
    global cookie

    def do_usdestinations_getall():
        do_url = _url + "usDestination/GetAll/"

        response = requests.get(do_url,data=None,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc

    repeat_read = True

    while repeat_read:
        doc = do_usdestinations_getall()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login()

    return doc
