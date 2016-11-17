import requests
from xml.dom import minidom
import sys
#from urllib3.util import response
#from __builtin__ import None

cookie = None

_url = "https://services.techhouse.dk/webTourManager/0.6/Service.svc/basHttps"

def is_authenticated(doc):

    access_xml = doc.getElementsByTagName("a:Access")[0]

    try:
        authenticated = access_xml.getElementsByTagName("b:IsAuthenticated")[0]
    except:
        print sys.exc_info()[0]
        return False

    return authenticated.firstChild.data == "true"

def login():
    global cookie
    header = {'content-type': 'text/xml', 'SOAPAction' : 'https://services.techhouse.dk/webTourManager/IPlanning/Login'}
    body =  """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="https://services.techhouse.dk/webTourManager">
            <soapenv:Header/>
            <soapenv:Body>
            <web:Login>
            <web:OwnerIDno>107</web:OwnerIDno>
            <web:Alias>testonly</web:Alias>
            <web:AuthKey>4057640D-4C9B-424C-A88C-DC9EE42B1032</web:AuthKey>
            </web:Login>
            </soapenv:Body>
            </soapenv:Envelope>"""

    response = requests.post(_url,data=body,headers=header)

    doc = minidom.parseString(response.content)

    authenticated = doc.getElementsByTagName("b:IsAuthenticated")[0]

    if authenticated.firstChild.data == "true":
        cookie = response.cookies

def gettours():
    global cookie
    
    def do_gettours():
        header = {'content-type': 'text/xml', 'SOAPAction' : 'https://services.techhouse.dk/webTourManager/ITour/Tour_GetFromStatusAndDateRange_WithSalesperson'}
        body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="https://services.techhouse.dk/webTourManager">
               <soapenv:Header/>
               <soapenv:Body>
              <web:Tour_GetFromStatusAndDateRange_WithSalesperson>
                <web:Status>10</web:Status>
                 <web:From>2016-09-01</web:From>
                 <web:To>2016-09-30</web:To>
                <web:SalespersonID>JDa</web:SalespersonID>
                  </web:Tour_GetFromStatusAndDateRange_WithSalesperson>
               </soapenv:Body>
                </soapenv:Envelope>"""

        response = requests.post(_url,data=body,headers=header,cookies=cookie)

        doc = minidom.parseString(response.content)
        
        return doc

    repeat_read = True

    while repeat_read:
        doc = do_gettours()

        if is_authenticated(doc):
            repeat_read = False
        else:
            login()

    if cookie is not None:
        tours = doc.getElementsByTagName("b:TourIDnoItem")

        tourids = []

        for TourIDnoItem in tours:
            tourid = TourIDnoItem.getElementsByTagName("b:TourIDno")[0]
            tourids = tourids + [int(tourid.firstChild.data)]

        return tourids

def gettour(id):
    global cookie
    
    def do_gettour(id):
        header = {'content-type': 'text/xml', 'SOAPAction' : 'https://services.techhouse.dk/webTourManager/ITour/Tour_Get'}
        body =  """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="https://services.techhouse.dk/webTourManager">
                <soapenv:Header/>
                <soapenv:Body>
                <web:Tour_Get>
                <web:IDno>""" + str(id) + """</web:IDno>
                </web:Tour_Get>
                </soapenv:Body>
                </soapenv:Envelope>"""

        response = requests.post(_url,data=body,headers=header,cookies=cookie)

        doc = minidom.parseString(response.content)

        return doc
    
    repeat_read = True

    while repeat_read:
        response_doc = do_gettour(id)

        if is_authenticated(response_doc):
            repeat_read = False
        else:
            login()

    if cookie is not None:

        content_xml = response_doc.getElementsByTagName("a:Content")[0]

        tour = {}

        for node in content_xml.childNodes:
            try:
                tour[str(node.localName)] = str(node.firstChild.data)
            except:
                tour[str(node.localName)] = None
       
        return tour

"""
def settour_attribute(id, attribute_id, attribute_value)
    global cookie
    

"""