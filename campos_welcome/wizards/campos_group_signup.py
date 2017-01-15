# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


import logging

_logger = logging.getLogger(__name__)

print "loading Group"

class CamposGroupSignup(models.TransientModel):

    _name = 'campos.group.signup'

    name = fields.Char()
    reg_id = fields.Many2one('event.registration')
    state = fields.Selection([('welcome', 'Welcome to SL2017 Group Preregistration. Please confirm your contact information'),
                               ('edit_group', 'Please Complete your Scout Group Address'),
                               ('edit_econ', 'Please add treasurer information'),
                               ('done', 'Contact information is now completed and the next step is the pre-registration'),
                               ('cancel', 'Cancel')], 'State', default='welcome')
    edit_partner_id = fields.Many2one('res.partner')

    partner_name = fields.Char(related='edit_partner_id.name')
    partner_street = fields.Char(related='edit_partner_id.street')
    partner_street2 = fields.Char(related='edit_partner_id.street2')
    partner_zip = fields.Char(related='edit_partner_id.zip')
    partner_city = fields.Char(related='edit_partner_id.city')
    partner_country_id = fields.Many2one(related='edit_partner_id.country_id')
    partner_email = fields.Char(related='edit_partner_id.email')

    @api.model
    def default_get(self, fields):
        result = super(CamposGroupSignup, self).default_get(fields)
        event_id = self.env['ir.config_parameter'].get_param('campos_welcome.event_id')
        _logger.info('Event: %s', event_id)
        if event_id:
            event_id = int(event_id)
            if self.env.user.partner_id.parent_id: #  and self.env.user.partner_id.parent_id.scoutgroup:
                _logger.info('Event: %d partner: %d', event_id, self.env.user.partner_id.parent_id.id)
                reg = self.env['event.registration'].search([('partner_id', '=', self.env.user.partner_id.parent_id.id), ('event_id', '=', event_id)])
                if reg:
                    result['reg_id'] = reg.id
        result['edit_partner_id'] = self.env.user.partner_id.id
        return result
 
    @api.multi
    def do_reopen_form(self):
        self.ensure_one()
        return {
                'name': _('Welcome to SL2017 Group Registration'),
                'type': 'ir.actions.act_window',
                'res_model': self._name, # this model
                'res_id': self.id, # the current wizard record
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new'}
 
    @api.multi
    def doit_welcome(self):
        for wizard in self:
            wizard.edit_partner_id = wizard.reg_id.partner_id
            wizard.state = 'edit_group'
        return self.do_reopen_form()
 
    @api.multi
    def doit_edit_group(self):
        for wizard in self:
            if not wizard.reg_id.econ_partner_id:
                wizard.reg_id.econ_partner_id = self.env['res.partner'].suspend_security().create({'parent_id': wizard.reg_id.partner_id.id,
                                                                                                   'country_id': self.env.ref('base.dk').id,
                                                                                                   'name': ' '})
            wizard.edit_partner_id = wizard.reg_id.econ_partner_id
            wizard.state = 'edit_econ'
 
        return self.do_reopen_form()
 
    @api.multi
    def doit_edit_econ(self):
        for wizard in self:
            if not wizard.reg_id.partner_id.municipality_id:
                wizard.reg_id.partner_id.geo_localize()
            cse = self.env['campos.subcamp.exception'].search([('name', 'ilike', wizard.reg_id.partner_id.name)])
            vals = {}
            if cse:
                vals['subcamp_id'] = cse.subcamp_id.id
                vals['camp_area_id'] = cse.camp_area_id.id
            elif wizard.reg_id.partner_id.municipality_id.subcamp_id:
                vals['subcamp_id'] = wizard.reg_id.partner_id.municipality_id.subcamp_id.id
                vals['camp_area_id'] = wizard.reg_id.partner_id.municipality_id.camp_area_id.id
            if vals:
                wizard.reg_id.write(vals)
            template = self.env.ref('campos_welcome.treasurer_mail')
            assert template._name == 'email.template'
            try:
                template.send_mail(wizard.reg_id.id)
            except:
                pass
            wizard.state = 'done'
 
        return self.do_reopen_form()
 
    @api.multi
    def doit_done(self):
        self.env.user.action_id = False
        for wizard in self:
            view = self.env.ref('campos_final_registration.view_form_finalregistration_gl')
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'event.registration',
                'res_id': wizard.reg_id.id,  # the current wizard record
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view.id,
                #'target': 'inline',
                }
