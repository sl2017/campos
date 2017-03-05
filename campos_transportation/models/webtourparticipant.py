# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ..interface import webtourinterface

import logging
import datetime

_logger = logging.getLogger(__name__)

class WebtourParticipant(models.Model):
    _inherit = 'campos.event.participant'
    
    webtourususeridno = fields.Char('webtour us User ID no', required=False)
    webtourusgroupidno = fields.Char(string='webtour us Group ID no', related='registration_id.webtourusgroupidno')                                 
    
    tocampfromdestination_id = fields.Many2one('campos.webtourusdestination',
                                            'To camp Pick up',
                                            ondelete='set null',compute='_compute_tocampfromdestination_id')
    fromcamptodestination_id = fields.Many2one('campos.webtourusdestination',
                                            'From camp Drop off',
                                            ondelete='set null',compute='_compute_fromcamptomdestination_id')
    
    tocampdate = fields.Date(compute='_compute_tocampdate', string='To Camp Date', store = True)
    fromcampdate = fields.Date(compute='_compute_fromcampdate', string='From Camp Date', store = True)
    
    tocampusneed_id = fields.Many2one('campos.webtourusneed','To Camp Need ID',ondelete='set null')
    fromcampusneed_id = fields.Many2one('campos.webtourusneed','From Camp Need ID',ondelete='set null')
    
    specialtocampdatetime = fields.Datetime('Special To Camp Date', required=False)
    specialfromcampdatetime = fields.Datetime('Special From Camp Date', required=False)

    individualtocampfromdestination_id = fields.Many2one('campos.webtourusdestination',
                                            'Individual To camp Pick up',
                                            ondelete='set null')
    individualfromcamptodestination_id = fields.Many2one('campos.webtourusdestination',
                                            'Individual From camp Drop off',
                                            ondelete='set null')

    @api.multi
    @api.depends('individualtocampfromdestination_id','registration_id.webtourdefaulthomedestination','registration_id.webtourgrouptocampdestination_id')
    def _compute_tocampfromdestination_id(self):
        for par in self:
            if par.individualtocampfromdestination_id:
                par.tocampfromdestination_id = par.individualtocampfromdestination_id
            elif par.registration_id.webtourgrouptocampdestination_id:
                par.tocampfromdestination_id = par.registration_id.webtourgrouptocampdestination_id
            elif par.registration_id.webtourdefaulthomedestination:
                par.tocampfromdestination_id = par.registration_id.webtourdefaulthomedestination
            else:
                par.tocampfromdestination_id = False
                
    @api.multi
    @api.depends('individualfromcamptodestination_id','registration_id.webtourdefaulthomedestination','registration_id.webtourgroupfromcampdestination_id')
    def _compute_fromcamptomdestination_id(self):
        for par in self:
            if par.individualfromcamptodestination_id:
                par.fromcamptodestination_id = par.individualfromcamptodestination_id
            elif par.registration_id.webtourgroupfromcampdestination_id:
                par.fromcamptodestination_id = par.registration_id.webtourgroupfromcampdestination_id
            elif par.registration_id.webtourdefaulthomedestination:
                par.fromcamptodestination_id = par.registration_id.webtourdefaulthomedestination
            else:
                par.fromcamptodestination_id = False
                
    @api.multi
    @api.depends('dates_summery','specialtocampdatetime')
    def _compute_tocampdate(self):

        for par in self:
            if par.specialtocampdatetime:
                par.tocampdate = par.specialtocampdatetime
            else:
                dates = []
                for d in par.camp_day_ids:
                    if d.will_participate:
                        dates.append(d.the_date)
        
                dates.sort()
                if len(dates) > 0:
                    par.tocampdate = dates[0]
                else :
                    par.tocampdate = False

    @api.multi
    @api.depends('dates_summery','specialfromcampdatetime')
    def _compute_fromcampdate(self):

        for par in self:
            if par.specialfromcampdatetime:
                par.fromcampdate = par.specialfromcampdatetime
            else:
                dates = []
                for d in par.camp_day_ids:
                    if d.will_participate:
                        dates.append(d.the_date)
        
                dates.sort(reverse=True)
                if len(dates) > 0:
                    par.fromcampdate = dates[0]
                else :
                    par.fromcampdate = False

  
    @api.model
    def get_create_usgroupidno_tron(self):
        
        _logger.info("get_create_usgroupidno_tron: Here we go...")

        # find participants having transort need but missing usGroupIDno
        rs_missingusGroupIDno= self.env['campos.event.participant'].search([('registration_id.event_id', '=', 1),('webtourusgroupidno', '=', False)
                                                                            ,'|',('transport_to_camp', '=', True),('transport_from_camp', '=', True)])
        # make at list of distinct Registrationid missing
        missingRegistrationidlist=[]
        for r in rs_missingusGroupIDno:
            if r.registration_id.id in missingRegistrationidlist: 
                continue 
            else:
                missingRegistrationidlist.append(r.registration_id.id)                                                                       

        #_logger.info("get_create_usgroupidno_tron: %s usGroupIDno's missing ",missingRegistrationidlist)
             
        #Get all usGroupIDno's from webtour and conver to a simple list
        response_doc=webtourinterface.usgroup_getall()
        usgroups = response_doc.getElementsByTagName("a:IDno")
        usgrouplist=[]

        for g in usgroups:
            usgrouplist.append(str(g.firstChild.data))

        # find all registrations missing usgroupidno or is missing in webtour
        rs_missingusgroupidno= self.env['event.registration'].search(['|',('id','in',missingRegistrationidlist)
                                                                      ,'&',('webtourusgroupidno', '!=', False),('webtourusgroupidno','not in',usgrouplist)])
        
        _logger.info("get_create_usgroupidno_tron: %d (%d) usGroupIDno's missing. Got %d usGroupIDno's from Webtour",len(missingRegistrationidlist),len(rs_missingusgroupidno),len(usgrouplist))    
        
        # for each registation check usgroupidno name and create if missing
        for rec in rs_missingusgroupidno:
            newidno=webtourinterface.usgroup_getbyname(str(rec.id))
            if newidno == "0":
                newidno=webtourinterface.usgroup_create(str(rec.id))
                if newidno != "0": #remember also this usgroupidno
                    usgrouplist.append
                
            _logger.info("get_create_usgroupidno_tron Group: %s %s %s %s",str(rec.id), rec.name, rec.webtourusgroupidno, newidno)
            
            if newidno <> "0": #Update registration
                dicto = {}
                dicto["webtourusgroupidno"] = newidno
                rec.write(dicto) 

        # find participants missing usUserIDno, from Registration having a usGroupIDno
        rs_missingususeridno= self.env['campos.event.participant'].search([('webtourususeridno', '=', False),('webtourusgroupidno', 'in', usgrouplist)
                                                                          ,'|',('transport_to_camp', '=', True),('transport_from_camp', '=', True)])
        
        # for each participant check ususeridno name and create if missing
        for rec in rs_missingususeridno:
            newidno=webtourinterface.ususer_getbyexternalid(str(rec.id))
            if newidno == "0":
                newidno=webtourinterface.ususer_create(str(rec.id), rec.webtourusgroupidno,str(rec.id),str(rec.registration_id))
            
            _logger.info("get_create_usgroupidno_tron User: %s %s %s %s %s",str(rec.id), rec.name, rec.webtourusgroupidno, rec.webtourususeridno,newidno)
            
            if newidno <> "0": #Update participant
                dicto = {}
                dicto["webtourususeridno"] = newidno
                rec.write(dicto)
              
        self.env['campos.webtourusneed'].get_create_usneed_tron()        

        return True
    
    @api.multi
    def write(self, vals):
        _logger.info("Transportation Participant Write Entered %s", vals.keys())
        ret = super(WebtourParticipant, self).write(vals)
        webtourconfig= self.env['campos.webtourconfig'].search([('event_id', '=', self.registration_id.event_id.id)])
        campdesination= webtourconfig.campdestinationid.destinationidno
               
        for par in self:
     
            if  ('tocampfromdestination_id' in vals 
                or 'tocampdate' in vals
                or 'transport_to_camp' in vals 
                or 'webtourususeridno' in vals
                ):
                if par.tocampusneed_id.id == False:
                    dicto1 = {}
                    dicto1["participant_id"] = par.id
                    dicto1["campos_demandneeded"] = par.transport_to_camp
                    dicto1["campos_TripType_id"] = webtourconfig.tocamp_campos_TripType_id.id
                    dicto1["campos_startdatetime"] = par.tocampdate
                    dicto1["campos_enddatetime"] = par.tocampdate
                    dicto1["campos_startdestinationidno"] = par.tocampfromdestination_id.destinationidno
                    dicto1["campos_enddestinationidno"] = campdesination
                    dicto1["webtour_useridno"] = par.webtourususeridno
                    dicto1["webtour_groupidno"] = par.webtourusgroupidno
                    dicto1["campos_writeseq"] = self.env['ir.sequence'].get('webtour.transaction')
                
                    usneed_obj = self.env['campos.webtourusneed']                
                    par.tocampusneed_id = usneed_obj.create(dicto1)
                else:
                    par.tocampusneed_id.campos_demandneeded = par.transport_to_camp
                    par.tocampusneed_id.campos_startdatetime = par.tocampdate
                    par.tocampusneed_id.campos_enddatetime = par.tocampdate
                    par.tocampusneed_id.campos_startdestinationidno = par.tocampfromdestination_id.destinationidno
                    par.tocampusneed_id.campos_enddestinationidno = campdesination
                    par.tocampusneed_id.webtour_useridno = par.webtourususeridno
                    par.tocampusneed_id.webtour_groupidno = par.webtourusgroupidno
                    par.tocampusneed_id.campos_writeseq = self.env['ir.sequence'].get('webtour.transaction')  
                                       
                _logger.info("Transportation Participant Write Change in To camp transportation for %s %s",par.webtourususeridno),par.tocampusneed_id.id
                
            if  ('fromcamptodestination_id' in vals 
                or 'fromcampdate' in vals
                or 'transport_from_camp' in vals 
                or 'webtourususeridno' in vals
                ):
                if par.fromcampusneed_id.id == False:
                    dicto1 = {}
                    dicto1["participant_id"] = par.id
                    dicto1["campos_demandneeded"] = par.transport_from_camp      
                    dicto1["campos_TripType_id"] = webtourconfig.fromcamp_campos_TripType_id.id                                  
                    dicto1["campos_startdatetime"] = par.fromcampdate
                    dicto1["campos_enddatetime"] = par.fromcampdate                    
                    dicto1["campos_startdestinationidno"] = campdesination
                    dicto1["campos_enddestinationidno"] = par.fromcamptodestination_id.destinationidno
                    dicto1["webtour_useridno"] = par.webtourususeridno
                    dicto1["webtour_groupidno"] = par.webtourusgroupidno
                    dicto1["campos_writeseq"] = self.env['ir.sequence'].get('webtour.transaction')
                                                        
                    usneed_obj = self.env['campos.webtourusneed']                
                    par.fromcampusneed_id = usneed_obj.create(dicto1)
                else:
                    par.fromcampusneed_id.campos_demandneeded = par.transport_from_camp
                    par.fromcampusneed_id.campos_startdatetime = par.fromcampdate
                    par.fromcampusneed_id.campos_enddatetime = par.fromcampdate
                    par.fromcampusneed_id.campos_startdestinationidno = campdesination
                    par.fromcampusneed_id.campos_enddestinationidno = par.fromcamptodestination_id.destinationidno
                    par.fromcampusneed_id.webtour_useridno = par.webtourususeridno
                    par.fromcampusneed_id.webtour_groupidno = par.webtourusgroupidno     
                    par.fromcampusneed_id.campos_writeseq = self.env['ir.sequence'].get('webtour.transaction')
                                                           
                _logger.info("Transportation Participant Write Change in To camp transportation for %s %s",par.webtourususeridno),par.tocampusneed_id.id                            
        return ret
    
    @api.multi
    def clearusecamptransport(self):
        # find participants missing usUserIDno, from Registration having a usGroupIDno
        #rs = self.env['campos.event.participant'].search([('transport_from_camp', '=', True)])
        #for rec in rs:
        #    rec.transport_from_camp = False   
        
        return True
    
class WebtourParticipantCampDay(models.Model):
    '''
    One persons participation to a camp in one day Webtour  datetime.strptime(tmp,'%Y-%m-%d %H:%M:%S')
    '''
    _inherit = 'campos.event.participant.day'
    webtourcamptransportation = fields.Char('Camp transportation',compute='_compute_webtourcamptransportation')

    @api.one
    def _compute_webtourcamptransportation(self):
        if self.the_date == self.participant_id.tocampdate:
            if self.participant_id.transport_to_camp:
                self.webtourcamptransportation = 'To Camp from: ' + self.participant_id.tocampfromdestination_id.placename
            else:
                self.webtourcamptransportation = ''
        elif self.the_date == self.participant_id.fromcampdate:
            if self.participant_id.transport_from_camp:
                self.webtourcamptransportation = 'From Camp to: ' + self.participant_id.fromcamptodestination_id.placename
            else:
                self.webtourcamptransportation = ''
        else:
            self.webtourcamptransportation = ''
        