# -*- coding: utf-8 -*-

from openerp import models, fields, api
from email import _name
class FinalRegistration(models.Model):
    '''
    Final registration for a scout group to an event
    '''
    _inherit = 'event.registration'
    total_price = fields.Float('Total Price')
    child_certificates_accept = fields.Boolean('Check declaration of child certificates')
    child_certificates_date = fields.Date('Date of declaration') 
    child_certificates_user = fields.Char('User signing declaration')
    friendhip_group_ids = fields.One2many('event.registration.friendshipgrouplist','registration_id','Friendship Groups')
    pioneering_pole_depot_id = fields.Many2one('event.registration.pioneeringpoledepot','Pioneering Pole Depot')
    @api.depends ('child_certificates_accept')
    @api.one
    def _child_certificates_accept_checked (self):
        for record in self:
            record.child_certificates_date = fields.Date.to_string(fields.Date.today())
            record.child_certificates_user = 'test'
#            if (self.child_certificates_accept == 'True'):
    
    #if subcamp_id or camp_area_id of DK changed then update to same on friendship groups
    @api.depends ('subcamp_id','camp_area_id')
    @api.one
    def _update_friendship_group_supcamp_area (self):
        if (self.group_country_code2 == 'DK'):
            for record in self.friendhip_group_ids:
                record.friendship_group_id.subcamp_id=self.subcamp_id
                record.friendship_group_id.camp_area_id=self.camp_area_id

class FriendshipGroupList(models.Model):
    _name = 'event.registration.friendshipgrouplist'
    registration_id = fields.Many2one('event.registration', 'Registration', required=True)
    friendship_group_id = fields.Many2one('res.partner','Friendship Group', required=True)

class FinalRegistrationParticipant(models.Model):
    '''
    Extending event participant for final registration
    '''
    _inherit = 'campos.event.participant'
    has_allergy_gluten = fields.Boolean('Has Gluten Allergy')
    has_allergy_milk = fields.Boolean('Has Milk Allergy')
    # Other allergies???
    own_transport_to_camp = fields.Boolean('No common transport TO camp')
    own_transport_from_camp = fields.Boolean('No common transport FROM camp')
    camp_day_ids = fields.One2many('campos.event.participant.day','participant_id','Camp Day List')
    reside_other_group_id = fields.Many2one('res.partner', 'Resides with this group')
    reside_in_caravan =fields.Char('Resides in caravan?!?!')
    access_token_id = fields.Char('Id of Access Token')
    
class ParticipantCampDay(models.Model):
    '''
    One persons participation to a camp in one day
    '''
    _name = 'campos.event.participant.day'
    participant_id = fields.Many2one('campos.event.participant', 'Participant')
    participation_date = fields.Char('Date')
    will_participate = fields.Boolean('Does Participate')
    
class RegistrationCampDay(models.Model):
    '''
    A camp day
    '''
    _name='event.registration.day'
    
class PioneeringPoleDepot(models.Model):
    '''
    List of pioneering pole depots
    '''
    _description = 'Pioneering Pole Depot'
    _name='event.registration.pioneeringpoledepot'
    name = fields.Char('Depot Name', required=True, translate=True)

    
    
    