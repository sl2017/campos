'''
Created on 2. dec. 2016

@author: jda.dk
'''
import logging

_logger = logging.getLogger(__name__)

from openerp import models, fields, api
from ..interface import webtourinterface
class WebtourRegistration(models.Model):
    _inherit = 'event.registration'
    webtourusgroupidno = fields.Char('webtour us Group ID no', required=False, Default='')
    
    @api.one
    def createTestPaticipants(self):
                
        for age_group in self.participant_ids:
            _logger.info("createTestPaticipants: %s",age_group.participant_age_group_id.name)
            for i in range(1,age_group.participant_total):
                    dicto0 = {}
                    dicto0["name"] = age_group.registration_id.name + ' ' + age_group.participant_age_group_id.name + 'Test ID ' + str(i)   
                    dicto0["email"] = 'jd@darum.name'             
                
                    partner_obj = self.env['res.partner']                
                    newpartner = partner_obj.create(dicto0)
                    dicto1 = {}
                    dicto1["partner_id"] = newpartner.id 
                    dicto1["registration_id"] = self.id
                    dicto1["participant"] = True     
                    #dicto1["tocampfromdestination_id"] = self.env['campos.webtourusdestination'].search([('destinationidno','=',4390)]).id     
                    #dicto1["fromcamptodestination_id"] = dicto1["tocampfromdestination_id"]  
                    dicto1["tocampdate"] = age_group.participant_from_date
                    dicto1["fromcampdate"] = age_group.participant_to_date
                    dicto1["usecamptransporttocamp"] = i > age_group.participant_own_transport_to_camp_total
                    dicto1["usecamptransportfromcamp"] = i > age_group.participant_own_transport_from_camp_total

                    _logger.info("createTestPaticipants: %s",dicto1)
                                                  
                    newparticipant_obj = self.env['campos.event.participant']                
                    newparticipant = newparticipant_obj.create(dicto1)
                    newparticipant.tocampfromdestination_id = self.env['campos.webtourusdestination'].search([('destinationidno','=',4390)]).id 
                    newparticipant.fromcamptodestination_id = newparticipant.tocampfromdestination_id
                


                    
