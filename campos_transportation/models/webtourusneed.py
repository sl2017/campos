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
    campos_startdatetime = fields.Char('CampOs StartDateTime', required=False)
    campos_startdestinationidno = fields.Char('CampOs StartDestinationIdNo', required=False)
    campos_startnote = fields.Char('CampOs StartNote', required=False)
    campos_enddatetime = fields.Char('CampOs EndDateTime', required=False)
    campos_enddestinationidno = fields.Char('CampOs EndDestinationIdNo', required=False)
    campos_endnote = fields.Char('CampOs EndNote', required=False)
    campos_writeseq = fields.Char('CampOs Last Write Seq.', required=False)
    campos_transferedseq = fields.Char('CampOs Last transfered Seq.', required=False)
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
    
    @api.one
    def get_create_webtour_need(self):
        
        def get_tag_data(nodetag):
            try:
                tag_data = response_doc.getElementsByTagName(nodetag)[0].firstChild.data
            except:
                tag_data = None
                Ok = False

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
            self.webtour_CurrentDateTime = get_tag_data("CurrentDateTime") 
            self.campos_transferedseq = self.campos_writeseq
        else :
            self.campos_transferedseq = ""
            
        return True
    
    @api.multi
    def updatewebtourtofromusneeds(self):
        needs = campdestination= self.env['campos.webtourusneed'].search([('participant_id','<>',False)])
        
        _logger.info("updatewebtourtofromusneeds: Here we go...%s",needs)
        for need in needs:
            campdestination= self.env['campos.webtourconfig'].search([('event_id', '=', self.participant_id.registration_id.event_id.id)]).campdestinationid.destinationidno

            if need.participant_id <> False:
                if need.campos_enddestinationidno == campdestination :
                    need.campos_demandneeded = need.participant_id.usecamptransporttocamp
                    need.campos_startdatetime = need.participant_id.tocampdate
                    need.campos_enddatetime = need.participant_id.tocampdate
                    need.campos_startdestinationidno = need.participant_id.tocampfromdestination_id.destinationidno
                    need.webtour_useridno = need.participant_id.webtourususeridno
                    need.webtour_groupidno = need.participant_id.webtourusgroupidno
                    need.campos_writeseq = self.env['ir.sequence'].get('webtour.transaction')  
                
                if need.campos_startdestinationidno == campdestination :
                    need.campos_demandneeded = need.participant_id.usecamptransportfromcamp
                    need.campos_startdatetime = need.participant_id.fromcampdate
                    need.campos_enddatetime = need.participant_id.fromcampdate
                    need.campos_enddestinationidno = need.participant_id.fromcamptodestination_id.destinationidno
                    need.webtour_useridno = need.participant_id.webtourususeridno
                    need.webtour_groupidno = need.participant_id.webtourusgroupidno                     
                    need.campos_writeseq = self.env['ir.sequence'].get('webtour.transaction')
                    
                need.get_create_webtour_need()
                
        return True