# -*- coding: utf-8 -*-
'''
Created on 11. july. 2017

@author: jda.dk
'''
from openerp import models, fields, api, tools
import xml.etree.ElementTree as ET

import logging

_logger = logging.getLogger(__name__)

class webtourdeparturebus(models.Model):
    _name = 'campos.webtourdeparture.bus'
    _description = 'Campos Webtour Departure bus'
    bsidno = fields.Integer('Webtour Tour ID no')
    pax = fields.Integer('pax')
    state = fields.Selection([('Select', 'Please Select'),
                              ('1', 'Arrived to depot'),
                              ('2', 'In transit to Site'),
                              ('3', 'At Site'),
                              ('4', 'In transit to Destination'),
                              ('5', 'Completed')                                                                        
                              ], default='Select', string='State')


class webtourtour(models.Model):
    _name = 'campos.webtour.tour'
    _description = 'Webtour Tours'
    usidno = fields.Integer('Webtour us Tour ID no')
    bsidno = fields.Integer('Webtour IDno')
    usname = fields.Char('Tour Name')
    drivername = fields.Char('Driver Name')
    vehiclename = fields.Char('Vehicle Name')
    interninfo = fields.Char('Intern Info')
    driverinfo = fields.Char('Driver Info')
    
    @api.model
    def get_webtourtour_cron(self):
        self.get_webtourtours()
         
    def get_webtourtour(self):
        _logger.info("get_webtourtour")
        
        ns = {'i': 'http://schemas.datacontract.org/2004/07/webTourManager',
              'a': 'http://schemas.datacontract.org/2004/07/webTourManager.Classes'}
        
        def get_tag_data_from_node(node,nodetag):
            if node is None:
                return False
            else:
                tag = node.findall(nodetag,ns)                            
                if tag is not None:
                    try:
                        t = tag[0].text
                    except:
                        t = False
                        pass
                    if t is None : t = False                    
                    return t
                else:
                    return False        
        
        root = ET.fromstring(self.env['campos.webtour_req_logger'].create({'name':'usTour/GetAll/?IncludeTourInfo=true'}).responce.encode('utf-8'))
        content = root.find("i:Content",ns) #Let's find the contet Section     
        _logger.info("kilroy 1")    
        if content is not None:
            array = content.find("i:Array",ns) 
            if array is not None:                
                _logger.info("kilroy 2")    
                for ustour in array.findall('a:usTour',ns):   
                    usidno = get_tag_data_from_node(ustour,'a:IDno')
                    usname = get_tag_data_from_node(ustour,'a:Name')
                    #_logger.info("kilroy 3 %s %s", usidno, usname) 
                    bsTourArr = ustour.find('a:bsTourArr',ns)  
                    if bsTourArr is not None: 
                        #_logger.info("kilroy 4")   
                        arrayintour = bsTourArr.find("i:Array",ns)
                        if arrayintour is not None:
                            #_logger.info("kilroy 5")
                            bsidnolist =[]
                            for bstour in arrayintour.findall('a:bsTourInfo',ns): 
                                drivername = get_tag_data_from_node(bstour,'a:DriverName')
                                driverinfo = get_tag_data_from_node(bstour,'a:DriverInfo')
                                bsidno = get_tag_data_from_node(bstour,'a:IDno')
                                bsidnolist.append(bsidno)
                                interninfo = get_tag_data_from_node(bstour,'a:InternInfo')
                                vehiclename = get_tag_data_from_node(bstour,'a:VehicleName')
                                #_logger.info("kilroy 6, %s %s %s %s ", drivername, bsidno,interninfo, vehiclename )  
                    
                                recs = self.search([('usidno','=',usidno),('bsidno','=',bsidno)])
                                if len(recs) == 0:
                                    self.create({'usidno':usidno,'bsidno':bsidno,'usname':usname,'drivername':drivername,'vehiclename':vehiclename,'interninfo':interninfo,'driverinfo':driverinfo})
                                elif len(recs) == 1:
                                    recs[0].write({'usname':usname,'drivername':drivername,'vehiclename':vehiclename,'interninfo':interninfo,'driverinfo':driverinfo})
                                else: 
                                    _logger.info("get_webtourtour, Houston we have a problem!!! %s %s %s ", usidno, bsidno, len(recs))
                                    
                            for rec in recs.search([('bsidno','not in',bsidnolist)]):
                                rec.unlink()


                                    