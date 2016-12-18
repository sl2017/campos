# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ..interface import webtourinterface

class WebtourUsNeed(models.Model):
    _name = 'campos.webtourusneed'
    participant_id = fields.Many2one('campos.event.participant','Participant ID', ondelete='set null')
    campos_deleted = fields.Boolean('CampOs Deleted', default=False)
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
               
        if self.webtour_needidno == False or self.webtour_needidno == "0" :
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
