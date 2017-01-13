# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
class FinalRegistration(models.Model):
    '''
    Final registration for a scout group to an event
    '''
    _inherit = 'event.registration'
    total_price = fields.Float('Total Price')
    child_certificates_accept = fields.Boolean('Check declaration of child certificates')
    child_certificates_date = fields.Date('Date of declaration') 
    child_certificates_user = fields.Char('User signing declaration')
    friendship_group_ids = fields.One2many('event.registration.friendshipgrouplist','own_registration_id','Friendship Groups')
    reverse_friendship_group_ids = fields.One2many('event.registration.friendshipgrouplist','friendship_group_registration_id','Reverse Friendship Groups')
    pioneering_pole_depot_id = fields.Many2one('event.registration.pioneeringpoledepot','Pioneering Pole Depot')
    event_days = fields.One2many(related='event_id.event_day_ids', string='Event Days', readonly=True)
    participants_camp_day_ids = fields.One2many('campos.event.participant.day','registration_id_stored','Participant Camp Days')
    need_ids = fields.One2many('event.registration.needlist','registration_id','Special needs')
    other_need = fields.Boolean('Other special need(s)')
    other_need_description = fields.Text('Other Need description')
    other_need_update_date = fields.Date('Need updated')
    @api.onchange('child_certificates_accept')
    @api.one
    def _child_certificates_accept_checked (self):
        if (self.child_certificates_accept == True):
            self.child_certificates_user = self.env.user.name
            self.child_certificates_date = fields.Date.today()
        else:
            self.child_certificates_user = False
            self.child_certificates_date = False
    @api.one
    def write(self, vals):
        if 'child_certificates_accept' in vals:
            if vals['child_certificates_accept'] == True:
                vals['child_certificates_user'] = self.env.user.name
                vals['child_certificates_date'] = fields.Date.today()
            else:
                vals['child_certificates_user'] = False
                vals['child_certificates_date'] = False
        retval = super(FinalRegistration, self).write(vals)
        if ('subcamp_id' in vals or 'camp_area_id' in vals) and self.group_country_code2 == 'DK':
            friendship_group_list = self.friendship_group_ids
            for friendship_group_reg in friendship_group_list:
                vals2 = {}
                if 'camp_area_id' in vals:
                    vals2['camp_area_id'] = vals['camp_area_id']
                if 'subcamp_id' in vals:
                    vals2['subcamp_id'] = vals['subcamp_id']
                reg_id = friendship_group_reg.friendship_group_registration_id
                reg_id.write(vals2)
        return retval

    @api.onchange('other_need_description')
    def _other_need_description_changed(self):
        self.other_need_update_date = fields.Date.today()

class FriendshipGroupList(models.Model):
    _name = 'event.registration.friendshipgrouplist'
    own_registration_id = fields.Many2one('event.registration', 'Registration', required=True,  domain="[('partner_id.country_id.code','=','DK')]")
    friendship_group_registration_id = fields.Many2one('event.registration','Friendship Group', required=True,  domain="[('partner_id.scoutgroup','=',True),('partner_id.country_id.code','!=','DK')]")
    _sql_constraints = [('unique_friendship_group_regid', 'unique(friendship_group_registration_id)', _('A group can only be added once as friendship group'))]
# When connecting friendship group to registration, then copy camp_area_id+subcamp_id to friendship groups registration
    @api.model
    def create(self, vals):
        retval = super(FriendshipGroupList, self).create(vals)
        own_registration_id = vals['own_registration_id']
        own_registration = self.env['event.registration'].search([('id', '=', own_registration_id)])
        camp_area_id = own_registration.camp_area_id.id
        subcamp_id = own_registration.subcamp_id.id
        vals2 = {}
        vals2['camp_area_id'] = camp_area_id
        vals2['subcamp_id'] = subcamp_id
        friendship_group_registration_id = vals['friendship_group_registration_id']
        friendship_group_registration = self.env['event.registration'].search([('id', '=', friendship_group_registration_id)])
        friendship_group_registration.write(vals2)
        return retval

class FinalRegistrationParticipant(models.Model):
    '''
    Extending event participant for final registration
    '''
    _inherit = 'campos.event.participant'
    transport_to_camp = fields.Boolean('Common transport to camp', default=True)
    transport_from_camp = fields.Boolean('Common transport from camp', default=True)
    camp_day_ids = fields.One2many('campos.event.participant.day','participant_id','Camp Day List')
#    reside_other_group_id = fields.Many2one('res.partner', 'Resides with other group')
    access_token_id = fields.Char('Id of Access Token')
    @api.model
    def create(self, vals):
        par = super(FinalRegistrationParticipant, self).create(vals)
        for day in par.registration_id.event_id.event_day_ids.filtered(lambda r: r.event_period == 'maincamp'):
            new = par.env['campos.event.participant.day'].create({'participant_id': par.id,
                                                         'day_id': day.id,
                                                         'will_participate' : False
                                                         })
        return par

    @api.multi
    def check_all_days(self):
        for record in self.camp_day_ids:
            record.will_participate = True
            
    @api.multi
    def uncheck_all_days(self):
        for record in self.camp_day_ids:
            record.will_participate = False
    @api.one
    def inactivate_participant(self):
        self.state = 'deregistered'
    @api.one
    def activate_participant(self):
        self.state = 'draft'
    
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
    event_period = fields.Selection([('precamp', 'Pre Camp'),
                                     ('maincamp', 'Main Camp'),
                                     ('postcamp', 'Post Camp')], default='maincamp', string='Period')
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
    for_group = fields.Boolean('For Scout Groups')
    for_staff = fields.Boolean('For Jobbers')

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
    
    