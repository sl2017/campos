# -*- coding: utf-8 -*-
from openerp import models, fields, api

class ActivityMain(models.Model):
    _name = 'model.activity'
    _inherit=['mail.thread', 'ir.needaction_mixin']
    
    
    activity_state = fields.Selection([('state_waiting','Awaiting confirmation'),
                                    ('state_application','Application'),
                                    ('state_processing','Processing'),
                                    ('state_approved','Approved'),
                                    ('state_rejected','Rejected'),
                                    ('state_locked','Locked')],
                                    track_visibility='onchange',
                                    default='state_application')
    
    
    #Activity name
    activity_name = fields.Char('Activity name',track_visibility='onchange',required=True)
    
    
    #Contact information
    activity_groupname = fields.Char('Group name',track_visibility='onchange',required=True)
    #Contact person 1
    activity_contact1_name = fields.Char('Name',track_visibility='onchange',required=True)
    activity_contact1_road = fields.Char('Road',track_visibility='onchange',required=True)
    activity_contact1_city = fields.Char('City',track_visibility='onchange',required=True)
    activity_contact1_zip = fields.Char('ZIP',track_visibility='onchange',required=True)
    activity_contact1_email = fields.Char('Email',track_visibility='onchange',required=True)
    activity_contact1_tlf = fields.Char('Phone',track_visibility='onchange',required=True)
    #Contact person 2
    activity_contact2_name = fields.Char('Contact 2 - name',track_visibility='onchange',required=False)
    activity_contact2_road = fields.Char('Road',track_visibility='onchange',required=True)
    activity_contact2_city = fields.Char('City',track_visibility='onchange',required=True)
    activity_contact2_zip = fields.Char('ZIP',track_visibility='onchange',required=True)
    activity_contact2_email = fields.Char('Contact 2 - Email',track_visibility='onchange',required=False)
    activity_contact2_tlf = fields.Char('Contact 2 - Tlf. number',track_visibility='onchange',required=False)
    
    
    #Activity hours
    activity_open_sunday = fields.Char('Opening hours sunday',track_visibility='onchange',required=False)
    activity_open_monday = fields.Char('Opening hours monay',track_visibility='onchange',required=False)
    activity_open_tuesday = fields.Char('Opening hours tuesday',track_visibility='onchange',required=False)
    activity_open_wednesday = fields.Char('Opening hours wednesday',track_visibility='onchange',required=False)
    activity_open_thursday = fields.Char('Opening hours thursday',track_visibility='onchange',required=False)
    activity_open_friday = fields.Char('Opening hours friday',track_visibility='onchange',required=False)
    
    
    #Activy information
    activity_age = fields.Char('Age group for activity',track_visibility='onchange',required=True)
    activity_capacity_day = fields.Char('Amount of scouts per day',track_visibility='onchange',required=True)
    activity_expense_total = fields.Char('Total expense for activity',track_visibility='onchange',required=True)
    activity_expense_scout = fields.Char('Total expense per scout',track_visibility='onchange',required=True)
    
    
    #Filled in by
    activity_filled = fields.Char('Filled in by',track_visibility='onchange',required=True)
    
    
    
    #BUTTONS
    @api.one
    def btn_activity_confirm(self):
        self.partner_state='state_application'
        
    @api.one
    def btn_activity_process(self):
        self.partner_state='state_processing'
        
    @api.one
    def btn_activity_approve(self):
        self.partner_state='state_approved'
        
    @api.one
    def btn_activity_reject(self):
        self.partner_state='state_rejected'
        
    @api.one
    def btn_activity_lock(self):
        self.partner_state='state_locked'
        
    @api.one
    def btn_activity_open(self):
        self.partner_state='state_application'