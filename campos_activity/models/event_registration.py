# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class EventRegistration(models.Model):

    _inherit = 'event.registration'

    ticket_ids = fields.One2many('campos.activity.ticket', 'reg_id', 'Activity tickets')

    @api.multi
    def action_add_activity(self):
        self.ensure_one()

        return {
            'name': _('New activity signup for: %s') % self.name,
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('campos_activity.campos_activity_signup_wiz_form_view').id,
            'res_model': 'campos.activity.signup.wiz',
            'type': 'ir.actions.act_window',
            #'nodestroy': True,
            'target': 'new',
            'context' : {
                         'default_reg_id': self.id, 
                         },
            }
        
    @api.multi
    def action_activity_calendar(self):
        self.ensure_one()
        return {
                'name': _("Activities for %s" % self.name),
                'view_mode': 'calendar,tree,form',
                'view_type': 'form',
                'res_model': 'campos.activity.ticket',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'domain': [('reg_id', '=', self.id)],
            }
