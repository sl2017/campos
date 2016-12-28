# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
#HIDEfrom email import _name
#HIDEfrom campos_event.models import participant
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
    event_days = fields.One2many(related='event_id.event_day_ids', string='Event Days', readonly=True)
#    participants_camp_day_ids = fields.One2many(related='participant_ids.camp_day_ids', string='Participant Camp Days')
    participants_camp_day_ids = fields.One2many('campos.event.participant.day','registration_id_stored','Participant Camp Days')
    need_ids = fields.One2many('event.registration.needlist','registration_id','Special needs')
    other_need = fields.Boolean('Other special need(s)')
    other_need_description = fields.Char('Need desription')
    other_need_update_date = fields.Date('Need updated') 
    @api.onchange('child_certificates_accept')
    def _child_certificates_accept_checked (self):
        if (self.child_certificates_accept == True):
            self.child_certificates_user = self.env.user.name
            self.child_certificates_date = fields.Date.today()
        else:
            self.child_certificates_user = ''
            self.child_certificates_date = ''
        
#        self.child_certificates_date = fields.Date.to_string(fields.Date.today())
    
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
    own_transport_to_camp = fields.Boolean('No common transport TO camp')
    own_transport_from_camp = fields.Boolean('No common transport FROM camp')
    camp_day_ids = fields.One2many('campos.event.participant.day','participant_id','Camp Day List')
    reside_other_group_id = fields.Many2one('res.partner', 'Resides with this group')
    reside_in_caravan =fields.Char('Resides in caravan?!?!')
    access_token_id = fields.Char('Id of Access Token')
    @api.multi
    def create_participant_days(self):
        for day in self.registration_id.event_id.event_day_ids:
            new = self.env['campos.event.participant.day'].create({'participant_id': self.id,
                                                         'day_id': day.id,
                                                         'will_participate' : False
                                                         })
    
#    def _default_participant_days(self):
#        days = self.registration_id.event_days
#        return [(id,d.id,False) for d in days]
#    m2m_camp_day_ids = fields.Many2many(comodel_name='event.day',  relation='campos_event_participant_day', column1='participant_id',column2='day_id', default=_default_participant_days)
    
    
class ParticipantCampDay(models.Model):
    '''
    One persons participation to a camp in one day
    '''
    _name = 'campos.event.participant.day'
    participant_id = fields.Many2one('campos.event.participant', 'Participant')
    registration_id_stored = fields.Many2one(related='participant_id.registration_id', string='Registration', store=True)
    day_id = fields.Many2one('event.day', 'Event day')
    the_date = fields.Date(related='day_id.event_date', String='Event date')
    will_participate = fields.Boolean('Will participate this day?')

class EventDay(models.Model):
    '''
    An Event day
    '''
    _name='event.day'
    event_date = fields.Date('Date', required=True)
    event_id = fields.Many2one('event.event', 'Event day', required=True)
    
class FinalRegistrationEvent(models.Model):
    '''
    Event extended for final registration
    '''
    _inherit = 'event.event'
    event_day_ids = fields.One2many('event.day','event_id','Event Days')


class PioneeringPoleDepot(models.Model):
    '''
    List of pioneering pole depots
    '''
    _description = 'Pioneering Pole Depot'
    _name='event.registration.pioneeringpoledepot'
    name = fields.Char('Depot Name', required=True, translate=True)

    
class RegistrationNeed(models.Model):
    '''
    A groups special need at the camp
    '''
    _description = 'Group Need'
    _name='event.registration.need'
    name = fields.Char('Need Name', required=True, translate=True)

class RegistrationNeeds(models.Model):
    '''
    Special need on a registration
    '''
    _description = 'Special need on a registration'
    _name='event.registration.needlist'
    registration_id  = fields.Many2one('event.registration', 'Registration', required=True)
    need_id = fields.Many2one('event.registration.need','Need', required=True)
    need_count = fields.Integer('Count', required=True)
    _sql_constraints = [('need_id_unique_on_registration', 'unique(registration_id,need_id)', _('Each need can only be added once'))]
    
    