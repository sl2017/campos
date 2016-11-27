# -*- coding: utf-8 -*-

from openerp import models, fields
class FinalRegistration(models.Model):
    '''
    Final registration for a scout group to an event
    '''
    _inherit = 'event.registration'
#  **********shouldn't really be integer**********
    total_price = fields.Integer('Total Price')
    child_certificates_accept = fields.Boolean('We declare to not bring any leaders not having a child certificate')
    child_certificates_date = fields.Date('Date of declaration') 
    child_certificates_user = fields.Char('User signing declaration')
    friendhip_group_ids = fields.One2many('event.registration.friendshipgrouplist','registration_id','Friendship Groups')
    
    
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
    own_transport_to_camp = fields.Boolean('No common transport TO camp')
    own_transport_from_camp = fields.Boolean('No common transport FROM camp')
#    camp_day_ids = fields.One2many('campos.event.participant.day','partner_id','Camp Day List')
    reside_other_group_id = fields.Many2one('res.partner', 'Resides with this group')
    reside_in_caravan =fields.Char('Resides in caravan?!?!')
    access_token_id = fields.Char('Id of Access Token')
    
class ParticipantCampDay(models.Model):
    '''
    Extending event participant for final registration
    '''
    _name = 'campos.event.participant.day'
    participant_id = fields.Many2one('campos.event.participant', 'Participant')
    participation_date = fields.Char('Date')
    will_participate = fields.Boolean('Does Participate')
    
    
    