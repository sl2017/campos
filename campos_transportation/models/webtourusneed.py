# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ..interface import webtourinterface

import logging

_logger = logging.getLogger(__name__)

class WebtourUsNeed(models.Model):
    _name = 'campos.webtourusneed'
    participant_id = fields.Many2one('campos.event.participant','Participant ID', ondelete='set null')
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
    
    api.multi
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
                tag_data = None
                Ok = False

            return tag_data
        
        def get_tag_data_from_node(node,nodetag):
            try:
                tag_data = node.getElementsByTagName(nodetag)[0].firstChild.data
            except:
                tag_data = None

            return tag_data        
        
        if self.campos_startnote== False : 
            self.campos_startnote=""
            
        if self.campos_endnote== False : 
            self.campos_endnote=""
            
        if self.campos_enddatetime == False:
            self.campos_enddatetime = self.campos_startdatetime
        
        if  self.webtour_groupidno == False or self.webtour_useridno == False or self.campos_startdestinationidno == False or self.campos_startdatetime == False or self.campos_enddestinationidno == False or self.campos_enddatetime == False:
            return True
               
        if (self.webtour_needidno == False or self.webtour_needidno == "0"):
            if (self.campos_demandneeded == True):
                request="UserIDno="+self.webtour_useridno
                request=request+"&GroupIDno="+self.webtour_groupidno
                request=request+"&StartDestinationIDno="+self.campos_startdestinationidno
                request=request+"&StartDateTime="+self.campos_startdatetime
                request=request+"&StartNote="+self.campos_startnote
                request=request+"&EndDestinationIDno="+self.campos_enddestinationidno
                request=request+"&EndDateTime="+self.campos_enddatetime
                request=request+"&EndNote="+self.campos_endnote
                response_doc=webtourinterface.usneed_create(request)
        else :
            if self.campos_transferedseq <> self.campos_writeseq :
                request="NeedIDno="+self.webtour_needidno
                request=request+"&StartDestinationIDno="+self.campos_startdestinationidno
                request=request+"&StartDateTime="+self.campos_startdatetime
                request=request+"&StartNote="+self.campos_startnote
                request=request+"&EndDestinationIDno="+self.campos_enddestinationidno
                request=request+"&EndDateTime="+self.campos_enddatetime
                request=request+"&EndNote="+self.campos_endnote
                response_doc=webtourinterface.usneed_update(request)    
            else:
                response_doc=webtourinterface.usneed_getbyidno(self.webtour_needidno)        
        Ok = True     
        idno = get_tag_data("a:IDno")
              
        if idno <> "0" and Ok==True:
            self.webtour_needidno = idno
            self.webtour_startdatetime = get_tag_data("a:StartDateTime")
            self.webtour_startdestinationidno = get_tag_data("a:StartDestinationIDno")
            self.webtour_startnote = get_tag_data("a:StartNote")
            self.webtour_enddatetime = get_tag_data("a:EndDateTime")
            self.webtour_enddestinationidno = get_tag_data("a:EndDestinationIDno")
            self.webtour_endnote = get_tag_data("a:EndNote")
            self.webtour_touridno = get_tag_data("a:TourIDno")
            self.webtour_CurrentDateTime = get_tag_data("CurrentDateTime")
            self.campos_transferedseq = self.campos_writeseq
        else: 
            if get_tag_data("a:Description") == "Need already exist" :
                _logger.info("get_create_usneed_tron: Ohh Need already exist")
                response_doc=webtourinterface.usneed_GetByGroupIDno(self.webtour_groupidno)
                usNeeds=response_doc.getElementsByTagName('a:usNeed')
                for node in usNeeds:
                    try:
                        StartDestinationIDno = node.getElementsByTagName("a:StartDestinationIDno")[0].firstChild.data
                        EndDestinationIDno = node.getElementsByTagName("a:EndDestinationIDno")[0].firstChild.data
                        UserIDno = node.getElementsByTagName("a:UserIDno")[0].firstChild.data
                        if (self.campos_startdestinationidno == StartDestinationIDno and self.campos_enddestinationidno == EndDestinationIDno and self.webtour_useridno == UserIDno):
                            self.webtour_needidno = node.getElementsByTagName("a:IDno")[0].firstChild.data
                            self.webtour_startdatetime = node.getElementsByTagName("a:StartDateTime")[0].firstChild.data
                            self.webtour_startdestinationidno = StartDestinationIDno
                            self.webtour_startnote = get_tag_data_from_node(node,"a:StartNote")
                            self.webtour_enddatetime = node.getElementsByTagName("a:EndDateTime")[0].firstChild.data
                            self.webtour_enddestinationidno = EndDestinationIDno
                            self.webtour_endnote = get_tag_data_from_node(node,"a:EndNote")
                            self.webtour_touridno = node.getElementsByTagName("a:TourIDno")[0].firstChild.data
                            self.webtour_CurrentDateTime = get_tag_data("CurrentDateTime")
                            self.campos_transferedseq = self.campos_writeseq
                            _logger.info("get_create_usneed_tron: Found a usNeed matching %s", node.toprettyxml(indent="   "))
                            break
                    except:
                        Ok = False                    
            else:
                self.campos_transferedseq = ""
            
        return True

    @api.model
    def get_create_usneed_tron(self):
        
        # find usneeds not beeing transfered
        rs_needs= self.env['campos.webtourusneed'].search([('campos_transfered', '=', False),('campos_demandneeded', '=', True)])

        _logger.info("get_create_usneed_tron: Here we go... %i usNeeds to update in Webtour", len(rs_needs))
        
        for need in rs_needs:
            need.get_create_webtour_need()

    
    @api.multi
    def updatewebtourtofromusneeds(self):
        # needs = self.env['campos.webtourusneed'].search([('participant_id','<>',False)])
        
        _logger.info("updatewebtourtofromusneeds: Here we go...%s",len(self))
        for need in self: # (change to needs to update all needs)
            if need.participant_id <> False:
                webtourconfig= self.env['campos.webtourconfig'].search([('event_id', '=', self.participant_id.registration_id.event_id.id)])
                
                if need.campos_TripType_id==webtourconfig.tocamp_campos_TripType_id:
                    need.campos_demandneeded = need.participant_id.usecamptransporttocamp
                    need.campos_startdatetime = need.participant_id.tocampdate
                    need.campos_enddatetime = need.participant_id.tocampdate
                    need.participant_id.tocampfromdestination_id = need.participant_id.registration_id.webtourdefaulthomedestination
                    need.campos_startdestinationidno = need.participant_id.tocampfromdestination_id.destinationidno                    
                    need.webtour_useridno = need.participant_id.webtourususeridno
                    need.webtour_groupidno = need.participant_id.webtourusgroupidno
                    need.campos_writeseq = self.env['ir.sequence'].get('webtour.transaction')  
                
                if need.campos_TripType_id==webtourconfig.fromcamp_campos_TripType_id :
                    need.campos_demandneeded = need.participant_id.usecamptransportfromcamp
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
    