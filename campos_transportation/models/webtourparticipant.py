# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ..interface import webtourinterface

import logging
#import datetime

_logger = logging.getLogger(__name__)

class WebtourParticipant(models.Model):
    _inherit = 'campos.event.participant'
    
    webtourususeridno = fields.Char('webtour us User ID no', required=False)
    webtourusgroupidno = fields.Char(string='webtour us Group ID no', related='registration_id.webtourusgroupidno')                                 
    
    tocampfromdestination_id = fields.Many2one('campos.webtourusdestination',
                                            'To camp Pick up',
                                            ondelete='set null') #, store=Truecompute='_compute_tocampfromdestination_id',
  
    fromcamptodestination_id = fields.Many2one('campos.webtourusdestination',
                                            'From camp Drop off',
                                            ondelete='set null')#,compute='_compute_fromcamptomdestination_id', store=True
    
    tocampdate = fields.Date(string='To Camp Date') #compute='_compute_tocampdate', , store = True
    fromcampdate = fields.Date(string='From Camp Date') #compute='_compute_fromcampdate', , store = True
    
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
    
    recalctoneed = fields.Boolean('recalctoneed')
    recalcfromneed = fields.Boolean('recalcfromneed')
    
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
    
    groupisdanish = fields.Boolean(related='registration_id.groupisdanish')

    @api.one
    def _compute_tocampfromdestination_id(self):
            #_logger.info("_compute_tocampfromdestination_id %s %s %s %s %s %s %s", len(self), par.id, par.tocampfromdestination_id, par.individualtocampfromdestination_id,par.registration_id.webtourgrouptocampdestination_id,par.registration_id.group_entrypoint.defaultdestination_id,par.registration_id.webtourdefaulthomedestination)
            destination=False
            if self.individualtocampfromdestination_id:
                destination = self.individualtocampfromdestination_id
            elif self.registration_id.webtourgrouptocampdestination_id:
                destination = self.registration_id.webtourgrouptocampdestination_id
            elif self.registration_id.group_entrypoint.defaultdestination_id:
                destination = self.registration_id.group_entrypoint.defaultdestination_id
            elif self.registration_id.webtourdefaulthomedestination:
                destination = self.registration_id.webtourdefaulthomedestination
            
            if  destination == False:
                _logger.info("_compute_tocampfromdestination_id No Destination known !!!!!!! %s", self.id)
                self.tocampfromdestination_id = False;
            else:
                if self.tocampfromdestination_id != destination:
                    _logger.info("_compute_tocampfromdestination_id Update %s %s %s",self.id,self.tocampfromdestination_id,destination)
                    self.tocampfromdestination_id = destination
                    return True
            
            return False 
                                                  
    @api.one
    def _compute_fromcamptomdestination_id(self):
        #_logger.info("_compute_fromcamptomdestination_id %s %s %s %s %s %s %s", len(self), par.id, par.fromcamptodestination_id, par.individualfromcamptodestination_id,par.registration_id.webtourgroupfromcampdestination_id,par.registration_id.group_exitpoint.defaultdestination_id,par.registration_id.webtourdefaulthomedestination)
        destination=self.fromcamptodestination_id
        if self.individualfromcamptodestination_id:
            destination = self.individualfromcamptodestination_id
        elif self.registration_id.webtourgroupfromcampdestination_id:
            destination = self.registration_id.webtourgroupfromcampdestination_id
        elif self.registration_id.group_exitpoint.defaultdestination_id:
            destination = self.registration_id.group_exitpoint.defaultdestination_id
        elif self.registration_id.webtourdefaulthomedestination:
            destination = self.registration_id.webtourdefaulthomedestination

        if  destination == False:
            _logger.info("individualfromcamptodestination_id No Destination known !!!!!!! %s",self.id)
            self.fromcamptodestination_id = False;
        else:
            if self.fromcamptodestination_id != destination:
                _logger.info("individualfromcamptodestination_id Update %s %s %s",self.id, self.fromcamptodestination_id.id,destination.id)
                self.fromcamptodestination_id = destination
                return True
        
        return False                
                         
    @api.one
    def _compute_tocampdate(self):        
        tocampdate = False
        if self.specialtocampdatetime:
            tocampdate = self.specialtocampdatetime
        else:
            dates = []
            for d in self.camp_day_ids:
                if d.will_participate:
                    dates.append(d.the_date)
    
            dates.sort()
            if len(dates) > 0:
                tocampdate = dates[0]
            else :
                tocampdate = False
                
        if self.tocampdate != tocampdate:
            _logger.info("_compute_tocampdate, Update %s %s %s %s %s",self.id, self.specialtocampdatetime,dates,self.tocampdate,tocampdate)
            self.tocampdate = tocampdate      
            return True
        
        return False                
            
    @api.one
    def _compute_fromcampdate(self):
        fromcampdate = False           
        if self.specialfromcampdatetime:
            fromcampdate = self.specialfromcampdatetime
        else:
            dates = []
            for d in self.camp_day_ids:
                if d.will_participate:
                    dates.append(d.the_date)
    
            dates.sort(reverse=True)
            if len(dates) > 0:
                fromcampdate = dates[0]
            else :
                fromcampdate = False
        if self.fromcampdate != fromcampdate:
            _logger.info("_compute_fromcampdate, Update %s %s %s %s %s",self.id,self.specialfromcampdatetime,dates,self.fromcampdate,fromcampdate)
            self.fromcampdate = fromcampdate
            return True
        
        return False
              
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
            notdoneto = True
            notdonefrom = True
            if  'recalctoneed' in vals or 'individualtocampfromdestination_id' in vals:           
                if [True] == par._compute_tocampfromdestination_id():
                    notdoneto = False
                   
            if  'recalcfromneed' in vals or 'individualfromcamptodestination_id' in vals:
                if [True] == par._compute_fromcamptomdestination_id():
                    notdonefrom = False
            
            if  ('camp_day_ids' in vals):    
                if [True] == par._compute_tocampdate():
                    notdoneto = False
                if [True] == par._compute_fromcampdate():
                    notdonefrom = False                
                
            if  ('tocampfromdestination_id' in vals 
                or 'tocamptravelgroup' in vals
                or 'tocampdate' in vals
                or 'transport_to_camp' in vals
                or ('recalctoneed' in vals and notdoneto)
                ):
                par.update_tocampusneed()


            if  ('fromcamptodestination_id' in vals 
                or 'fromcamptravelgroup' in vals                                
                or 'fromcampdate' in vals
                or 'transport_from_camp' in vals
                or ('recalcfromneed' in vals and notdonefrom)
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
            dicto1["campos_traveldate"]  = self.tocampdate
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
            dicto1["campos_traveldate"]  = self.tocampdate
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
            dicto1["campos_traveldate"] = self.fromcampdate                  
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
            dicto1["campos_traveldate"] = self.fromcampdate 
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
        #_logger.info("_compute_webtourcamptransportation %s %s %s", self, self.participant_id,self.participant_id.tocampfromdestination_id)
        if self.the_date == self.participant_id.tocampdate:
            if self.participant_id.transport_to_camp and self.participant_id.tocampfromdestination_id.placename:
                self.webtourcamptransportation = 'To Camp from: ' + self.participant_id.tocampfromdestination_id.webtourname
            else:
                self.webtourcamptransportation = ''
        elif self.the_date == self.participant_id.fromcampdate:
            if self.participant_id.transport_from_camp and self.participant_id.fromcamptodestination_id.placename:
                self.webtourcamptransportation = 'From Camp to: ' + self.participant_id.fromcamptodestination_id.webtourname
            else:
                self.webtourcamptransportation = ''
        else:
            self.webtourcamptransportation = ''
        