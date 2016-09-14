# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions
class Preregistration(models.Model):
    '''
    Pre-registration for a scout group to an event
    '''
    _inherit = 'event.registration'
    group_name = fields.Char('Group Name')
    group_association = fields.Many2one('campos.scout.org','Scout Organization')
    group_world_association = fields.Selection(related='group_association.worldorg', string='World Organisation', readonly=True)
    group_entrypoint = fields.Char('Point of entry into Denmark')
    group_municipality = fields.Many2one('campos.municipality','Municipallity')
    group_country = fields.Many2one('res.country', 'Country')
    group_country_name = fields.Char(related='group_country.name', string='Country Name', readonly=True)
    group_country_code = fields.Char(related='group_country.code', string='Country Code', readonly=True)
    association_groupid = fields.Char('Groups id (number) at local association')
    participant_ids = fields.One2many('event.registration.participants','registration_id','Participants')
    pioneeringpole_ids = fields.One2many('event.registration.polelist','registration_id','Pioneering Poles')
    handicap = fields.Boolean('Participant(s) with handicap or other special considerations?')
    handicap_description = fields.Text('Description of handicap / special considerations')
    handicap_needs = fields.Text('Special needs due to handicap / special considerations')
    friendship_group = fields.Boolean('Request placement with friendship group?')
    friendship_group_name = fields.Char('Friendship group name, association, country')
    friendship_group_info = fields.Text('Friendship group other info')
    friendship_group_desire = fields.Boolean('Would like a friendship group?')
    friendship_group_desire_country = fields.Many2one('res.country', 'Country of friendship group (optional)')
    friendship_group_home_hospitality = fields.Boolean('Would like to offer home hospitality?')
    group_camp_agreements = fields.Text('Official agreements')
    internal_information = fields.Text('Internal information',  groups="campos_event.group_campos_staff,campos_event.group_campos_admin")

class PreregistrationAgegroup(models.Model):
    _name = 'event.registration.agegroup'
    name = fields.Char('Age Group name', required=True)
    age_from = fields.Integer('From age', required=True)
    age_to = fields.Integer('To age', required=True)
    
class PreregistrationPioneeringPole(models.Model):
    _name = 'event.registration.pioneeringpole'
    name = fields.Char('Pioneering Pole Name', required=True)
    length = fields.Integer('Length', required=True)

class PreregistrationTransportType(models.Model):
    _name = 'event.registration.transporttype'
    name = fields.Char('Transport Type Name', required=True)

class PreregistrationParticipants(models.Model):
    _name = 'event.registration.participants'
    registration_id = fields.Many2one('event.registration', 'Registration')
    participant_age_group_id = fields.Many2one('event.registration.agegroup','Age Group', required=True)
    participant_total  = fields.Integer('Number of participants', required=True)
    participant_from_date = fields.Date('Date of arrival', required=True, default='2017-07-22')
    participant_to_date = fields.Date('Date of departure', required=True, default='2017-07-30')
    participant_own_transport_to_camp_total  = fields.Integer('No. of own transport to camp', required=True)
    participant_own_transport_from_camp_total  = fields.Integer('No. of own transport from camp', required=True)
    participant_common_transport_to_camp_total  = fields.Integer(compute = '_calculate_common_transport', string='No. of common transport to camp')
    participant_common_transport_from_camp_total  = fields.Integer(compute = '_calculate_common_transport', string='No. of common transport from camp')
    participant_own_transport_type = fields.Many2one('event.registration.transporttype','Primary own transport')
    
#    participant_transport_note = fields.Char(compute = '_calculate_note', string='Note')
    
#    @api.depends ('participant_total','participant_transport_to_camp_total','participant_transport_from_camp_total')
#    @api.multi
#    def _calculate_note (self):
#        for record in self:
#            if record.participant_transport_to_camp_total<record.participant_total or record.participant_transport_from_camp_total<record.participant_total:
#                record.participant_transport_note = 'Not all participants with transport.'
#            if record.participant_transport_to_camp_total>record.participant_total or record.participant_transport_from_camp_total>record.participant_total:
#                record.participant_transport_note = 'More than all participants with transport.'
    @api.one
    def _default_start_date (self):   
        # 21-30 
        return '2017-07-07'         
    
    @api.depends ('participant_total','participant_own_transport_to_camp_total','participant_own_transport_from_camp_total')
    @api.one
    def _calculate_common_transport (self):
        for record in self:
            record.participant_common_transport_to_camp_total = record.participant_total - record.participant_own_transport_to_camp_total
            record.participant_common_transport_from_camp_total = record.participant_total - record.participant_own_transport_from_camp_total
                
    def _check_from_before_end(self):
        if self.participant_from_date < self.participant_to_date:
            return True
        return False
    
    @api.one
    @api.constrains('participant_total','participant_own_transport_to_camp_total','participant_own_transport_from_camp_total')
    def validation_own_transport_numbers(self):
        if self.participant_own_transport_to_camp_total>self.participant_total:
            raise exceptions.ValidationError('Own transport to camp more than total participants')
        if self.participant_own_transport_from_camp_total>self.participant_total:
            raise exceptions.ValidationError('Own transport from camp more than total participants')

    @api.one
    @api.constrains('participant_from_date', 'participant_to_date')
    def validation_from_to_dates(self):
        validation_result = self._check_from_before_end()
        if validation_result != True:
            raise exceptions.ValidationError('Date of arrival must be before date of departure')

    def _check_transport_in_camp_period(self):
        if (fields.Datetime.from_string(self.registration_id.event_begin_date).date() <= fields.Datetime.from_string(self.participant_from_date).date() and 
        fields.Datetime.from_string(self.registration_id.event_end_date).date() >= fields.Datetime.from_string(self.participant_to_date).date()):
            return True
        return False
    
    @api.one
    @api.constrains('participant_from_date', 'participant_to_date')
    def validation_transport_in_camp_period(self):
        validation_result = self._check_transport_in_camp_period()
        if validation_result != True:
            raise exceptions.ValidationError('Date of arrival and departure must be within camp period ('+self.registration_id.event_begin_date+' - '+ self.registration_id.event_end_date + ')')

class PreregistrationPolelist(models.Model):
    _name = 'event.registration.polelist'
    registration_id = fields.Many2one('event.registration', 'Registration')
    pioneeringpole_id = fields.Many2one('event.registration.pioneeringpole','Pole type', required=True)
    polecount  = fields.Integer('Number of pioneering poles', required=True)
    _sql_constraints = [('pole_id_unique_on_registration', 'unique(registration_id,pioneeringpole_id)', ' Please only make one line with each type of pole')]
