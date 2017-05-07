# -*- coding: utf-8 -*-

from openerp import models, fields, api, _, exceptions
import datetime
import logging
_logger = logging.getLogger(__name__)


class FinalRegistration(models.Model):
    '''
    Final registration for a scout group to an event
    '''
    _inherit = 'event.registration'
    total_price = fields.Float('Total Price')
    child_certificates_accept = fields.Boolean('Check declaration of child certificates')
    child_certificates_date = fields.Date('Date of declaration') 
    child_certificates_user = fields.Char('User signing declaration')
    friendship_group_ids = fields.One2many('campos.reg.friendship','own_registration_id','Friendship Groups')
    reverse_friendship_group_ids = fields.One2many('campos.reg.friendship','friendship_group_reg_id','Reverse Friendship Groups')
    pioneering_pole_depot_id = fields.Many2one('event.registration.pioneeringpoledepot','Pioneering Pole Depot')
    event_days = fields.One2many(related='event_id.event_day_ids', string='Event Days', readonly=True)
    participants_camp_day_ids = fields.One2many('campos.event.participant.day','registration_id_stored','Participant Camp Days')
    need_ids = fields.One2many('event.registration.needlist','registration_id','Special needs')
    other_need = fields.Boolean('Other special need(s)')
    other_need_description = fields.Text('Other Need description')
    other_need_update_date = fields.Date('Need updated')
    meatlist_ids = fields.One2many('event.registration.meatlist','registration_id','Meat Choices')
    number_of_tents = fields.Integer('Number of patrol tents (for personal accommodation)',help='Information about tents will not be used in the calculation of area for the individual group. This will be based on the number of participants. More tents will not give a bigger campsite.')
    number_of_other_small_tents = fields.Integer('Number of other tents, less than 50 m2')
    large_tents = fields.Text('Number of assembly and staff tents, more than 50 m2, incl. their sizes', help='If the tent is larger than 50m2, it must be approved by the authorities, via the camp''s emergency management. This also applies to mast sails if there are sides of more than half of the circumference.')
    mast_sails = fields.Text('Number of mast sails, incl. diameters, if they have sides and on how much of the cercumfence.', help='If the tent is larger than 50m2, it must be approved by the authorities, via the camp''s emergency management. This also applies to mast sails if there are sides of more than half of the circumference.')
    number_gas_burners = fields.Integer('Number of gas burners with tanks more than 2 kg', help='When using a gas blower, place the burner on non-combustible material in a size dimensioned according to the size of the gas flue. There may be only 1 gas bottle in connection with each gas blow. The gas bottle must not exceed 11 kg. There may be 1 extra gas bottle of max. 11 kg on each campsite. Excess gas bottles must be stored in another location, according to the instructions given by the emergency department.')
    pioneering_in_height = fields.Boolean('Are you planning to construct pioneering more than 4 meters high?',help='Pioneering constructions above 4 meters height must be approved by the authorities, through the camp''s emergency management (this does not include flagpoles and other single masts).')
    pioneering_in_height_with_persons = fields.Boolean('Are you planning to construct pioneering with persons staying above 2 meters?',help='Pioneeing constructions planned for persons staying above 2 meters height must be approved by the authorities, through the camp''s emergency management.')
    raised_sleeping = fields.Boolean('Are you planning to have raised sleeping places?',help='Pioneering constructions with planned accommodation at more than 1 meter height, must be approved by the authorities through the camp''s emergency management.')
    gear_transport = fields.Text('How will get your gear to the camp (own trailer(s)/common transport with other groups like rented truck or carriage man)?',help='The emergency management of the camp recommends that the groups use the opportunity to deliver equipment at the camp before 06:00 on 22 July, as it will not be possible to enter the campsite with vehicles not belonging to the camp, cf. the camp''s traffic policy.')
    glofo_number_participants = fields.Integer('Number of participants in Grean Profile')
    glofo_co2_amount = fields.Integer('Grean Profile, amount of CO2 (in grams)')
    glofo_co2_amount_total = fields.Integer('Total amount of CO2 (in grams)')
    glofo_remarks = fields.Text('Remarks (e.g. certain weeks chosen, more or fewer weeks than suggested, etc.)')
    car_ids = fields.One2many('campos.event.car','registration_id','Cars')

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
                reg_id = friendship_group_reg.friendship_group_reg_id
                reg_id.write(vals2)
        return retval

    @api.onchange('other_need_description')
    def _other_need_description_changed(self):
        self.other_need_update_date = fields.Date.today()
        
    @api.multi
    def action_open_groupparticipants(self):
        self.ensure_one()
        
        view = self.env.ref('campos_final_registration.view_form_finalregistration_participant')
        treeview = self.env.ref('campos_final_registration.view_tree_finalregistration_participant')
        _logger.info('"OPEN PAR: %s %s', view, treeview)
        return {
                'name': _("Participants from %s" % self.name),
                'view_mode': 'tree,form',
                'view_type': 'form',
                'views': [(treeview.id, 'tree'), (view.id, 'form')],
                'res_model': 'campos.event.participant',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'domain': [('registration_id', '=', self.id)],
                'context': {
                            'default_registration_id': self.id,
                            'default_participant': True,
                            'default_parent_id': self.partner_id.id,
                            }
            }

class FriendshipGroupList(models.Model):
    _name = 'campos.reg.friendship'
    own_registration_id = fields.Many2one('event.registration', 'Registration', required=True,  domain="[('partner_id.country_id.code','=','DK')]")
    friendship_group_reg_id = fields.Many2one('event.registration','Friendship Group', required=True,  domain="[('partner_id.scoutgroup','=',True),('partner_id.country_id.code','!=','DK')]")
    _sql_constraints = [('unique_friendship_group_regid', 'unique(friendship_group_reg_id)', _('A group can only be added once as friendship group'))]
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
        friendship_group_reg_id = vals['friendship_group_reg_id']
        friendship_group_registration = self.env['event.registration'].search([('id', '=', friendship_group_reg_id)])
        friendship_group_registration.write(vals2)
        return retval

class FinalRegistrationParticipant(models.Model):
    '''
    Extending event participant for final registration
    '''
    _inherit = 'campos.event.participant'
    transport_to_camp = fields.Boolean('Common transport to camp', default=True, help="Remember to mark this, with you wish to use the joint transportation. See page 29 in the instructions.")
    transport_from_camp = fields.Boolean('Common transport from camp', default=True, help="Remember to mark this, with you wish to use the joint transportation. See page 29 in the instructions.")
    camp_day_ids = fields.One2many('campos.event.participant.day','participant_id','Camp Day List', help="Chose which days you're participating in the jamboree")
    access_token_id = fields.Char('Id of Access Token')
    dates_summery = fields.Char('Camp Days', compute='_compute_dates_summery', store=True)
    own_note = fields.Char('Own Note')
    passport_number = fields.Integer('Passport number')
    visa_required = fields.Boolean(related='registration_id.partner_id.country_id.visa_req', string='Visa Required', readonly=True)
    group_country_code = fields.Char(related='registration_id.partner_id.country_id.code', string='Country Code', readonly=True)
#    green_transport = fields.Boolean('Whish to participate in Green Transport - CO2 neutral?', default=False)
#    green_transport_origin = fields.Selection([('home', 'From home'),
#                              ('border','From municipallty border')],
#                             'From where will your CO2 neutral transportation start?',
#                             default='border')
#    green_transport_means = fields.Selection([('foot', 'By foot'),
#                              ('bycicle','By bike'),
#                              ('water','By water without engine'),
#                              ('hitchhiking','By hitchhiking')],
#                             'How will you get to the camp?')
#    green_transport_borrow_bike = fields.Boolean('Whish to borrow a bike from the ferry at Fynshav?', default=False)
#    green_transport_mail = fields.Char('Mail addresse for communication about Green Transport')
    
    @api.onchange('name')
    def onchange_name(self):
        if not self.camp_day_ids:
            days_ids = []
            if self.participant:
                for day in self.env['event.day'].search([('event_id', '=', self.registration_id.event_id.id),('event_period' ,'=','maincamp')]):
                    days_ids.append((0,0, {'participant_id': self.id,
                                           'day_id': day.id,
                                           'will_participate': True if day.event_period == 'maincamp' else False,
                                           'the_date': day.event_date,
                                           }))
            if self.staff:
                for day in self.env['event.day'].search([('event_id', '=', self.registration_id.event_id.id),('event_period' ,'!=','maincamp')]):
                    days_ids.append((0,0, {'participant_id': self.id,
                                           'day_id': day.id,
                                           'will_participate': True if day.event_period == 'maincamp' else False,
                                           'the_date': day.event_date,
                                           }))
                    
            self.camp_day_ids = days_ids
    @api.model
    def create(self, vals):
        par = super(FinalRegistrationParticipant, self).create(vals)
        if not par.camp_day_ids:
            if par.participant:
                for day in par.registration_id.event_id.event_day_ids.filtered(lambda r: r.event_period == 'maincamp'):
                    new = par.env['campos.event.participant.day'].create({'participant_id': par.id,
                                                                          'day_id': day.id,
                                                                          'will_participate' : False
                                                                          })
            if par.staff:
                for day in par.registration_id.event_id.event_day_ids:
                    new = par.env['campos.event.participant.day'].create({'participant_id': par.id,
                                                                          'day_id': day.id,
                                                                          'will_participate' : False
                                                                          })
        return par
    
    @api.multi
    @api.depends('camp_day_ids', 'camp_day_ids.will_participate')
    def _compute_dates_summery(self):
        for par in self:
            dates = []
            for d in par.camp_day_ids:
                if d.will_participate:
                    dates.append(d.the_date)
            dates.sort()
            text = ''
            for d in dates:
                text += ',' + d[8:]
            if text > '': 
                text = text[1:]
                if text == '22,23,24,25,26,27,28,29,30':
                    text = _('Full camp')
                par.dates_summery = text
                
    def check_camp_days(self):
        masterdays = set()
        if self.staff:
            masterdays = set(self.registration_id.event_id.event_day_ids.ids)
        else:
            masterdays = set(self.registration_id.event_id.event_day_ids.filtered(lambda r: r.event_period == 'maincamp').ids)
        pardays = set(self.camp_day_ids.mapped('day_id').ids)
        for d in list(masterdays - pardays):
            self.env['campos.event.participant.day'].create({'participant_id': self.id,
                                                             'day_id': d})
        
            

    @api.multi
    def check_all_days(self):
        for record in self:
            record.check_camp_days()
            for day in record.camp_day_ids:
                day.will_participate = True
    @api.multi
    def check_all_maincamp_days(self):
        for record in self:
            record.check_camp_days()
            for day in record.camp_day_ids.filtered(lambda r: r.day_id.event_period == 'maincamp'):
                day.will_participate = True
    @api.multi
    def check_all_first_half_days(self):
        wednesday = fields.Datetime.from_string('2017-07-26').date()
        for record in self:
            record.check_camp_days()
            for day in record.camp_day_ids.filtered(lambda r: r.day_id.event_period == 'maincamp' and fields.Datetime.from_string(r.the_date).date() <= wednesday):
                day.will_participate = True
            for day in record.camp_day_ids.filtered(lambda r: r.day_id.event_period == 'maincamp' and fields.Datetime.from_string(r.the_date).date() > wednesday):
                day.will_participate = False
    @api.multi
    def check_all_second_half_days(self):
        wednesday = fields.Datetime.from_string('2017-07-26').date()
        for record in self:
            record.check_camp_days()
            for day in record.camp_day_ids.filtered(lambda r: r.day_id.event_period == 'maincamp' and fields.Datetime.from_string(r.the_date).date() >= wednesday):
                day.will_participate = True
            for day in record.camp_day_ids.filtered(lambda r: r.day_id.event_period == 'maincamp' and fields.Datetime.from_string(r.the_date).date() < wednesday):
                day.will_participate = False
            
    @api.multi
    def uncheck_all_days(self):
        for record in self:
            record.check_camp_days()
            for day in record.camp_day_ids:
                day.will_participate = False
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
    _name= 'campos.event.participant.day'
    _description= 'Participant Camp Days'
    _order="day_id"
    participant_id = fields.Many2one('campos.event.participant', 'Participant')
    registration_id_stored = fields.Many2one(related='participant_id.registration_id', string='Registration', store=True)
    day_id = fields.Many2one('event.day', 'Event day')
    the_date = fields.Date(related='day_id.event_date', String='Event date', readonly=True, store=True)
    will_participate = fields.Boolean('Will participate this day?')

class EventDay(models.Model):
    '''
    An Event day
    '''
    _name='event.day'
    _order="event_date"
    event_date = fields.Date('Date', required=True)
    event_period = fields.Selection([('precamp', 'Pre Camp'),
                                     ('maincamp', 'Main Camp'),
                                     ('postcamp', 'Post Camp')], default='maincamp', string='Period')
    event_id = fields.Many2one('event.event', 'Event day', required=True)
#    event_day_meat_ids = fields.One2many('event.day.meat','event_day_id','Meat Types')
    
    @api.multi
    @api.depends('event_day', 'event_period')
    def name_get(self):
        result = []
        for ed in self:
            result.append((ed.id, '%s %s-%s' % (dict(self.fields_get(allfields=['event_period'])['event_period']['selection'])[ed.event_period], ed.event_date[8:], ed.event_date[5:7])))
        return result
    
class FinalRegistrationEvent(models.Model):
    '''
    Event extended for final registration
    '''
    _inherit = 'event.event'
    event_day_ids = fields.One2many('event.day','event_id','Event Days')
    event_day_meat_ids = fields.One2many('event.day.meat','event_id','Meat list per day')

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
    
class RegistrationMeatType(models.Model):
    '''
    List of meat types
    '''
    _description = 'List of meat types'
    _name='event.registration.meat'
    name = fields.Char('Name', required=True, translate=True)
    
class EventDayMeat(models.Model):
    '''
    Available meat types per event day
    '''
    _description = 'Available meat types per event day'
    _name='event.day.meat'
    _order="event_day_id"
    meat_id = fields.Many2one('event.registration.meat', 'Meat Type', required=True)
    event_day_id = fields.Many2one('event.day', 'Event Day', required=True)
    event_id = fields.Many2one(related='event_day_id.event_id', store=True)
#TODO   _sql_constraints = [('meat_unique_per_day', 'unique(meat_id,event_day_id)', _('Each meat type can only be added once per day'))]
    @api.multi
    def name_get(self):
        data = []
        for rec in self:
            display_value = ''
            display_value += rec.event_day_id.event_date or ""
            display_value += ' ['
            display_value += rec.meat_id.name or ""
            display_value += ']'
            data.append((rec.id, display_value))
        return data
    
class RegistrationMeat(models.Model):
    '''
    Chosen meat on a registration
    '''
    _description = 'Chosen meat on a registration'
    _name='event.registration.meatlist'
    _order="event_day_meat_id"
    registration_id = fields.Many2one('event.registration', 'Registration', required=True)
    event_day_meat_id = fields.Many2one('event.day.meat','Meat type choice', required=True)
    meat_count = fields.Integer('Count', required=True)
    event_day_id = fields.Many2one(related='event_day_meat_id.event_day_id')
    event_date = fields.Date(related='event_day_id.event_date')
    day_meat_total = fields.Integer('Day meat total', compute='_compute_meat_day_total')
    day_participant_total = fields.Integer('Day part. total', compute='_compute_participant_day_total')
#TODO   _sql_constraints = [('meat_unique_per_registration_camp_day', 'unique(registration_id,event_day_meat_id)', _('Each meat type can only be chosen once per day'))]
    
    @api.one
    @api.depends('event_day_meat_id', 'meat_count')
    def _compute_meat_day_total(self):
        self.day_meat_total = sum(self.env['event.registration.meatlist'].sudo().search([('registration_id', '=', self.registration_id.id),
                                                                                    ('event_day_id', '=', self.event_day_id.id)]).mapped('meat_count'))
    @api.one
    @api.depends('event_day_meat_id', 'meat_count')
    def _compute_participant_day_total(self):
        if self.event_date:
            participants_this_day = self.env['campos.event.participant.day'].search([('registration_id_stored', '=', self.registration_id.id),
                                                                                     ('will_participate', '=', True),
                                                                                     ('the_date','=',self.event_date),
                                                                                     ('participant_id.state','!=','deregistered'),
                                                                                     ('participant_id.birthdate','<','2015-07-22')]).mapped('participant_id')
            participants_next_day = self.env['campos.event.participant.day'].search([('registration_id_stored', '=', self.registration_id.id),
                                                                                     ('will_participate', '=', True),
                                                                                     ('the_date','=',fields.Datetime.from_string(self.event_date).date() + datetime.timedelta(days=1)),
                                                                                     ('participant_id.state','!=','deregistered'),
                                                                                     ('participant_id.birthdate','<','2015-07-22')]).mapped('participant_id')
            jobbers_both_days_count =  self.env['campos.jobber.accomodation'].search_count([('registration_id', '=', self.registration_id.id),
                                                                                     ('state', '=', 'approved'),
                                                                                     ('date_from','<=',self.event_date),
                                                                                     ('date_to','>=',fields.Datetime.from_string(self.event_date).date() + datetime.timedelta(days=1))])
            participants_both_days = participants_this_day & participants_next_day
            self.day_participant_total = len(participants_both_days)
            self.day_participant_total = self.day_participant_total + jobbers_both_days_count
        else:
            self.day_participant_total=0

    @api.multi
    @api.constrains('event_day_meat_id','meat_count')
    def _check_meat_count(self):
        for rec in self:
            if (rec.day_meat_total>rec.day_participant_total):
                raise exceptions.ValidationError(_('Number of ordered meat portions (%d) exceeds the number of dinner participants (%d) on %s. ' % (rec.day_meat_total,rec.day_participant_total, rec.event_date)))

class RegistrationCar(models.Model):
    '''
    A car needing a parking permit at the camp
    '''
    _description = 'A car for parking at the camp'
    _name='campos.event.car'
    registration_id  = fields.Many2one('event.registration', 'Registration', required=True)
    reg_number = fields.Char('Registration number (licence plate)', required=True)
    park_permit_start_date = fields.Date('Start date', required=True)
    park_permit_end_date = fields.Date('End date', required=True)
    phone_number = fields.Char('Contact phone number during camp period', required=True)
    @api.one
    @api.constrains('park_permit_start_date', 'park_permit_end_date')
    def validation_car_date_interval(self):
        if fields.Datetime.from_string(self.park_permit_start_date).date() > fields.Datetime.from_string(self.park_permit_end_date).date():
            raise exceptions.ValidationError(_('Start data cannot be after end date'))
