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
    
    recalcneed = fields.Boolean('recalcneed')
    tocamptravelgroup = fields.Selection([    ('1', 'Group 1'),
                                              ('2', 'Group 2'),
                                              ('3', 'Group 3'),
                                              ('4', 'Group 4'),
                                              ('5', 'Group 5')], default='1', string='Travel Group to Camp')
    
    fromcamptravelgroup = fields.Selection([  ('1', 'Group 1'),
                                              ('2', 'Group 2'),
                                              ('3', 'Group 3'),
                                              ('4', 'Group 4'),
                                              ('5', 'Group 5')], default='1', string='Travel Group from Camp')      
      
    @api.multi
    @api.depends('individualtocampfromdestination_id','recalcneed','registration_id.webtourdefaulthomedestination','registration_id.webtourgrouptocampdestination_id')
    def _compute_tocampfromdestination_id(self):
        for par in self:
            #_logger.info("_compute_tocampfromdestination_id %s %s %s %s %s", len(self), par.id, par.individualtocampfromdestination_id.destinationidno,par.registration_id.webtourgrouptocampdestination_id,par.registration_id.webtourdefaulthomedestination)
            if par.individualtocampfromdestination_id:
                par.tocampfromdestination_id = par.individualtocampfromdestination_id
            elif par.registration_id.webtourgrouptocampdestination_id:
                par.tocampfromdestination_id = par.registration_id.webtourgrouptocampdestination_id
            elif par.registration_id.webtourdefaulthomedestination:
                par.tocampfromdestination_id = par.registration_id.webtourdefaulthomedestination
            else:
                par.tocampfromdestination_id = False
            #par.update_tocampusneed()
                          
    @api.multi
    @api.depends('individualfromcamptodestination_id','recalcneed','registration_id.webtourdefaulthomedestination','registration_id.webtourgroupfromcampdestination_id')
    def _compute_fromcamptomdestination_id(self):
        for par in self:
            #_logger.info("_compute_fromcamptomdestination_id %s %s %s %s %s", len(self), par.id, par.individualtocampfromdestination_id.destinationidno,par.registration_id.webtourgrouptocampdestination_id,par.registration_id.webtourdefaulthomedestination)
            if par.individualfromcamptodestination_id:
                par.fromcamptodestination_id = par.individualfromcamptodestination_id
            elif par.registration_id.webtourgroupfromcampdestination_id:
                par.fromcamptodestination_id = par.registration_id.webtourgroupfromcampdestination_id
            elif par.registration_id.webtourdefaulthomedestination:
                par.fromcamptodestination_id = par.registration_id.webtourdefaulthomedestination
            else:
                par.fromcamptodestination_id = False
            #par.update_fromcampusneed()   
                         
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
            #xxxpar.update_tocampusneed()
            _logger.info("xxxxxxxxxxxxxxxxxxxxxxxx _compute_tocampdate, % % %",par.specialtocampdatetime,dates,par.tocampdate)
            
    @api.multi
    @api.depends('dates_summery','specialfromcampdatetime')
    def _compute_fromcampdate(self):

        for par in self:
            #_logger.info("xxxxxxxxxxxxxxxxxxxxxxxx _compute_fromcampdate")            
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
            #xxxpar.update_fromcampusneed()
            _logger.info("xxxxxxxxxxxxxxxxxxxxxxxx _compute_fromcampdate, % % %",par.specialfromcampdatetime,dates,par.fromcampdate)
              
    @api.model
    def get_create_usgroupidno_tron(self):
        MAX_LOOPS_usGroup = 100  #Max No of Groups pr Scheduled call
        MAX_LOOPS_usUser = 1000  #Max No of Users pr Scheduled call
        _logger.info("get_create_usgroupidno_tron: Here we go...")

        # find participants having transort need but missing usGroupIDno
        rs_missingusGroupIDno= self.env['campos.event.participant'].search([('registration_id.event_id', '=', 1),('webtourusgroupidno', '=', False),('registration_id.scoutgroup', '=', True)
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
        response_doc=webtourinterface.usgroup_getall(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'))
        usgroups = response_doc.getElementsByTagName("a:IDno")
        usgrouplist=[]

        for g in usgroups:
            usgrouplist.append(str(g.firstChild.data))

        # find all registrations missing usgroupidno or is missing in webtour
        rs_missingusgroupidno= self.env['event.registration'].search(['|',('id','in',missingRegistrationidlist)
                                                                      ,'&',('webtourusgroupidno', '!=', False),('webtourusgroupidno','not in',usgrouplist)])
        
        _logger.info("get_create_usgroupidno_tron: %d (%d) usGroupIDno's missing. Got %d usGroupIDno's from Webtour",len(missingRegistrationidlist),len(rs_missingusgroupidno),len(usgrouplist))    
        
        # for each registation check usgroupidno name and create if missing
        g = 0
        for rec in rs_missingusgroupidno:
            newidno=webtourinterface.usgroup_getbyname(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),str(rec.id))
            if newidno == "0":
                # xx newidno=webtourinterface.usgroup_create(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),str(rec.id))
                if newidno != "0": #remember also this usgroupidno
                    usgrouplist.append
                
            _logger.info("get_create_usgroupidno_tron Group: %s %s %s %s",str(rec.id), rec.name, rec.webtourusgroupidno, newidno)
            
            if newidno <> "0": #Update registration
                dicto = {}
                dicto["webtourusgroupidno"] = newidno
                rec.write(dicto)
                 
            rec.env.cr.commit()                 
            
            g = g +1
            if g > MAX_LOOPS_usGroup:
                break

               
        # find participants missing usUserIDno, from Registration having a usGroupIDno
        rs_missingususeridno= self.env['campos.event.participant'].search([('webtourususeridno', '=', False),('webtourusgroupidno', 'in', usgrouplist)
                                                                          ,'|',('transport_to_camp', '=', True),('transport_from_camp', '=', True)])
        
        # for each participant check ususeridno name and create if missing
        g=0
        for rec in rs_missingususeridno:
            newidno=webtourinterface.ususer_getbyexternalid(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),str(rec.id))
            if newidno == "0":
                newidno=webtourinterface.ususer_create(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),str(rec.id), rec.webtourusgroupidno,str(rec.id),str(rec.registration_id))
            
            _logger.info("get_create_usgroupidno_tron User: %s %s %s %s %s",str(rec.id), rec.name, rec.webtourusgroupidno, rec.webtourususeridno,newidno)
            
            if newidno <> "0": #Update participant
                dicto = {}
                dicto["webtourususeridno"] = newidno
                rec.write(dicto)
                
            rec.env.cr.commit()               
            
            g = g +1
            if g > MAX_LOOPS_usUser:
                break
            
        self.env['campos.webtourusneed'].get_create_usneed_tron()        

        return True
    
    @api.multi
    def write(self, vals):
        _logger.info("Write Entered %s", vals.keys())
        ret = super(WebtourParticipant, self).write(vals)
                      
        for par in self:
            if  ('recalcneed' in vals):
                _logger.info("Write xxxxxxxxxxxx recalcneed change %s", par.id)
                par._compute_tocampfromdestination_id()
                par._compute_fromcamptomdestination_id()
            
            if  ('camp_day_ids' in vals):    
                par._compute_tocampdate()
                par._compute_fromcampdate()
                
            if  ('tocampfromdestination_id' in vals 
                or 'individualtocampfromdestination_id' in vals 
                or 'tocamptravelgroup' in vals
                or 'camp_day_ids' in vals
                or 'tocampdate' in vals
                or 'transport_to_camp' in vals 
                or 'webtourususeridno' in vals
                ):
                
                par.update_tocampusneed()        
                               
            if  ('fromcamptodestination_id' in vals 
                or 'individualfromcamptodestination_id' in vals
                or 'fromcamptravelgroup' in vals                
                or 'camp_day_ids' in vals                 
                or 'fromcampdate' in vals
                or 'transport_from_camp' in vals 
                or 'webtourususeridno' in vals
                ):
                par.update_fromcampusneed()   
                        
        return ret

    @api.one
    def update_tocampusneed(self):
      
        webtourconfig= self.env['campos.webtourconfig'].search([('event_id', '=', self.registration_id.event_id.id)])
        campdesination= webtourconfig.campdestinationid.destinationidno

        
        if self.tocampusneed_id.id == False:
            dicto1 = {}
            dicto1["participant_id"] = self.id
            dicto1["travelgroup"] = self.tocamptravelgroup
            dicto1["campos_demandneeded"] = self.transport_to_camp
            dicto1["campos_TripType_id"] = webtourconfig.tocamp_campos_TripType_id.id
            dicto1["campos_startdatetime"] = self.tocampdate
            dicto1["campos_enddatetime"] = self.tocampdate
            dicto1["campos_startdestinationidno"] = self.tocampfromdestination_id.destinationidno
            dicto1["campos_enddestinationidno"] = campdesination
            dicto1["webtour_useridno"] = self.webtourususeridno
            dicto1["webtour_groupidno"] = self.webtourusgroupidno
            dicto1["campos_writeseq"] = self.env['ir.sequence'].get('webtour.transaction')
        
            usneed_obj = self.env['campos.webtourusneed']                
            self.tocampusneed_id = usneed_obj.create(dicto1)
        else:
            dicto1 = {}   
            dicto1["travelgroup"] = self.tocamptravelgroup                             
            dicto1["campos_demandneeded"]  = self.transport_to_camp
            dicto1["campos_startdatetime"]  = self.tocampdate
            dicto1["campos_enddatetime"]  = self.tocampdate
            dicto1["campos_startdestinationidno"]  = self.tocampfromdestination_id.destinationidno
            dicto1["campos_enddestinationidno"]  = campdesination
            dicto1["webtour_useridno"]  = self.webtourususeridno
            dicto1["webtour_groupidno"]  = self.webtourusgroupidno
            dicto1["campos_writeseq"]  = self.env['ir.sequence'].get('webtour.transaction')  
            self.tocampusneed_id.write(dicto1)
            
        _logger.info("Update_tocampusneed %s", dicto1)
        
    @api.one
    def update_fromcampusneed(self):
      
        webtourconfig= self.env['campos.webtourconfig'].search([('event_id', '=', self.registration_id.event_id.id)])
        campdesination= webtourconfig.campdestinationid.destinationidno           
            
        if self.fromcampusneed_id.id == False:
            dicto1 = {}
            dicto1["participant_id"] = self.id
            dicto1["travelgroup"] = self.fromcamptravelgroup            
            dicto1["campos_demandneeded"] = self.transport_from_camp      
            dicto1["campos_TripType_id"] = webtourconfig.fromcamp_campos_TripType_id.id                                  
            dicto1["campos_startdatetime"] = self.fromcampdate
            dicto1["campos_enddatetime"] = self.fromcampdate                    
            dicto1["campos_startdestinationidno"] = campdesination
            dicto1["campos_enddestinationidno"] = self.fromcamptodestination_id.destinationidno
            dicto1["webtour_useridno"] = self.webtourususeridno
            dicto1["webtour_groupidno"] = self.webtourusgroupidno
            dicto1["campos_writeseq"] = self.env['ir.sequence'].get('webtour.transaction')
                                                
            usneed_obj = self.env['campos.webtourusneed']                
            self.fromcampusneed_id = usneed_obj.create(dicto1)
        else:
            dicto1 = {} 
            dicto1["travelgroup"] = self.fromcamptravelgroup               
            dicto1["campos_demandneeded"]  = self.transport_from_camp
            dicto1["campos_startdatetime"]  = self.fromcampdate
            dicto1["campos_enddatetime"]  = self.fromcampdate
            dicto1["campos_startdestinationidno"]  = campdesination
            dicto1["campos_enddestinationidno"]  = self.fromcamptodestination_id.destinationidno
            dicto1["webtour_useridno"]  = self.webtourususeridno
            dicto1["webtour_groupidno"]  = self.webtourusgroupidno     
            dicto1["campos_writeseq"]  = self.env['ir.sequence'].get('webtour.transaction')
            self.fromcampusneed_id.write(dicto1)
                       
        _logger.info("update_fromcampusneed %s", dicto1)
         
                 
    @api.multi
    def clearusecamptransport(self):
        # find participants missing usUserIDno, from Registration having a usGroupIDno
        #rs = self.env['campos.event.participant'].search([('transport_from_camp', '=', True)])
        #for rec in rs:
        #    rec.transport_from_camp = False   
        
        return True
    
class WebtourParticipantCampDay(models.Model):
    '''
    One persons participation to a camp in one day Webtour
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
        