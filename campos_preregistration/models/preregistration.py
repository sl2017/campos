# -*- coding: utf-8 -*-

from openerp.addons.base_geoengine import geo_model
from openerp.addons.base_geoengine import fields as geo_fields

from openerp import models, fields, api, exceptions, _
import logging
_logger = logging.getLogger(__name__)


class Preregistration(geo_model.GeoModel):
 
    '''
    Pre-registration for a scout group to an event
    '''
    _inherit = 'event.registration'
#    group_name = fields.Char('Group Name')
#    group_association = fields.Many2one('campos.scout.org','Scout Organization')
#    group_world_association = fields.Selection(related='group_association.worldorg', string='World Organisation', readonly=True)
    group_entrypoint = fields.Many2one('event.registration.entryexitpoint','Point of entry into Denmark')
    group_exitpoint = fields.Many2one('event.registration.entryexitpoint','Point of exit from Denmark')
#    group_municipality = fields.Many2one('campos.municipality','Municipallity')
#    group_country = fields.Many2one('res.country', 'Country')
#    group_country_name = fields.Char(related='group_country.name', string='Country Name', readonly=True)
#    group_country_code = fields.Char(related='group_country.code', string='Country Code', readonly=True)
    group_country_code2 = fields.Char(related='partner_id.country_id.code', string='Country Code2', readonly=True)
#    association_groupid = fields.Char('Groups id (number) at local association')
    prereg_participant_ids = fields.One2many('event.registration.participants','registration_id','Participants')
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
    pre_reg_cnt = fields.Integer('Pre Reg #', compute='_compute_pre_req_cnt')
    geo_point = geo_fields.GeoPoint(related='partner_id.geo_point')
    #@api.depends('participant_ids.participant_total')
    @api.multi
    def _compute_pre_req_cnt(self):
        for record in self:
            record.pre_reg_cnt = sum(line.participant_total for line in record.prereg_participant_ids)
    
    
    @api.one
    def cancel_registration (self):
        self.state = 'cancel'
        template = self.env.ref('campos_preregistration.preregistration_cancel_mail')
        assert template._name == 'email.template'
        try:
            template.send_mail(self.id)
        except:
            pass
        
    @api.one
    def reopen_registration (self):
        self.state = 'draft'

class PreregistrationAgegroup(models.Model):
    _description = 'Age Group'
    _name = 'event.registration.agegroup'
    
    name = fields.Char('Age Group name', required=True, translate=True)
    age_from = fields.Integer('From age', required=True)
    age_to = fields.Integer('To age', required=True)
    
class PreregistrationPioneeringPole(models.Model):
    _description = 'Pioneering Pole'
    _name = 'event.registration.pioneeringpole'
    
    name = fields.Char('Pioneering Pole Name', required=True, translate=True)
    length = fields.Integer('Length', required=True)

class PreregistrationTransportType(models.Model):
    _description = 'Transport Type'
    _name = 'event.registration.transporttype'
    
    name = fields.Char('Transport Type Name', required=True, translate=True)

class PreregistrationEntryExitPoint(models.Model):
    _name = 'event.registration.entryexitpoint'
    name = fields.Char('Entry/exit Point Name', required=True, translate=True)

class PreregistrationParticipants(models.Model):
    _description = 'Preregistration Participants'
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

    def _calculate_default_start_date (self):
        return fields.Date.from_string(self.registration_id.event_begin_date)

    @api.depends ('participant_total','participant_own_transport_to_camp_total','participant_own_transport_from_camp_total')
    @api.one
    def _calculate_common_transport (self):
        for record in self:
            record.participant_common_transport_to_camp_total = record.participant_total - record.participant_own_transport_to_camp_total
            record.participant_common_transport_from_camp_total = record.participant_total - record.participant_own_transport_from_camp_total
            if (record.participant_own_transport_to_camp_total==0 and record.participant_own_transport_from_camp_total==0):
                record.participant_own_transport_type=None

    def _check_from_before_end(self):
        if self.participant_from_date < self.participant_to_date:
            return True
        return False
    
    @api.one
    @api.constrains('participant_total','participant_own_transport_to_camp_total','participant_own_transport_from_camp_total')
    def validation_own_transport_numbers(self):
        if self.participant_own_transport_to_camp_total>self.participant_total:
            raise exceptions.ValidationError(_('Own transport to camp more than total participants'))
        if self.participant_own_transport_from_camp_total>self.participant_total:
            raise exceptions.ValidationError(_('Own transport from camp more than total participants'))
    
    @api.multi
    @api.constrains('participant_own_transport_to_camp_total','participant_own_transport_from_camp_total','participant_own_transport_type')
    def validation_own_transport_type(self):
        for record in self:
            if (record.participant_own_transport_to_camp_total>0 or record.participant_own_transport_from_camp_total>0) and record.participant_own_transport_type.name==False:
                raise exceptions.ValidationError(_('Primary own transport must be chosen when number of own transport to or from camp is greater than 0'))

    @api.one
    @api.constrains('participant_from_date', 'participant_to_date')
    def validation_from_to_dates(self):
        validation_result = self._check_from_before_end()
        if validation_result != True:
            raise exceptions.ValidationError(_('Date of arrival must be before date of departure'))
    
    @api.one
    @api.constrains('participant_from_date', 'participant_to_date')
    def validation_transport_in_camp_period(self):
        event_begin_date_located = self.registration_id.event_id.date_begin_located
        event_end_date_located = self.registration_id.event_id.date_end_located
        if (fields.Datetime.from_string(event_begin_date_located).date() > fields.Datetime.from_string(self.participant_from_date).date() or 
        fields.Datetime.from_string(event_end_date_located).date() < fields.Datetime.from_string(self.participant_to_date).date()):
            raise exceptions.ValidationError(_('Date of arrival and departure must be within camp period')+' ('+event_begin_date_located+' - '+ event_end_date_located + ')')

class PreregistrationPolelist(models.Model):
    _description = 'Polelist'
    _name = 'event.registration.polelist'
    
    registration_id = fields.Many2one('event.registration', 'Registration')
    pioneeringpole_id = fields.Many2one('event.registration.pioneeringpole','Pole type', required=True)
    polecount  = fields.Integer('Number of pioneering poles', required=True)
    _sql_constraints = [('pole_id_unique_on_registration', 'unique(registration_id,pioneeringpole_id)', ' Please only make one line with each type of pole')]
