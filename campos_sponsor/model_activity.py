# -*- coding: utf-8 -*-
from openerp import models, fields, api

class ActivityMain(models.Model):
    _name = 'model.activity'
    _inherit=['mail.thread', 'ir.needaction_mixin']
    
    
    activity_state = fields.Selection([('state_waiting',u'Afventer bekræftelse'),
                                    ('state_application',u'Ansøgning'),
                                    ('state_processing','Behandles'),
                                    ('state_approved','Godkendt'),
                                    ('state_rejected','Afvist'),
                                    ('state_locked',u'Låst')],
                                    track_visibility='onchange',
                                    default='state_application')
    
    
    #Activity information
    activity_name = fields.Char('Navn på aktivitet',track_visibility='onchange',required=True)
    activity_groupname = fields.Char('Gruppenavn',track_visibility='onchange',required=True)
    activity_description = fields.Text('Beskrivelse af aktivitet', track_visibility='onchange', required=True)
    activity_participant_usage = fields.Char(u'Hvad får spejderne ud af aktiviteten?',track_visibility='onchange', required=True)
    activity_participant_knowledge = fields.Char(u'Hvad lærer spejderne af aktiviteten?',track_visibility='onchange', required=True)
    
    
    #Contact person 1
    activity_contact1_name = fields.Char('Navn',track_visibility='onchange',required=True)
    activity_type = fields.Selection([('type_scout_group','Spedjergruppe'),
                                      ('type_organisation','Organisation'),
                                      ('type_company','Firma'),
                                      ('type_private_person','Privatperson'),
                                      ('type_other','Andet')]
                                     ,track_visibility='onchange',required=True)
    activity_contact1_road = fields.Char('Vej',track_visibility='onchange',required=True)
    activity_contact1_city = fields.Char('By',track_visibility='onchange',required=True)
    activity_contact1_zip = fields.Char('Postnr',track_visibility='onchange',required=True)
    activity_contact1_email = fields.Char('Email',track_visibility='onchange',required=True)
    activity_contact1_tlf = fields.Char('Telefon',track_visibility='onchange',required=True)
    
    
    #Target audience
    activity_age_from = fields.Char('Minimumsalder for aktivitet',track_visibility='onchange',required=True)
    activity_age_to = fields.Char('Maximumsalder for aktivitet',track_visibility='onchange',required=True)
    activity_expected_participants = fields.Selection([('expected_50','Under 50'),
                                                       ('expected_50_100','50 - 100'),
                                                       ('expected_101_200','101 - 200'),
                                                       ('expected_201_350','201 - 350'),
                                                       ('expected_351_500','351 - 500'),
                                                       ('expected_501_750','501 - 750'),
                                                       ('expected_751','>750')],
                                                       track_visibility='onchange', required=True)
    
    
    
    
    #Economy
    activity_expense_total = fields.Char('Samlet udgift for aktivitet',track_visibility='onchange')
    
    
    #Udvalgsnoter
    activity_note = fields.Text('Noter til aktivitet', track_visibility='onchange')
    
    
    
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