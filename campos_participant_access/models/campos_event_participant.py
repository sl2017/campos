# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, exceptions, _


class CamposEventParticipant(models.Model):

    _inherit = 'campos.event.participant'

    clc_user_needed = fields.Boolean('CLC User needed', compute='_compute_clc_user_needed')
    
    @api.multi
    def _compute_clc_user_needed(self):
        for p in self:
            p.clc_user_needed = False
            if p.camp_age >= 18 and p.registration_id.group_country_code2 != "DK":
                if not self.env['res.users'].search(['|',('partner_id', '=', self.partner_id.id),('login', '=', self.email)]):
                    p.clc_user_needed = True

    @api.multi
    def action_create_clc_user(self):
        self.ensure_one()
        self.create_clc_user()

    def create_clc_user(self, silent=False):
        if not self.email:
            if silent:
                return
            raise exceptions.Warning(_('Email adress missing for %s') % (self.name))
        if self.env['res.users'].search([('partner_id', '=', self.partner_id.id)]):
            if silent:
                return
            raise exceptions.Warning(_('User already created for %s') % (self.name))
        if self.env['res.users'].search([('login', '=', self.email)]):
            if silent:
                return
            raise exceptions.Warning(_('User already created for this email %s') % (self.email))

        self.partner_id.lang='en_US'
        self.env['res.users'].sudo().with_context(template_ref='campos_participant_access.clc_signup_email').create({'login': self.email,
                                                            'partner_id': self.partner_id.id,
                                                            'groups_id': [(4, self.env.ref('campos_participant_access.group_campos_participant').id)],
                                                         })
