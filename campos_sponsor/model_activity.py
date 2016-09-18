# -*- coding: utf-8 -*-
from openerp import models, fields, api

class ActivityMain(models.Model):
    _name = 'model.activity'
    _inherit=['mail.thread', 'ir.needaction_mixin']
    
    
    activity_state = fields.Selection([('state_waiting',u'Afventer bekræftelse'),
                                    ('state_application',u'Ansøgning'),
                                    ('state_processing',u'Behandles'),
                                    ('state_approved',u'Godkendt'),
                                    ('state_rejected',u'Afvist'),
                                    ('state_locked',u'Låst')],
                                    track_visibility='onchange',
                                    default='state_application')
    
    
    #Activity information
    activity_name = fields.Char(u'Navn på aktivitet',track_visibility='onchange',required=True)
    activity_groupname = fields.Char(u'Gruppenavn',track_visibility='onchange',required=True)
    activity_description = fields.Text(u'Beskrivelse af aktivitet', track_visibility='onchange', required=True)
    activity_participant_usage = fields.Char(u'Hvad får spejderne ud af aktiviteten?',track_visibility='onchange', required=True)
    activity_participant_knowledge = fields.Char(u'Hvad lærer spejderne af aktiviteten?',track_visibility='onchange', required=True)
    
    
    #Contact person 1
    activity_contact1_name = fields.Char(u'Navn',track_visibility='onchange',required=True)
    activity_type = fields.Selection([('type_scout_group',u'Spedjergruppe'),
                                      ('type_organisation',u'Organisation'),
                                      ('type_company',u'Firma'),
                                      ('type_private_person',u'Privatperson'),
                                      ('type_other',u'Andet')]
                                     ,track_visibility='onchange',required=True)
    activity_contact1_road = fields.Char(u'Vej',track_visibility='onchange',required=True)
    activity_contact1_city = fields.Char(u'By',track_visibility='onchange',required=True)
    activity_contact1_zip = fields.Char(u'Postnr',track_visibility='onchange',required=True)
    activity_contact1_email = fields.Char(u'Email',track_visibility='onchange',required=True)
    activity_contact1_tlf = fields.Char(u'Telefon',track_visibility='onchange',required=True)
    
    
    #Target audience
    activity_age_from = fields.Char(u'Minimumsalder for aktivitet',track_visibility='onchange',required=True)
    activity_age_to = fields.Char(u'Maximumsalder for aktivitet',track_visibility='onchange',required=True)
    activity_expected_participants = fields.Selection([('expected_50',u'Under 50'),
                                                       ('expected_50_100',u'50 - 100'),
                                                       ('expected_101_200',u'101 - 200'),
                                                       ('expected_201_350',u'201 - 350'),
                                                       ('expected_351_500',u'351 - 500'),
                                                       ('expected_501_750',u'501 - 750'),
                                                       ('expected_751',u'>750')],
                                                       track_visibility='onchange', required=True)
    
    
    
    
    #Economy
    activity_expense_total = fields.Char(u'Samlet udgift for aktivitet',track_visibility='onchange')
    
    
    #Udvalgsnoter
    activity_note = fields.Text(u'Noter til aktivitet', track_visibility='onchange')
    
    
    
    #BUTTONS
    @api.one
    def btn_activity_confirm(self):
        self.activity_state='state_application'
        
    @api.one
    def btn_activity_process(self):
        self.activity_state='state_processing'
        
    @api.one
    def btn_activity_approve(self):
        self.activity_state='state_approved'
        
    @api.one
    def btn_activity_reject(self):
        self.activity_state='state_rejected'
        
    @api.one
    def btn_activity_lock(self):
        self.activity_state='state_locked'
        
    @api.one
    def btn_activity_open(self):
        self.activity_state='state_application'