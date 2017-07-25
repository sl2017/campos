# -*- coding: utf-8 -*-
'''
Created on 11. july. 2017

@author: jda.dk
'''
from openerp import models, fields, api, tools
import xml.etree.ElementTree as ET

import logging

_logger = logging.getLogger(__name__)

class webtourbstourstop(models.Model):
    _name = 'campos.webtour.bstour.stop'
    _description = 'Campos Webtour bsTour Stop'
    bsidno = fields.Integer('Webtour Tour IDno')
    usidno = fields.Integer('Webtour us Tour ID no')
    usname = fields.Char('Webtour usName')
    updated = fields.Boolean('Updated')    
    startdate = fields.Char('DateStart')
    enddate = fields.Char('DateEnd')
    startplaceidno =fields.Char('StartPlaceIDno')     
    endplaceidno =  fields.Char('EndPlaceIDno')    
    startplace =    fields.Many2one('campos.webtourusdestination.view','StartPlace')
    endplace =      fields.Many2one('campos.webtourusdestination.view','EndPlace')


class webtourtripstate(models.Model):
    _name = 'campos.webtour.tripstate'
    _description = 'Campos Webtour Trip state'
    name = fields.Char('State')
    nextstate_id = fields.Many2one('campos.webtour.tripstate','Next State', ondelete='set null')

class webtourbstour(models.Model):
    _name = 'campos.webtour.bstour'
    _description = 'Webtour bsTours'
    bsidno = fields.Integer('Webtour IDno')
    bstourname = fields.Char('Tour bsName')
    updated = fields.Boolean('Updated')
    drivername = fields.Char('Driver Name')
    driver2name = fields.Char('Driver2 Name')
    driver3name = fields.Char('Driver3 Name')
    vehiclename = fields.Char('Vehicle Name')
    interninfo = fields.Char('Intern Info')
    driverinfo = fields.Char('Driver Info')
    pax = fields.Integer('Pax')
    vehiclemaxpax = fields.Integer('VehicleMaxPax')    
    state_id = fields.Many2one('campos.webtour.tripstate','State', ondelete='set null')
    nextstate_id = fields.Many2one('campos.webtour.tripstate','Next State', related='state_id.nextstate_id')
    
    stop_ids = fields.One2many('campos.webtour.bstour.stop','bsidno','Stops')
    
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
        
        _logger.info("kilroy 1 %s")    
        if content is not None:
            array = content.find("i:Array",ns) 
            if array is not None:                
                _logger.info("kilroy 2")    
                
                tours = self.env['campos.webtour.bstour'].search([])                    
                for t in tours:
                    t.updated = False

                stops = self.env['campos.webtour.bstour.stop'].search([])                    
                for s in stops:
                    s.updated = False

                for ustour in array.findall('a:usTour',ns):   
                    usidno = get_tag_data_from_node(ustour,'a:IDno')
                    usname = get_tag_data_from_node(ustour,'a:Name')
                    
                    #_logger.info("kilroy 3 %s %s", usidno, name) 
                    bsTourArr = ustour.find('a:bsTourArr',ns)  
                    if bsTourArr is not None: 
                        #_logger.info("kilroy 4")   
                        arrayintour = bsTourArr.find("i:Array",ns)
                        if arrayintour is not None:
                            #_logger.info("kilroy 5")
                            for bstour in arrayintour.findall('a:bsTourInfo',ns):
                                tourdic = {}
                                stopdic = {}
                                
                                bsidno = get_tag_data_from_node(bstour,'a:IDno')
                                bstourname = get_tag_data_from_node(bstour,'a:TourName')

                                tourdic['bsidno'] = bsidno
                                tourdic['bstourname'] = bstourname
                                tourdic['drivername'] =    get_tag_data_from_node(bstour,'a:DriverName')
                                tourdic['driver2name'] =   get_tag_data_from_node(bstour,'a:Driver2Name')
                                tourdic['driver3name'] =   get_tag_data_from_node(bstour,'a:Driver3Name')
                                tourdic['driverinfo'] =    get_tag_data_from_node(bstour,'a:DriverInfo')
                                tourdic['interninfo'] =    get_tag_data_from_node(bstour,'a:InternInfo')
                                tourdic['vehiclename'] =   get_tag_data_from_node(bstour,'a:VehicleName')
                                tourdic['pax'] =           get_tag_data_from_node(bstour,'a:Pax')
                                tourdic['vehiclemaxpax'] = get_tag_data_from_node(bstour,'a:VehicleMaxPax')
                                tourdic['updated'] = True
                                
                                stopdic['usidno'] = usidno
                                stopdic['usname'] = usname
                                stopdic['bsidno'] = bsidno

                                startdate =     get_tag_data_from_node(bstour,'a:DateStart')
                                enddate =       get_tag_data_from_node(bstour,'a:DateEnd')
                                startplaceidno= get_tag_data_from_node(bstour,'a:StartPlaceIDno') 
                                endplaceidno =  get_tag_data_from_node(bstour,'a:EndPlaceIDno')
                                                                                           
                                stopdic['startdate'] =     startdate
                                stopdic['enddate'] =       enddate
                                stopdic['startplace']=     startplaceidno
                                stopdic['endplace'] =      endplaceidno
                                stopdic['startplaceidno']= startplaceidno
                                stopdic['endplaceidno'] =  endplaceidno
                                stopdic['updated'] = True
                    
                                #_logger.info("kilroy 6, %s %s %s %s", usidno, bsidno,len(recs),dic ) 
                                                                                             
                                bstour = self.env['campos.webtour.bstour'].search([('bsidno','=',bsidno)])
                                                                    
                                if len(bstour) == 0:
                                    self.env['campos.webtour.bstour'].create(tourdic)                                     
                                elif len(bstour) == 1:     
                                    bstour.write(tourdic)
                                else:                                     
                                    _logger.info("Doublet of bsidno !!!!!!!!!! , %s %s %s", usidno, bsidno,len(bstour)) 

                                stop = self.env['campos.webtour.bstour.stop'].search([('usidno','=',usidno),('bsidno','=',bsidno),('startdate','=',startdate),('enddate','=',enddate),('startplaceidno','=',startplaceidno),('endplaceidno','=',endplaceidno)])
                                                                    
                                if len(stop) == 0:
                                    self.env['campos.webtour.bstour.stop'].create(stopdic)                                     
                                elif len(stop) == 1:     
                                    stop.write(stopdic)
                                else:                                     
                                    _logger.info("Doublet of stop !!!!!!!!!! , %s %s", stopdic,len(stop))                                 


                                    