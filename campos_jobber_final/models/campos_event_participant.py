# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposEventParticipant(models.Model):

    _inherit = 'campos.event.participant'

    signup_state = fields.Selection([('draft', 'Not signed up'),
                                     ('oncamp', 'Camp Jobber'),
                                     ('dayjobber', 'Day Jobber')], default='draft', string='Final registration', track_visibility='onchange')
    accomodation_ids = fields.One2many('campos.jobber.accomodation', 'participant_id', 'Accomodation')
    # AS on registration
    canteen_ids = fields.One2many('campos.jobber.canteen', 'participant_id', 'Catering')
    need_ids = fields.Many2many('event.registration.need', string='Special needs')
    other_need = fields.Boolean('Other special need(s)')
    other_need_description = fields.Text('Other Need description')
    other_need_update_date = fields.Date('Need updated')
    paybygroup = fields.Boolean('Pay by Scout Group')
    payreq_state=fields.Selection([('draft', 'Draft'),
                                   ('cancelled', 'Cancelled'),
                                   ('approved', 'Approved'),
                                   ('refused', 'Refused')], default='draft', string='Pay Req state', track_visibility='onchange')
    payreq_approved_date = fields.Datetime('Pay Req Approved', track_visibility='onchange')
    payreq_approved_user_id = fields.Many2one('res.users', 'Pay Req Approved By', track_visibility='onchange')
    exp_child_qu = fields.Integer("Expected number of children in 'Childrens Island'")
    
    @api.multi
    def action_approve_payreq(self):
        self.write({'payreq_state': 'approved'})
        
    @api.multi
    def action_refuse_payreq(self):
        self.write({'payreq_state': 'refused'})
        
    @api.onchange('signup_state')
    def onchange_signup_state(self):
        if self.signup_state != 'draft':
            self.transport_to_camp = False
            self.transport_from_camp = False
        if self.registration_id.partner_id.id == self.partner_id.id:
            self.payreq_state = 'approved'
        if not self.camp_day_ids:
            days_ids = []
            for day in self.env['event.day'].search([('event_id', '=', self.registration_id.event_id.id)]):
                days_ids.append((0,0, {'participant_id': self.id,
                                       'day_id': day.id,
                                       'will_participate': True if day.event_period == 'maincamp' else False,
                                       'the_date': day.event_date,
                                      }))
            self.camp_day_ids = days_ids
    
    @api.onchange('registration_id')
    def onchange_registration_id(self):
        if self.registration_id.partner_id.id != self.partner_id.id:
            self.payreq_state = 'draft'
        else:
            self.payreq_state = 'approved'

    @api.onchange('paybygroup')
    def onchange_paybygroup(self):
        if not self.paybygroup:
            self.registration_id = self.env['event.registration'].search([('partner_id', '=', self.partner_id.id)])
            
    @api.multi
    def check_all_precamp_days(self):
        for record in self:
            record.check_camp_days()
            for day in record.camp_day_ids.filtered(lambda r: r.day_id.event_period == 'precamp'):
                day.will_participate = True
                
    @api.multi
    def check_all_postcamp_days(self):
        for record in self:
            record.check_camp_days()
            for day in record.camp_day_ids.filtered(lambda r: r.day_id.event_period == 'postcamp'):
                day.will_participate = True
