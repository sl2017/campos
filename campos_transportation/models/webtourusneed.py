# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
from ..interface import webtourinterface
from xml.dom import minidom

import logging

_logger = logging.getLogger(__name__)

class WebtourUsNeed(models.Model):
    _name = 'campos.webtourusneed'
    participant_id = fields.Many2one('campos.event.participant','Participant ID', ondelete='set null')
    registration_id = fields.Many2one('event.registration','Registration ID', ondelete='set null', related="participant_id.registration_id")
    travelgroup = fields.Char('Travel Group')
    campos_deleted = fields.Boolean('CampOs Deleted', default=False)
    
    campos_demandneeded = fields.Boolean('CampOs Demand Needed', default=False)
    campos_TripType_id = fields.Many2one('campos.webtourconfig.triptype','Webtour_TripType', ondelete='set null')
    campos_traveldate = fields.Char('CampOs StartDateTime', required=False)
    campos_startdestinationidno = fields.Char('CampOs StartDestinationIdNo', required=False)
    campos_enddestinationidno = fields.Char('CampOs EndDestinationIdNo', required=False)
    travelneed_id= fields.Many2one('event.registration.travelneed','Travel need',ondelete='set null')
    travelneed_deadline = fields.Selection([    ('Select', 'Please Select'),
                                     ('00:00', '00:00'),
                                     ('01:00', '01:00'),
                                     ('02:00', '02:00'),
                                     ('03:00', '03:00'),
                                     ('04:00', '04:00'),
                                     ('05:00', '05:00'),                                    
                                     ('06:00', '06:00'),
                                     ('07:00', '07:00'),
                                     ('08:00', '08:00'),
                                     ('09:00', '09:00'),                                     
                                     ('10:00', '10:00'),                                     
                                     ('11:00', '11:00'),
                                     ('12:00', '12:00'),
                                     ('13:00', '13:00'),
                                     ('14:00', '14:00'),
                                     ('15:00', '15:00'),                                    
                                     ('16:00', '16:00'),
                                     ('17:00', '17:00'),
                                     ('18:00', '18:00'),
                                     ('19:00', '19:00'),                                     
                                     ('20:00', '20:00'),                                     
                                     ('21:00', '21:00'),
                                     ('22:00', '22:00'),
                                     ('23:00', '23:00')                                                                         
                                     ], default='Select', string='Time', related='travelneed_id.deadline') 
    travelneed_travelconnectiondetails = fields.Char(related='travelneed_id.travelconnectiondetails')
        
    campos_transfered_demandneeded = fields.Boolean('Transfered Demand Needed', default=False)
    campos_transfered_deadline = fields.Selection([    ('Select', 'Please Select'),
                                     ('00:00', '00:00'),
                                     ('01:00', '01:00'),
                                     ('02:00', '02:00'),
                                     ('03:00', '03:00'),
                                     ('04:00', '04:00'),
                                     ('05:00', '05:00'),                                    
                                     ('06:00', '06:00'),
                                     ('07:00', '07:00'),
                                     ('08:00', '08:00'),
                                     ('09:00', '09:00'),                                     
                                     ('10:00', '10:00'),                                     
                                     ('11:00', '11:00'),
                                     ('12:00', '12:00'),
                                     ('13:00', '13:00'),
                                     ('14:00', '14:00'),
                                     ('15:00', '15:00'),                                    
                                     ('16:00', '16:00'),
                                     ('17:00', '17:00'),
                                     ('18:00', '18:00'),
                                     ('19:00', '19:00'),                                     
                                     ('20:00', '20:00'),                                     
                                     ('21:00', '21:00'),
                                     ('22:00', '22:00'),
                                     ('23:00', '23:00')                                                                         
                                     ], default='Select', string='Time')
    campos_transfered_travelconnectiondetails = fields.Char('Transfered connection details', required=False)
    campos_transfered_traveldate = fields.Char('Transfered Travel Date', required=False)

    campos_transfered_startdatetime = fields.Char('Transfered StartDateTime', required=False)
    campos_transfered_enddatetime = fields.Char('Transfered EndDateTime', required=False)
    campos_transfered_startdestinationidno = fields.Char('Transfered StartDestinationIdNo', required=False)
    campos_transfered_enddestinationidno = fields.Char('Transfered EndDestinationIdNo', required=False)
    campos_transfered_startnote = fields.Char('Transfered StartNote', required=False)
    campos_transfered_endnote = fields.Char('Transfered EndNote', required=False)
    
    campos_writeseq = fields.Char('CampOs Last Write Seq.', required=False)
    campos_transferedseq = fields.Char('CampOs Last transfered Seq.', required=False)
    
    campos_transfered = fields.Boolean(string='campos transfered',compute='_computediff', readonly=True, store=True)

    webtour_needidno = fields.Char('Webtour Need ID', required=False)
    webtour_useridno = fields.Char('Webtour User ID', required=False)
    webtour_groupidno = fields.Char('Webtour Groupidno', required=False)
    webtour_deleted = fields.Boolean('Webtour Deleted', default=False)
    webtour_startdatetime = fields.Char('Webtour StartDateTime', required=False)
    webtour_startdestinationidno = fields.Char('Webtour StartDestinationIdNo', required=False)
    webtour_startnote = fields.Char('Webtour StartNote', required=False)
    webtour_enddatetime = fields.Char('Webtour EndDateTime', required=False)
    webtour_enddestinationidno = fields.Char('Webtour EndDestinationIdNo', required=False)
    webtour_endnote = fields.Char('Webtour EndNote', required=False)
    webtour_CurrentDateTime = fields.Char('CurrentDateTime', required=False)
    webtour_touridno = fields.Char('Webtour TourIDno', required=False)

    WebtourUsNeedChanges_ids= fields.One2many('campos.webtourusneed.changes','WebtourUsNeed_id',ondelete='set null')
    status = fields.Selection([('1', 'Initiated'),
                               ('2', 'In Planning'),
                               ('3', 'Planned'),
                               ('4', 'Change Pending'),
                               ('5', 'Rejected')], default=False, string='Status')
    
    
    @api.multi
    def write(self, vals):
        _logger.info("WebtourUsNeed Write Entered %s", vals.keys())
        ret = super(WebtourUsNeed, self).write(vals)
        
        for need in self:
     
            if  ('campos_TripType_id' in vals 
                or 'travelgroup' in vals
                or 'campos_traveldate' in vals
                or 'campos_startdestinationidno' in vals
                or 'campos_enddestinationidno' in vals 
                ):
                #_logger.info("WebtourUsNeed Write Change %s %s", need.campos_traveldate,fields.Date.from_string(need.campos_startdatetime))
                need.calc_travelneed_id()
             
        return ret
    
    @api.model
    def create(self, vals):
        _logger.info("WebtourUsNeed Create Entered %s", vals.keys())
        rec = super(WebtourUsNeed, self).create(vals)
        rec.calc_travelneed_id()       
        return rec
    
    @api.one
    def calc_travelneed_id(self):
        # find travelneed matching usneeds
        rs_travelneed= self.env['event.registration.travelneed'].search([('registration_id', '=', self.participant_id.registration_id.id),('travelgroup', '=', self.travelgroup),('campos_TripType_id', '=', self.campos_TripType_id.id)
                                                                        ,('startdestinationidno.id', '=', self.campos_startdestinationidno),('enddestinationidno.id', '=', self.campos_enddestinationidno),('traveldate', '=', self.campos_traveldate)])
    
        if self.campos_TripType_id.id and self.campos_startdestinationidno and self.campos_enddestinationidno:
            _logger.info("calc_travelneed_id Entered %s %s %s %s %s %s %s",self.travelneed_id.traveldate , len(rs_travelneed),self.participant_id.registration_id.id,self.campos_TripType_id.id,self.campos_startdestinationidno,self.campos_enddestinationidno,self.campos_traveldate)
            if rs_travelneed:
                #_logger.info("WebtourUsNeed Write Change AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA %s %s",self.campos_traveldate,fields.Date.from_string(self.webtour_startdatetime))
                if (self.travelneed_id == False) or (self.travelneed_id != rs_travelneed[0]):
                    #_logger.info("WebtourUsNeed Write Change BBBBBBBBBBBBBBBBBBBBBBBBBBB")  
                    self.travelneed_id=rs_travelneed[0]     
            else:
                dicto0 = {}
                dicto0["registration_id"] = self.participant_id.registration_id.id
                dicto0["travelgroup"] =self.travelgroup
                dicto0["name"] = 'Bus Trip'   
                dicto0["campos_TripType_id"] = self.campos_TripType_id.id
                dicto0["startdestinationidno"] = self.campos_startdestinationidno
                dicto0["enddestinationidno"] = self.campos_enddestinationidno
                dicto0["traveldate"] = fields.Date.from_string(self.campos_traveldate)
                dicto0["deadline"] ='Select'
                _logger.info("calc_travelneed_id Create %s",dicto0)
                self.travelneed_id = self.env['event.registration.travelneed'].create(dicto0)     
        else:
            _logger.info("calc_travelneed_id Entered with insufficent data %s %s %s %s %s %s %s",self.travelneed_id.traveldate , len(rs_travelneed),self.participant_id.registration_id.id,self.campos_TripType_id.id,self.campos_startdestinationidno,self.campos_enddestinationidno,fields.Date.from_string(self.campos_traveldate))
            
    @api.multi
    @api.depends('campos_writeseq','campos_transferedseq') 
    def _computediff(self):
        for record in self: 
            record.campos_transfered = record.campos_writeseq == record.campos_transferedseq
    
    @api.one
    def get_create_webtour_need(self):
                
        def get_tag_data(nodetag):
            try:
                tag_data = response_doc.getElementsByTagName(nodetag)[0].firstChild.data
            except:
                tag_data = False

            return tag_data
        
        def get_tag_data_from_node(node,nodetag):
            try:
                tag_data = node.getElementsByTagName(nodetag)[0].firstChild.data
            except:
                tag_data = None

            return tag_data
        '''
        def camposeqwebtour():
            sd = (fields.Date.from_string(self.campos_startdatetime) == fields.Date.from_string(self.webtour_startdatetime))
            sdi = (self.campos_startdestinationidno ==  self.webtour_startdestinationidno)
            sn = ((self.campos_startnote ==  self.webtour_startnote) or (self.campos_startnote == "" and self.webtour_startnote == False)) 
            edi = (self.campos_enddestinationidno ==  self.webtour_enddestinationidno)  
            en = ((self.campos_endnote ==  self.webtour_endnote) or (self.campos_endnote == "" and self.webtour_endnote == False))
            
            _logger.info("camposeqwebtour %s %s %s %s %s %s %s",self.campos_startdatetime , fields.Date.from_string(self.webtour_startdatetime) ,sd,  sdi,sn , edi , en)
            
            return sd and sdi and sn and edi and en 
'''
        def updatewebtourfields():
            dicto ={}
            if self.webtour_needidno != get_tag_data("a:IDno"): dicto['webtour_needidno'] = get_tag_data("a:IDno")
            if self.webtour_startdatetime != get_tag_data("a:StartDateTime"): dicto['webtour_startdatetime'] = get_tag_data("a:StartDateTime")
            if self.webtour_startdestinationidno != get_tag_data("a:StartDestinationIDno"): dicto['webtour_startdestinationidno'] = get_tag_data("a:StartDestinationIDno")
            if self.webtour_startnote != get_tag_data("a:StartNote"): dicto['webtour_startnote'] = get_tag_data("a:StartNote")
            if self.webtour_enddatetime != get_tag_data("a:EndDateTime"): dicto['webtour_enddatetime'] = get_tag_data("a:EndDateTime")
            if self.webtour_enddestinationidno != get_tag_data("a:EndDestinationIDno"): dicto['webtour_enddestinationidno'] = get_tag_data("a:EndDestinationIDno")
            if self.webtour_endnote != get_tag_data("a:EndNote"): dicto['webtour_endnote'] = get_tag_data("a:EndNote")
            if self.webtour_touridno != get_tag_data("a:TourIDno"): dicto['webtour_touridno'] = get_tag_data("a:TourIDno")
            if self.webtour_CurrentDateTime != get_tag_data("CurrentDateTime"): dicto['webtour_CurrentDateTime'] = get_tag_data("CurrentDateTime")
            if self.campos_transferedseq != self.campos_writeseq: dicto['campos_transferedseq'] = self.campos_writeseq
            if len(dicto) > 0:
                self.write(dicto)

        def updatewebtourfields_fromnode(node):
            dicto ={}
            if self.webtour_needidno != get_tag_data_from_node(node,"a:IDno"): dicto['webtour_needidno'] = get_tag_data_from_node(node,"a:IDno")
            if self.webtour_startdatetime != get_tag_data_from_node(node,"a:StartDateTime"): dicto['webtour_startdatetime'] = get_tag_data_from_node(node,"a:StartDateTime")
            if self.webtour_startdestinationidno != get_tag_data_from_node(node,"a:StartDestinationIDno"): dicto['webtour_startdestinationidno'] = get_tag_data_from_node(node,"a:StartDestinationIDno")
            if self.webtour_startnote != get_tag_data_from_node(node,"a:StartNote"): dicto['webtour_startnote'] = get_tag_data_from_node(node,"a:StartNote")
            if self.webtour_enddatetime != get_tag_data_from_node(node,"a:EndDateTime"): dicto['webtour_enddatetime'] = get_tag_data_from_node(node,"a:EndDateTime")
            if self.webtour_enddestinationidno != get_tag_data_from_node(node,"a:EndDestinationIDno"): dicto['webtour_enddestinationidno'] = get_tag_data_from_node(node,"a:EndDestinationIDno")
            if self.webtour_endnote != get_tag_data_from_node(node,"a:EndNote"): dicto['webtour_endnote'] = get_tag_data_from_node(node,"a:EndNote")
            if self.webtour_touridno != get_tag_data_from_node(node,"a:TourIDno"): dicto['webtour_touridno'] = get_tag_data_from_node(node,"a:TourIDno")
            if self.webtour_CurrentDateTime != get_tag_data_from_node(node,"CurrentDateTime"): dicto['webtour_CurrentDateTime'] = get_tag_data_from_node(node,"CurrentDateTime")
            if self.campos_transferedseq != self.campos_writeseq: dicto['campos_transferedseq'] = self.campos_writeseq
            if len(dicto) > 0:
                self.write(dicto)
         
        _logger.info("Here we go !!!!!!!!!!!")
                          
        if  self.webtour_groupidno == False or self.webtour_useridno == False or self.campos_startdestinationidno == False or self.campos_traveldate == False or self.campos_enddestinationidno == False:
            _logger.info("get_create_usneed_tron: Info missing %s %s %s %s %s", self.webtour_useridno,self.webtour_groupidno,self.campos_traveldate,self.campos_startdestinationidno,self.campos_enddestinationidno)
            return True

        needtransfered = False
        # check for changes in travel data
        if ((self.campos_demandneeded != self.campos_transfered_demandneeded) 
            or (self.travelneed_deadline != self.campos_transfered_deadline)
            or (self.travelneed_travelconnectiondetails != self.campos_transfered_travelconnectiondetails)
            or (self.campos_traveldate != self.campos_transfered_traveldate)
            or (self.campos_startdestinationidno != self.campos_transfered_startdestinationidno)
            or (self.campos_enddestinationidno != self.campos_transfered_enddestinationidno)         
            ):
            _logger.info("1A. Change in travel data")       
                 
            #compose note (for non Danish groups)
            note = False
            if self.travelneed_id.deadline and (self.travelneed_id.deadline != 'Select'):
                note = 'Deadline: ' + self.travelneed_id.deadline
            if self.travelneed_id.travelconnectiondetails:
                if note:
                    note = note + ', '
                note = note + 'Connection: ' + self.travelneed_id.travelconnectiondetails     
        
            if self.travelneed_id.campos_TripType_id.returnjourney: #Return jurney
                startnote = False
                endnote = note
                if self.travelneed_id.deadline and (self.travelneed_id.deadline != 'Select'):
                    enddatetime = self.campos_traveldate+"T"+self.travelneed_id.deadline
                else:
                    enddatetime = self.campos_traveldate
                startdatetime = self.campos_traveldate
            else: 
                startnote = note
                endnote = False
                if self.travelneed_id.deadline and (self.travelneed_id.deadline != 'Select'):
                    startdatetime = self.campos_traveldate+"T"+self.travelneed_id.deadline
                else:
                    startdatetime = self.campos_traveldate
                enddatetime = self.campos_traveldate                
            
            if (self.campos_demandneeded == True): # there is demand
                _logger.info("2A. demand needed")
                if (self.webtour_needidno == False or self.webtour_needidno == "0"): #no need known, so try to create
                    _logger.info("3. No need - Try to create")
                    request="UserIDno=" + self.webtour_useridno
                    request=request+"&GroupIDno="+self.webtour_groupidno
                    request=request+"&StartDestinationIDno="+self.campos_startdestinationidno
                    request=request+"&EndDestinationIDno="+self.campos_enddestinationidno
                    request=request+"&StartDateTime="+startdatetime
                    request=request+"&EndDateTime="+enddatetime
                    if startnote == False:
                        startnote=""
                    if endnote == False:
                        endnote=""
                           
                    request=request+"&StartNote="+startnote
                    request=request+"&EndNote="+endnote                        
                    
                    _logger.info("3a. request %s",request)
                    response_doc=webtourinterface.usneed_create(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),request)
                    
                    idno = get_tag_data("a:IDno") #Let us check response
                                       
                    if (idno <> "0") and idno:
                        _logger.info("4a. New usNeed Created")
                        updatewebtourfields()
                        needtransfered = True
                    else: 
                        _logger.info("4b.usNeed NOT created") 
                        if get_tag_data("a:Description") == "Need already exist" :
                            _logger.info("5. Ohh usNeed already exist")
                            response_doc=webtourinterface.usneed_GetByGroupIDno(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),self.webtour_groupidno)
                            #response_doc2 = minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usNeed/GetByGroupIDno/?GroupIDno=' + self.webtour_groupidno}).responce)
                            usNeeds=response_doc.getElementsByTagName('a:usNeed')
                            for node in usNeeds:
                                try:
                                    StartDestinationIDno = node.getElementsByTagName("a:StartDestinationIDno")[0].firstChild.data
                                    EndDestinationIDno = node.getElementsByTagName("a:EndDestinationIDno")[0].firstChild.data
                                    UserIDno = node.getElementsByTagName("a:UserIDno")[0].firstChild.data
                                    if (self.campos_startdestinationidno == StartDestinationIDno and self.campos_enddestinationidno == EndDestinationIDno and self.webtour_useridno == UserIDno):
                                        _logger.info("6. Found a usNeed matching %s", node.toprettyxml(indent="   "))
                                        self.webtour_needidno = get_tag_data_from_node(node,"a:IDno") # save found usNeed IDno
                                        
                                        request="NeedIDno="+self.webtour_needidno + "&" + request
                                        response_doc=webtourinterface.usneed_update(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),request)

                                        if get_tag_data("a:IDno") <> "0": # Stil OK?
                                            updatewebtourfields()
                                            needtransfered = True
                                        else:
                                            _logger.info("7. Still problem with the response %s %s", request,response_doc.toprettyxml(indent="   "))
                                            
                                        break
                                except:
                                    pass                    
                        else:
                            self.campos_transferedseq = False
                            _logger.info("8. Not possible to update usNeed!!!!!!!!!!!!! %s", response_doc.toprettyxml(indent="   ")) 
                else: # There is a Need to try to update
                    request="NeedIDno="+self.webtour_needidno      
                    request=request+"&UserIDno="+self.webtour_useridno
                    request=request+"&GroupIDno="+self.webtour_groupidno
                    
                    if ((self.travelneed_deadline != self.campos_transfered_deadline)
                        or (self.travelneed_travelconnectiondetails != self.campos_transfered_travelconnectiondetails)):
                        if startnote == False:
                            startnote=""  
                        request=request+"&StartNote="+startnote
                        
                        if endnote == False:
                            endnote="" 
                        request=request+"&EndNote="+endnote
                        
                        request=request+"&StartDateTime="+startdatetime
                        request=request+"&EndDateTime="+enddatetime      
                    else:        
                        if (self.campos_traveldate != self.campos_transfered_traveldate):
                            request=request+"&StartDateTime="+startdatetime
                            request=request+"&EndDateTime="+enddatetime                        
                        
                    if (self.campos_startdestinationidno != self.campos_transfered_startdestinationidno):
                        request=request+"&StartDestinationIDno="+self.campos_startdestinationidno
                           
                    if (self.campos_enddestinationidno != self.campos_transfered_enddestinationidno):
                        request=request+"&EndDestinationIDno="+self.campos_enddestinationidno                          
                    
                    response_doc=webtourinterface.usneed_update(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),request)

                    if get_tag_data("a:IDno") <> "0": # Stil OK?
                        _logger.info("9A. Need updated with the Request %s Response %s", request, response_doc.toprettyxml(indent="   ")) 
                        updatewebtourfields()
                        needtransfered = True
                    else:
                        _logger.info("9B. Problem with the Request %s Response %s", request, response_doc.toprettyxml(indent="   "))
                        if get_tag_data("a:Description") == "NeedIDno not found" :
                            _logger.info("15. webtour_needidno %s removed from usNeed %s", self.webtour_needidno, self.id)
                            self.webtour_needidno=False
            
                if (needtransfered): ## usNeed has been updated :-)   
                    if self.campos_transfered_demandneeded != True: self.campos_transfered_demandneeded = True
                    if self.campos_transfered_deadline != self.travelneed_deadline: self.campos_transfered_deadline = self.travelneed_deadline
                    if self.campos_transfered_travelconnectiondetails != self.travelneed_travelconnectiondetails: self.campos_transfered_travelconnectiondetails = self.travelneed_travelconnectiondetails
                    if self.campos_transfered_traveldate != self.campos_traveldate:self.campos_transfered_traveldate = self.campos_traveldate
                    if self.campos_transfered_startdatetime != startdatetime: self.campos_transfered_startdatetime = startdatetime
                    if self.campos_transfered_enddatetime != enddatetime : self.campos_transfered_enddatetime = enddatetime
                    if self.campos_transfered_startdestinationidno != self.campos_startdestinationidno: self.campos_transfered_startdestinationidno = self.campos_startdestinationidno
                    if self.campos_transfered_enddestinationidno != self.campos_enddestinationidno: self.campos_transfered_enddestinationidno = self.campos_enddestinationidno
                    if self.campos_transfered_startnote != startnote: self.campos_transfered_startnote = startnote
                    if self.campos_transfered_endnote != endnote: self.campos_transfered_endnote = endnote
                    if self.webtour_deleted: self.webtour_deleted = False # Clear Delete falg
                    self.get_webtour_need_change()
                                                                            
            else: #No demand now        
                _logger.info("2B. No demand needed")
                if not self.webtour_deleted:
                    _logger.info("10. Deleting usNeed %s", self.webtour_needidno)
                    if self.webtour_needidno and (self.webtour_needidno <> '0'):
                        _logger.info("11. There is usNeedID No - Try to delete")
                        response_doc=webtourinterface.usneed_delete(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),self.webtour_needidno)                         
                        updatewebtourfields()
                        self.get_webtour_need_change()
                        _logger.info("12. Deleted responce %s", response_doc.toprettyxml(indent="   "))
                    self.webtour_deleted = True
        else: 
            _logger.info("1B. No changes in travel data")
            if self.webtour_needidno and self.webtour_needidno <> '0' and self.webtour_deleted == False:
                _logger.info("13. There is usNeed IDno")
                response_doc=webtourinterface.usneed_getbyidno(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),self.webtour_needidno)
                
                idno = get_tag_data("a:IDno")
                if idno <> "0":
                    _logger.info("14A. Got usNeed reponce")
                    updatewebtourfields()
                    self.get_webtour_need_change()
                else:
                    _logger.info("14B. Dit not Get usNeed reponce !!!!!!!!!!!!!!!!!!!!! %s %s",self.webtour_needidno, response_doc.toprettyxml(indent="   "))
                  
        self.env.cr.commit()                                                                
        return True
    
    @api.one
    def get_webtour_need_change(self):
         
        response_doc=webtourinterface.usneed_GetPending_ByIDno(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),self.webtour_needidno)
        usContent = response_doc.getElementsByTagName("Content")

        element = usContent[0]
        i=1 # next element
                                  
        for rec in self.WebtourUsNeedChanges_ids:
            dicto={}
            dicto['WebtourUsNeed_id'] = self.id
            if element != None:
                for n in element.childNodes:
                    if n.firstChild != None:
                        dicto[n.nodeName.replace('a:','').lower()]=n.firstChild.nodeValue
                    else:
                        dicto[n.nodeName.replace('a:','').lower()]=False
                
                if len(usContent) > i:
                    element = usContent[i]
                    i = i + 1
                else:
                    element = None
                rec.write(dicto)
            else:
                rec.delete()
        
        while element != None:
            dicto={}
            dicto['WebtourUsNeed_id'] = self.id

            for n in element.childNodes:
                if n.firstChild != None:
                    dicto[n.nodeName.replace('a:','').lower()]=n.firstChild.nodeValue
                else:
                    dicto[n.nodeName.replace('a:','').lower()]=False
                       
            self.env['campos.webtourusneed.changes'].create(dicto)
                                
            if len(usContent) > i:
                element = usContent[i]
                i = i + 1
            else:
                element = None
    
    @api.model
    def get_create_usneed_tron(self):
        MAX_LOOPS_usNeed = 100  #Max No of Needs pr Scheduled call
        
        # find usneeds not beeing transfered
        rs_needs= self.env['campos.webtourusneed'].search([('campos_transfered', '=', False),('campos_demandneeded', '=', True)])

        _logger.info("get_create_usneed_tron: Here we go... %i usNeeds to update in Webtour", len(rs_needs))
        
        loops=0
        for need in rs_needs:
            
            if  need.webtour_groupidno == False or need.webtour_useridno == False or need.campos_startdestinationidno == False or need.campos_traveldate == False or need.campos_enddestinationidno == False:
                _logger.info("get_create_usneed_tron: Info missing %s %s %s %s %s", need.webtour_useridno,need.webtour_groupidno,need.campos_startdestinationidno,need.campos_traveldate,need.campos_enddestinationidno)
            else:
                need.get_create_webtour_need()
                loops = loops + 1
            
            if loops > MAX_LOOPS_usNeed:
                break
    
    @api.multi
    def updatewebtourtofromusneeds(self):
        # needs = self.env['campos.webtourusneed'].search([('participant_id','<>',False)])
        
        _logger.info("updatewebtourtofromusneeds: Here we go...%s",len(self))
        for need in self: # (change to needs to update all needs)
            if need.participant_id <> False:
                webtourconfig= self.env['campos.webtourconfig'].search([('event_id', '=', self.participant_id.registration_id.event_id.id)])
                
                if need.campos_TripType_id==webtourconfig.tocamp_campos_TripType_id:
                    need.campos_demandneeded = need.participant_id.transport_to_camp
                    need.campos_startdatetime = need.participant_id.tocampdate
                    need.campos_enddatetime = need.participant_id.tocampdate
                    need.participant_id.tocampfromdestination_id = need.participant_id.registration_id.webtourdefaulthomedestination
                    need.campos_startdestinationidno = need.participant_id.tocampfromdestination_id.destinationidno                    
                    need.webtour_useridno = need.participant_id.webtourususeridno
                    need.webtour_groupidno = need.participant_id.webtourusgroupidno
                    need.campos_writeseq = self.env['ir.sequence'].get('webtour.transaction')  
                
                if need.campos_TripType_id==webtourconfig.fromcamp_campos_TripType_id :
                    need.campos_demandneeded = need.participant_id.transport_from_camp
                    need.campos_startdatetime = need.participant_id.fromcampdate
                    need.campos_enddatetime = need.participant_id.fromcampdate
                    need.participant_id.fromcamptodestination_id = need.participant_id.registration_id.webtourdefaulthomedestination
                    need.campos_enddestinationidno = need.participant_id.fromcamptodestination_id.destinationidno
                    need.webtour_useridno = need.participant_id.webtourususeridno
                    need.webtour_groupidno = need.participant_id.webtourusgroupidno                     
                    need.campos_writeseq = self.env['ir.sequence'].get('webtour.transaction')
                    
                need.get_create_webtour_need()
                
        return True

    @api.multi
    def updateusneedtriptypes(self):
        pars = self.env['campos.event.participant'].search([('registration_id.event_id.id','=',self.participant_id.registration_id.event_id.id)])
        webtourconfig= self.env['campos.webtourconfig'].search([('event_id', '=', self.participant_id.registration_id.event_id.id)])
        for par in pars:

            if (par.tocampusneed_id.id <> False):
                _logger.info("updateusneedtriptypes To Camp %s, %s, %s",par.id,par.name,par.registration_id.id)
                par.tocampusneed_id.campos_TripType_id=webtourconfig.tocamp_campos_TripType_id.id
                par.tocampusneed_id.campos_enddestinationidno=webtourconfig.campdestinationid.destinationidno
                par.tocampusneed_id.campos_writeseq = self.env['ir.sequence'].get('webtour.transaction')  
                
            if (par.fromcampusneed_id.id <> False): 
                _logger.info("updateusneedtriptypes From Camp %s, %s, %s",par.id,par.name,par.registration_id.id)                              
                par.fromcampusneed_id.campos_TripType_id=webtourconfig.fromcamp_campos_TripType_id.id
                par.fromcampusneed_id.campos_startdestinationidno=webtourconfig.campdestinationid.destinationidno
                par.fromcampusneed_id.campos_writeseq = self.env['ir.sequence'].get('webtour.transaction')  
    
class WebtourNeedOverview(models.Model):
    _name = 'campos.webtourusneed.overview'
    _auto = False
    _log_access = False

    registration_id = fields.Many2one('event.registration','Registration ID')
    travelgroup = fields.Char('Travel Group')
    webtour_groupidno = fields.Char('Webtour us Group ID no')
    campos_TripType_id = fields.Many2one('campos.webtourconfig.triptype','Webtour Trip Type')    
    campos_transfered_startdatetime = fields.Char('CampOs StartDateTime')
    campos_startdestinationidno = fields.Char('CampOs Start Destination IdNo')
    campos_enddestinationidno = fields.Char('CampOs End Destination IdNo')    
    pax = fields.Integer('CampOS PAX')
        
    excessdemand = fields.Integer('Excess demand in WEBTour')
    nottransfered = fields.Integer('Needs Not transfered to WEBTour')
    notdeleted = fields.Integer('Needs Not Deleted in WEBTour')
    startdestdiffer = fields.Integer('Needs where start destination differ')    
    enddestdiffer = fields.Integer('Needs where end destination differ')   
    startdatetimediffer = fields.Integer('Needs where startdatetime differ')
    enddatetimediffer = fields.Integer('Needs where end datetime differ')
    startnotediffer = fields.Integer('Needs where start note differ')    
    endnotediffer = fields.Integer('Needs where end note differ')
     
    
    def init(self, cr, context=None):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_webtourusneed_overview as
                    SELECT case when travelneed_id is not null then travelneed_id else -min(campos_webtourusneed.id) end as id, campos_event_participant.registration_id as registration_id,travelgroup,webtour_groupidno, "campos_TripType_id",campos_transfered_startdatetime::timestamp,campos_startdestinationidno,campos_enddestinationidno
                    , count(campos_webtourusneed.id) as pax
                    , sum(case when campos_demandneeded then 0 else 1 end) as excessdemand 
                    , sum(case when campos_transfered then 0 else 1 end) as nottransfered
                    , sum(case when campos_deleted and not webtour_deleted then 1 else 0 end) as notdeleted
                    , sum(case when webtour_startdestinationidno = campos_startdestinationidno then 0 else 1 end) as startdestdiffer
                    , sum(case when webtour_enddestinationidno = campos_enddestinationidno then 0 else 1 end) as enddestdiffer
                    , sum(case when campos_transfered_startdatetime::timestamp = webtour_startdatetime::timestamp then 0 else 1 end) as startdatetimediffer
                    , sum(case when campos_transfered_enddatetime::timestamp = webtour_enddatetime::timestamp then 0 else 1 end) as enddatetimediffer
                    , sum(case when (case when campos_transfered_startnote isnull then '' else campos_transfered_startnote end) = (case when webtour_startnote isnull then '' else webtour_startnote end) then 0 else 1 end) as startnotediffer
                    , sum(case when (case when campos_transfered_endnote isnull then '' else campos_transfered_endnote end) = (case when webtour_endnote isnull then '' else webtour_endnote end) then 0 else 1 end) as endnotediffer
                    FROM campos_webtourusneed
                    left outer join campos_event_participant on campos_event_participant.id = participant_id
                    where campos_demandneeded or( not webtour_deleted and webtour_needidno::INT4>0)
                    group by travelneed_id, travelgroup            
                    ,campos_event_participant.registration_id,webtour_groupidno,"campos_TripType_id",campos_transfered_startdatetime::timestamp
                    ,campos_startdestinationidno
                    ,campos_enddestinationidno
                    """
                    )

class WebtourUsNeedChanges(models.Model):
    _name = 'campos.webtourusneed.changes'
    WebtourUsNeed_id = fields.Many2one('campos.webtourusneed','id', ondelete='set null')
    idno = fields.Char('webtour_needidno')
    touridno = fields.Char('TourIDno', required=False)
    useridno = fields.Char('UserIDno', required=False)
    groupidno = fields.Char('GroupIDno', required=False)
    startdatetime = fields.Char('StartDateTime', required=False)
    startdestinationidno = fields.Char('StartDestinationIDno', required=False)
    startnote = fields.Char('StartNote', required=False)
    enddatetime = fields.Char('EndDateTime', required=False)
    enddestinationidno = fields.Char('EndDestinationIDno', required=False)
    endnote = fields.Char('EndNote', required=False)
    action = fields.Char('Action', required=False)
    actiondatetime = fields.Char('ActionDateTime', required=False)
    currentdatetime = fields.Char('CurrentDateTime', required=False)
    
    def sameasWebtourusneed(self):
        sdt = (self.WebtourUsNeed_id.webtour_startdatetime == fields.Date.from_string(self.startdatetime)) 
        sdi = (self.WebtourUsNeed_id.webtour_startdestinationidno ==  self.startdestinationidno)
        sn = ((self.WebtourUsNeed_id.webtour_startnote ==  self.startnote) or (self.WebtourUsNeed_id.webtour_startnote == "" and self.startnote == False)) 
        edi = (self.WebtourUsNeed_id.webtour_enddestinationidno ==  self.enddestinationidno) 
        en = ((self.WebtourUsNeed_id.cwebtour_endnote ==  self.endnote) or (self.WebtourUsNeed_id.webtour_endnote == "" and self.endnote == False))
        #_logger.info("sameasWebtourusneed %s %s %s %s %s",sdt , sdi , sn , edi , en)
        _logger.info("sameasWebtourusneed")
        return sdt and sdi and sn and edi and en