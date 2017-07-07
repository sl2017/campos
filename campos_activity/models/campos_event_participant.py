# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposEventParticipant(models.Model):

    _inherit = 'campos.event.participant'
    
    ticket_ids = fields.Many2many('campos.activity.ticket', 'campos_activity_par_rel', 'par_id', 'ticket_id', 'Activity Tickets', domain=[('state', '=', 'done')])
    
    def is_on_camp(self, act_ins):
        if self.state in ['reg', 'duplicate', 'deregistered']:
            return False
        dt = act_ins.period_id.date_begin[0:10]
        if dt < self.tocampdate or dt > self.fromcampdate:
            return False
        return True

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
                         'default_reg_id': self.registration_id.id,
                         'default_par_id': self.id 
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
                'domain': [('par_ids', 'in', [self.id])],
            }
