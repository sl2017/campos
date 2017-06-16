# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


import logging
_logger = logging.getLogger(__name__)


class CamposEventParticipant(models.Model):

    _inherit = 'campos.event.participant'

    signup_state = fields.Selection([('draft', 'Not signed up'),
                                     ('oncamp', 'Camp Jobber'),
                                     ('dayjobber', 'Day Jobber')], default='draft', string='Final registration', track_visibility='onchange', help='Chose weather you are going to stay at the campsite or not. Must be filled in.')
    accomodation_ids = fields.One2many('campos.jobber.accomodation', 'participant_id', 'Accomodation', help=u'Chose where you would like to stay at the campsite. You may chose between several different locations - but only within the jamboree site. During the pre/post camp everybody is accommodated in Øen.')
    # AS on registration
    canteen_ids = fields.One2many('campos.jobber.canteen', 'participant_id', 'Catering', help=u"Chose where you would like to eat at the campsite. You may chose between several different locations - but only within the jamboree site. During the pre/post camp everybody is catered in Øen.")
    need_ids = fields.Many2many('event.registration.need', string='Special needs', help="Is chosen if you have any kind special needs - or have a caravan with you. See page 20 in the instructions.")
    other_need = fields.Boolean('Other special need(s)')
    other_need_description = fields.Text('Other Need description')
    other_need_update_date = fields.Date('Need updated')
    
    
    paybygroup = fields.Boolean('Pay by Scout Group', help="Is only chosen if you have to pay through a group. See page 21 in the instructions.")
    payreq_state=fields.Selection([('draft', 'In process'),
                                   ('cancelled', 'Cancelled'),
                                   ('approved', 'Approved'),
                                   ('refused', 'Refused')], default='draft', string='Pay Req state', track_visibility='onchange')
    payreq_approved_date = fields.Datetime('Pay Req Approved', track_visibility='onchange')
    payreq_approved_user_id = fields.Many2one('res.users', 'Pay Req Approved By', track_visibility='onchange')
    
    paybyjobber = fields.Boolean('Pay by Other ITS', help="Is only chosen if you have to pay through another ITS. See page 21 in the instructions.")
    pay_key_entered = fields.Char('Code from payer', help='Enter the code the payer has issued you with')
    payforotherjobber = fields.Boolean('Want to pay for others', help="Is only chosen if you want to pay for a group of ITS. See page 21 in the instructions.")
    pay_key_master = fields.Char('Payment Code', help='Enter a code and pass it on to the people ypu want to pay for')
    jobber_pay_for_ids = fields.One2many(related='registration_id.jobber_pay_for_ids')
    exp_child_qu = fields.Integer("Expected number of children in 'Childrens Island'")
    
    ckr_needed = fields.Boolean('CKR Needed',compute='_compute_ckr_needed')
    info_html = fields.Html(compute='_compute_info_html')
    
    # Handle jobbers childs
    jobber_child = fields.Boolean('Jobber Child')
    parent_jobber_id = fields.Many2one('campos.event.participant')
    jobber_child_ids = fields.One2many('campos.event.participant', 'parent_jobber_id')
    car_ids = fields.One2many('campos.event.car','participant_id','Cars')
    
    _sql_constraints = [
                        ('pay_key_master_uniq', 'unique(pay_key_master)', 'Payment Code already in use. Choose another'),
                        ]
    
    @api.constrains('birthdate','jobber_child')
    def _check_jobber_child_age(self):
        if self.jobber_child and self.birthdate < '2002-07-21':
            raise ValidationError("Jobber children must be under 15 years")
        
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
                                       'will_participate':  False,
                                       'the_date': day.event_date,
                                      }))
            self.camp_day_ids = days_ids
        if self.staff and self.birthdate <= '2002-07-30' and self.partner_id.country_id.code == 'DK' and not self.ckr_ids and self.signup_state != 'draft':
            self.ckr_needed = True
            self.info_html = _('CKR Attest Needed. Please Request one')
        else:
            self.ckr_needed = False
            self.info_html = False
        
            
    @api.onchange('staff','birthdate','ckr_ids', 'country_id')
    def onchange_recalc_ckr_needed(self):
        _logger.info('ONCHANGE %s %s %s %s %s', self.ckr_ids, self.birthdate, self.staff, self.country_id.code, (self.staff and self.birthdate and self.birthdate <= '2002-07-30' and self.country_id.code == 'DK' and not self.ckr_ids))
        if self.staff and self.birthdate and self.birthdate <= '2002-07-30' and self.country_id.code == 'DK' and not self.ckr_ids:
            self.ckr_needed = True
            if self.signup_state in ['oncamp','dayjobber']:
                self.info_html = _('CKR Attest Needed. Please Request one')
            else:
                self.info_html = False
        else:
            self.ckr_needed = False
            self.info_html = False
            
    @api.onchange('registration_id')
    def onchange_registration_id(self):
        if self.registration_id.partner_id.id != self.partner_id.id:
            self.payreq_state = 'draft'
        else:
            self.payreq_state = 'approved'

    @api.onchange('paybygroup')
    def onchange_paybygroup(self):
        if not self.paybygroup:
            event_id = self.env['ir.config_parameter'].get_param('campos_welcome.event_id')
            _logger.info('EVent: %s %s', event_id, self.partner_id.id)
            if event_id:
                event_id = int(event_id)
                reg_id = self.env['event.registration'].suspend_security().search([('partner_id', '=', self.partner_id.id), ('event_id', '=', event_id)])
                if reg_id:
                    self.registration_id = reg_id[0]
        else:
            self.payreq_state = 'draft'
             
    @api.onchange('pay_key_entered')
    def onchange_pay_key_entered(self):
        if self.paybyjobber and self.pay_key_entered:
            payer = self.suspend_security().search([('staff', '=', True), ('payforotherjobber', '=', True),('pay_key_master', '=', self.pay_key_entered)])
            if payer:
                self.registration_id = payer.registration_id
                self.payreq_state = 'draft'
            
            
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

    @api.multi
    def check_precamp_wed_fri(self):
        for record in self:
            record.check_camp_days()    
            for day in record.camp_day_ids.filtered(lambda r: r.day_id.event_period == 'precamp' and r.the_date >= '2017-07-19' and r.the_date <= '2017-07-21'):
                day.will_participate = True

    @api.one
    @api.depends('staff','birthdate','ckr_ids','partner_id.country_id')
    def _compute_ckr_needed(self):
        #_logger.info('COMPUTE CKR NEEDED')
        if self.staff and self.birthdate and self.birthdate <= '2002-07-30' and self.partner_id.country_id.code == 'DK' and not self.sudo().ckr_ids:
            self.ckr_needed = True
        else:
            self.ckr_needed = False

    @api.one
    @api.depends('ckr_needed')
    def _compute_info_html(self):
        if self.ckr_needed and self.signup_state in ['oncamp','dayjobber']:
            self.info_html = _('CKR Attest Needed. Please Request one')
        else:
            self.info_html = False
            
    @api.multi
    def action_top_request_ckr(self):
        self.ensure_one
        ckr_id = self.env['campos.ckr.check'].suspend_security().create({'state': 'draft',
                                                                         'participant_id': self.id,
                                                                        })
        return {
            'name': _("Request CKR"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'campos.ckr.fetch.wiz',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'res_id': ckr_id.id,
        }
    
    @api.multi
    def action_request_ckr2(self):
        return self.action_request_own_ckr()
    
    @api.multi
    def write(self, vals):
        res = super(CamposEventParticipant, self).write(vals)
        for cep in self.suspend_security():
            if cep.staff:
                if not cep.paybygroup and not cep.paybyjobber and cep.registration_id.partner_id.id != cep.partner_id.id:
                    event_id = self.env['ir.config_parameter'].get_param('campos_welcome.event_id')
                    _logger.info('EVent: %s %s', event_id, cep.partner_id.id)
                    if event_id:
                        event_id = int(event_id)
                        reg_id = self.env['event.registration'].suspend_security().search([('partner_id', '=', cep.partner_id.id), ('event_id', '=', event_id)])
                        if reg_id:
                            cep.registration_id = reg_id[0]
                            cep.payreq_state = 'approved'
                elif cep.paybygroup and cep.registration_id.partner_id.id != cep.partner_id.parent_id.id and cep.registration_id.partner_id.id != cep.partner_id.id:
                    cep.partner_id.parent_id = cep.registration_id.partner_id
                elif cep.paybyjobber and cep.pay_key_entered and 'pay_key_entered' in vals:
                    payer = cep.suspend_security().search([('staff', '=', True), ('payforotherjobber', '=', True),('pay_key_master', '=', cep.pay_key_entered)])
                    _logger.info('Payer? %s', payer )
                    if payer and cep.registration_id != payer.registration_id:
                        cep.suspend_security().write({'registration_id': payer.registration_id.id,
                                                      'payreq_state': 'draft'})
                    
        return res
    
    @api.multi
    def action_add_jobber_child(self):
        self.ensure_one()
        
        days_ids = []
        for day in self.env['event.day'].search([('event_id', '=', self.registration_id.event_id.id)]):
                days_ids.append((0,0, {'participant_id': self.id,
                                       'day_id': day.id,
                                       'will_participate':  False,
                                       'the_date': day.event_date,
                                      }))
        return {
            'name': _('New child for: %s') % self.name,
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('campos_jobber_final.campos_jobber_child_form_view').id,
            'res_model': 'campos.event.participant',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            #'target': 'new',
            'context' : {'default_registration_id': self.registration_id.id, 
                         'default_street': self.street, 
                         'default_city': self.city, 
                         'default_zip': self.zip, 
                         'default_country_id': self.country_id.id, 
                         'default_jobber_child': True, 
                         'default_parent_id': self.partner_id.id,
                         'default_transport_to_camp': self.transport_to_camp,
                         'default_transport_from_camp': self.transport_from_camp,
                         'defualt_camp_day_ids': days_ids,
                         'default_parent_jobber_id': self.id,
                         }
            }
        
        
    @api.multi
    def action_add_accom_group(self):
        self.ensure_one()
        _logger.info("ADD ACCOM")
        
        return {
            'name': _('New Staff Accomodation Group'),
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('campos_jobber_final.campos_jobber_accom_group_form_view').id,
            'res_model': 'campos.jobber.accom.group',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            #'target': 'new',
            'context' : {
                         'default_owner_id': self.id, 
                         }
            }    