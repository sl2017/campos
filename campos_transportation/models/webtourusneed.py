# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
from ..interface import webtourinterface

import logging

_logger = logging.getLogger(__name__)

class WebtourUsNeed(models.Model):
    _name = 'campos.webtourusneed'
    participant_id = fields.Many2one('campos.event.participant','Participant ID', ondelete='set null')
    travelgroup = fields.Char('Travel Group')
    campos_deleted = fields.Boolean('CampOs Deleted', default=False)
    campos_demandneeded = fields.Boolean('CampOs Demand Needed', default=False)
    campos_TripType_id = fields.Many2one('campos.webtourusneed.triptype','Webtour_TripType', ondelete='set null')
    campos_startdatetime = fields.Char('CampOs StartDateTime', required=False)
    campos_startdestinationidno = fields.Char('CampOs StartDestinationIdNo', required=False)
    campos_startnote = fields.Char('CampOs StartNote', required=False)
    campos_enddatetime = fields.Char('CampOs EndDateTime', required=False)
    campos_enddestinationidno = fields.Char('CampOs EndDestinationIdNo', required=False)
    campos_endnote = fields.Char('CampOs EndNote', required=False)
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
    travelneed_id= fields.Many2one('event.registration.travelneed','Travel need',ondelete='set null')
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
                or 'campos_startdatetime' in vals
                or 'campos_startdestinationidno' in vals
                or 'campos_enddestinationidno' in vals 
                ):
                #_logger.info("WebtourUsNeed Write Change %s %s", need.campos_startdatetime,fields.Date.from_string(need.campos_startdatetime))
                need.calc_travelneed_id()
             
        return ret
    
    @api.one
    def calc_travelneed_id(self):
                # find travelneed matching usneeds
                rs_travelneed= self.env['event.registration.travelneed'].search([('registration_id', '=', self.participant_id.registration_id.id),('travelgroup', '=', self.travelgroup),('campos_TripType_id', '=', self.campos_TripType_id.id)
                                                                                 ,('startdestinationidno.id', '=', self.campos_startdestinationidno),('enddestinationidno.id', '=', self.campos_enddestinationidno),('traveldate', '=', fields.Date.from_string(self.campos_startdatetime))])
                
                #_logger.info("calc_travelneed_id Entered %s %s %s %s",self.travelneed_id.traveldate , rs_travelneed,self.campos_startdatetime,fields.Date.from_string(self.campos_startdatetime))
                if rs_travelneed:
                    #_logger.info("WebtourUsNeed Write Change AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA %s %s",self.campos_startdatetime,fields.Date.from_string(self.webtour_startdatetime))
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
                    dicto0["traveldate"] = fields.Date.from_string(self.campos_startdatetime)
                    dicto0["deadline"] ='Select'
                    _logger.info("calc_travelneed_id Create %s",dicto0)
                    self.travelneed_id = self.env['event.registration.travelneed'].create(dicto0)          
            
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
        
        def camposeqwebtour():
            sd = (fields.Date.from_string(self.campos_startdatetime) == fields.Date.from_string(self.webtour_startdatetime))
            sdi = (self.campos_startdestinationidno ==  self.webtour_startdestinationidno)
            sn = ((self.campos_startnote ==  self.webtour_startnote) or (self.campos_startnote == "" and self.webtour_startnote == False)) 
            edi = (self.campos_enddestinationidno ==  self.webtour_enddestinationidno)  
            en = ((self.campos_endnote ==  self.webtour_endnote) or (self.campos_endnote == "" and self.webtour_endnote == False))
            
            _logger.info("camposeqwebtour %s %s %s %s %s %s %s",self.campos_startdatetime , fields.Date.from_string(self.webtour_startdatetime) ,sd,  sdi,sn , edi , en)
            
            return sd and sdi and sn and edi and en 

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
            if self.webtour_needidno != idno: dicto['webtour_needidno'] = idno
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
               
        if self.campos_startnote== False : 
            self.campos_startnote=""
                    
        s = ''
        if self.travelneed_id.deadline and (self.travelneed_id.deadline != 'Select'):
            s = 'Deadline: ' + self.travelneed_id.deadline
        if self.travelneed_id.travelconnectiondetails:
            if len(s) > 0:
                s = s + ', '
            s = s + 'Connection: ' + self.travelneed_id.travelconnectiondetails    
        
        if self.campos_startnote != s:
            self.campos_startnote = s
            self.campos_writeseq = self.env['ir.sequence'].get('webtour.transaction')


        if self.campos_endnote== False : 
            self.campos_endnote=""
            
        if self.campos_enddatetime == False:
            self.campos_enddatetime = self.campos_startdatetime
            
        
        if  self.webtour_groupidno == False or self.webtour_useridno == False or self.campos_startdestinationidno == False or self.campos_startdatetime == False or self.campos_enddestinationidno == False or self.campos_enddatetime == False:
            _logger.info("get_create_usneed_tron: Info missing %s %s %s %s %s %s", self.webtour_useridno,self.webtour_groupidno,self.campos_startdestinationidno,self.campos_startdatetime,self.campos_enddestinationidno,self.campos_enddatetime)
            return True
        
        if (self.campos_transferedseq <> self.campos_writeseq): #new campos data
            _logger.info("11111111111")
            if (self.campos_demandneeded == True): # there is need
                _logger.info("222222222")
                if (self.webtour_needidno == False or self.webtour_needidno == "0"): #no need known, so try to create
                    _logger.info("3333333333")
                    request="UserIDno="+self.webtour_useridno
                    request=request+"&GroupIDno="+self.webtour_groupidno
                    request=request+"&StartDestinationIDno="+self.campos_startdestinationidno
                    request=request+"&StartDateTime="+self.campos_startdatetime
                    request=request+"&StartNote="+self.campos_startnote
                    request=request+"&EndDestinationIDno="+self.campos_enddestinationidno
                    request=request+"&EndDateTime="+self.campos_enddatetime
                    request=request+"&EndNote="+self.campos_endnote
                   
                    response_doc=webtourinterface.usneed_create(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),request)
                    if self.status != '1': self.status = '1'
                    if self.webtour_deleted: self.webtour_deleted = False                  
                    
                    idno = get_tag_data("a:IDno")
                    
                    if idno <> "0":
                        _logger.info("4444444444")
                        updatewebtourfields()
                    else: 
                        _logger.info("5555555555")
                        if get_tag_data("a:Description") == "Need already exist" :
                            _logger.info("Ohh usNeed already exist")
                            response_doc=webtourinterface.usneed_GetByGroupIDno(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),self.webtour_groupidno)
                            usNeeds=response_doc.getElementsByTagName('a:usNeed')
                            for node in usNeeds:
                                try:
                                    StartDestinationIDno = node.getElementsByTagName("a:StartDestinationIDno")[0].firstChild.data
                                    EndDestinationIDno = node.getElementsByTagName("a:EndDestinationIDno")[0].firstChild.data
                                    UserIDno = node.getElementsByTagName("a:UserIDno")[0].firstChild.data
                                    if (self.campos_startdestinationidno == StartDestinationIDno and self.campos_enddestinationidno == EndDestinationIDno and self.webtour_useridno == UserIDno):
                                        dicto ={}
                                        if self.webtour_needidno != idno: dicto['webtour_needidno'] = idno
                                        if self.webtour_startdatetime != get_tag_data_from_node(node,"a:StartDateTime"): dicto['webtour_startdatetime'] = get_tag_data_from_node(node,"a:StartDateTime")
                                        if self.webtour_startdestinationidno != get_tag_data_from_node(node,"a:StartDestinationIDno"):dicto['webtour_startdestinationidno'] = get_tag_data_from_node(node,"a:StartDestinationIDno")
                                        if self.webtour_startnote != get_tag_data_from_node(node,"a:StartNote"):dicto['webtour_startnote'] = get_tag_data_from_node(node,"a:StartNote")
                                        if self.webtour_enddatetime != get_tag_data_from_node(node,"a:EndDateTime"):dicto['webtour_enddatetime'] = get_tag_data_from_node(node,"a:EndDateTime")
                                        if self.webtour_enddestinationidno != get_tag_data_from_node(node,"a:EndDestinationIDno"):dicto['webtour_enddestinationidno'] = get_tag_data_from_node(node,"a:EndDestinationIDno")
                                        if self.webtour_endnote != get_tag_data_from_node(node,"a:EndNote"):dicto['webtour_endnote'] = get_tag_data_from_node(node,"a:EndNote")
                                        if self.webtour_touridno != get_tag_data_from_node(node,"a:TourIDno"):dicto['webtour_touridno'] = get_tag_data_from_node(node,"a:TourIDno")
                                        if self.webtour_CurrentDateTime != get_tag_data_from_node(node,"CurrentDateTime"):dicto['webtour_CurrentDateTime'] = get_tag_data_from_node(node,"CurrentDateTime")
                                        if self.campos_transferedseq != self.campos_writeseq:dicto['campos_transferedseq'] = self.campos_writeseq
                                        if len(dicto) > 0:
                                            self.write(dicto)
                                        _logger.info("Found a usNeed matching %s", node.toprettyxml(indent="   "))
                                        break
                                except:
                                    Ok = False                    
                        else:
                            self.campos_transferedseq = False
                            _logger.info("Not possible to update usNeed!!!!!!!!!!!!! %s", self)            
                else:#need to update
                    _logger.info("66666666666")
                    request="NeedIDno="+self.webtour_needidno
                    request=request+"&StartDestinationIDno="+self.campos_startdestinationidno
                    request=request+"&StartDateTime="+self.campos_startdatetime
                    request=request+"&StartNote="+self.campos_startnote
                    request=request+"&EndDestinationIDno="+self.campos_enddestinationidno
                    request=request+"&EndDateTime="+self.campos_enddatetime
                    request=request+"&EndNote="+self.campos_endnote
                                        
                    response_doc=webtourinterface.usneed_update(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),request)    
                    if self.webtour_deleted: self.webtour_deleted = False
                    
                    idno = get_tag_data("a:IDno")                    
                    if idno <> "0":
                        updatewebtourfields()
                    else:
                        self.campos_transferedseq = False
                        _logger.info("Can not update usNeed!!!!!!!!!!!!! %s", response_doc.toprettyxml(indent="   "))                                 
            else: # No need
                _logger.info("77777777777")
                if not self.webtour_deleted:
                    _logger.info("Deleting usNeed %s", self.webtour_needidno)
                    if self.webtour_needidno and (self.webtour_needidno <> '0'):
                        _logger.info("77777aaaaaaaaa")
                        response_doc=webtourinterface.usneed_delete(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),self.webtour_needidno)    
                        updatewebtourfields()
                        _logger.info("Deleted responce %s", response_doc.toprettyxml(indent="   "))
                    self.webtour_deleted = True
                    self.get_webtour_need_change()
        else: #no chenge in campos data
            _logger.info("88888888888")
            if self.webtour_needidno and self.webtour_needidno <> '0' and self.webtour_deleted == False:
                _logger.info("999999999")
                response_doc=webtourinterface.usneed_getbyidno(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),self.webtour_needidno)        
                
                idno = get_tag_data("a:IDno")
                if idno <> "0":
                    _logger.info("0000000000000")
                    updatewebtourfields()
                    self.get_webtour_need_change()            
                
                    if self.webtour_needidno:
                        _logger.info("AAAAAAAAAAAAAA")
                        self.get_webtour_need_change()
           
                    if camposeqwebtour() and self.campos_demandneeded:
                        _logger.info("BBBBBBBBBBBBBBBB")
                        if self.webtour_touridno == "-1":         
                            if self.status != '2': self.status = '2'
                        else:
                            if self.status != '3':self.status = '3'
                    else:
                        _logger.info("CCCCCCCCCCCCCC")
                        if self.campos_demandneeded == False:
                            _logger.info("DDDDDDDDDDDDDD")
                            for change in self.WebtourUsNeedChanges_ids.filtered(lambda r: r.action == "Delete"):
                                _logger.info("EEEEEEEEEEEEEE")
                                updatewebtourfields_fromnode(change)
                                self.webtour_deleted = True
                                if self.status <> False :self.status = False
                        else:
                            _logger.info("FFFFFFFFFFFF")       
                            for change in self.WebtourUsNeedChanges_ids.filtered(lambda r: r.action == "Update"):
                                if  not change.sameasWebtourusneed:
                                    request="NeedIDno="+self.webtour_needidno
                                    request=request+"&StartDestinationIDno="+self.campos_startdestinationidno
                                    request=request+"&StartDateTime="+self.campos_startdatetime
                                    request=request+"&StartNote="+self.campos_startnote
                                    request=request+"&EndDestinationIDno="+self.campos_enddestinationidno
                                    request=request+"&EndDateTime="+self.campos_enddatetime
                                    request=request+"&EndNote="+self.campos_endnote
                                    response_doc=webtourinterface.usneed_update(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),request)
                                    if self.webtour_deleted: self.webtour_deleted = False                       
                                if self.status != '4':self.status = '4'
                else: # Need must be deleted
                    _logger.info("GGGGGGGGGGGGG")
                    updatewebtourfields()
                    self.webtour_deleted = True
                    if self.status :self.status = False
                    
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
        MAX_LOOPS_usNeed = 1000  #Max No of Needs pr Scheduled call
        
        # find usneeds not beeing transfered
        rs_needs= self.env['campos.webtourusneed'].search([('campos_transfered', '=', False),('campos_demandneeded', '=', True)])

        _logger.info("get_create_usneed_tron: Here we go... %i usNeeds to update in Webtour", len(rs_needs))
        
        loops=0
        for need in rs_needs:
            
            if  need.webtour_groupidno == False or need.webtour_useridno == False or need.campos_startdestinationidno == False or need.campos_startdatetime == False or need.campos_enddestinationidno == False or need.campos_enddatetime == False:
                _logger.info("get_create_usneed_tron: Info missing %s %s %s %s %s %s", need.webtour_useridno,need.webtour_groupidno,need.campos_startdestinationidno,need.campos_startdatetime,need.campos_enddestinationidno,need.campos_enddatetime)
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

    
class WebtourTripType(models.Model):
    _description = 'Webtour Trip Types'
    _name = 'campos.webtourusneed.triptype'
   
    name = fields.Char('Webtour Trip Type', required=True)
    traveldate_ids = fields.One2many('campos.webtourusneed.triptype.date','campos_TripType_id','Travel Days')

class WebtourTripTypeDate(models.Model):
    _description = 'Webtour Trip Types Date'
    _name = 'campos.webtourusneed.triptype.date'
    campos_TripType_id = fields.Many2one('campos.webtourusneed.triptype','Webtour_TripType', ondelete='set null')
    name = fields.Date('Date', required=True) 
    date = fields.Date('Date', required=True) 
    
class WebtourNeedOverview(models.Model):
    _name = 'campos.webtourusneed.overview'
    _auto = False
    _log_access = False

    registration_id = fields.Many2one('event.registration','Registration ID')
    travelgroup = fields.Char('Travel Group')
    webtour_groupidno = fields.Char('Webtour us Group ID no')
    campos_TripType_id = fields.Many2one('campos.webtourusneed.triptype','Webtour Trip Type')    
    campos_startdatetime = fields.Char('CampOs StartDateTime')
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
                    SELECT case when travelneed_id is not null then travelneed_id else -min(campos_webtourusneed.id) end as id, event_registration.id as registration_id,travelgroup,webtour_groupidno, "campos_TripType_id",campos_startdatetime::timestamp,campos_startdestinationidno,campos_enddestinationidno
                    , count(campos_webtourusneed.id) as pax
                    , sum(case when campos_demandneeded then 0 else 1 end) as excessdemand 
                    , sum(case when campos_transfered then 0 else 1 end) as nottransfered
                    , sum(case when campos_deleted and not webtour_deleted then 1 else 0 end) as notdeleted
                    , sum(case when webtour_startdestinationidno = campos_startdestinationidno then 0 else 1 end) as startdestdiffer
                    , sum(case when webtour_enddestinationidno = campos_enddestinationidno then 0 else 1 end) as enddestdiffer
                    , sum(case when campos_startdatetime::timestamp = webtour_startdatetime::timestamp then 0 else 1 end) as startdatetimediffer
                    , sum(case when campos_enddatetime::timestamp = webtour_enddatetime::timestamp then 0 else 1 end) as enddatetimediffer
                    , sum(case when (case when campos_startnote isnull then '' else campos_startnote end) = (case when webtour_startnote isnull then '' else webtour_startnote end) then 0 else 1 end) as startnotediffer
                    , sum(case when (case when campos_endnote isnull then '' else campos_endnote end) = (case when webtour_endnote isnull then '' else webtour_endnote end) then 0 else 1 end) as endnotediffer
                    FROM campos_webtourusneed
                    left outer join event_registration on webtourusgroupidno = webtour_groupidno
                    where campos_demandneeded or (not webtour_deleted and webtour_needidno::INT4>0)
                    group by travelneed_id, travelgroup            
                    ,event_registration.id,webtour_groupidno, "campos_TripType_id",campos_startdatetime::timestamp
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