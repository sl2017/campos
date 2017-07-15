# -*- coding: utf-8 -*-
'''
Created on 11. july. 2017

@author: jda.dk
'''
from openerp import models, fields, api, tools
import xml.etree.ElementTree as ET

import logging

_logger = logging.getLogger(__name__)

class webtourbus(models.Model):
    _name = 'campos.webtour.bus'
    _description = 'Campos Webtour bus'
    bstour_id = fields.Many2one('campos.webtour.bstour','WebTour Tour', ondelete='set null') 
    bsidno = fields.Integer('Webtour Tour IDno', related='bstour_id.id')
    driverinfo = fields.Char('Driver Info', related='bstour_id.driverinfo')
    pax = fields.Integer('pax')
    state_id = fields.Many2one('campos.webtour.tripstate','State', ondelete='set null')
    nextstate_id = fields.Many2one('campos.webtour.tripstate','Next State', related='state_id.nextstate_id')

class webtourtripstate(models.Model):
    _name = 'campos.webtour.tripstate'
    _description = 'Campos Webtour Trip state'
    name = fields.Char('State')
    nextstate_id = fields.Many2one('campos.webtour.tripstate','Next State', ondelete='set null')

class webtourbstour(models.Model):
    _name = 'campos.webtour.bstour'
    _description = 'Webtour bsTours'
    id = fields.Integer('Webtour IDno')
    name = fields.Char('Tour Name')    
    usidno = fields.Integer('Webtour us Tour ID no')
    drivername = fields.Char('Driver Name')
    vehiclename = fields.Char('Vehicle Name')
    interninfo = fields.Char('Intern Info')
    driverinfo = fields.Char('Driver Info')
    startdate = fields.Char('DateStart')
    enddate = fields.Char('DateEnd')
    startplaceidno = fields.Many2one('campos.webtourusdestination.view','StartPlaceIDno') 
    endplaceidno = fields.Many2one('campos.webtourusdestination.view','EndPlaceIDno')
    pax = fields.Integer('Pax')
    vehiclemaxpax = fields.Integer('VehicleMaxPax')    
    
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
                    name = get_tag_data_from_node(ustour,'a:Name')
                    #_logger.info("kilroy 3 %s %s", usidno, name) 
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
                                    self.create({'usidno':usidno,'bsidno':bsidno,'name':name,'drivername':drivername,'vehiclename':vehiclename,'interninfo':interninfo,'driverinfo':driverinfo})
                                elif len(recs) == 1:
                                    recs[0].write({'name':name,'drivername':drivername,'vehiclename':vehiclename,'interninfo':interninfo,'driverinfo':driverinfo})
                                else: 
                                    _logger.info("get_webtourtour, Houston we have a problem!!! %s %s %s ", usidno, bsidno, len(recs))
                                    
                            for rec in recs.search([('bsidno','not in',bsidnolist)]):
                                rec.unlink()


                                    