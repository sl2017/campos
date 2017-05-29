# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposEventParticipant(models.Model):

    _inherit = 'campos.event.participant'
    
    ckr_ids = fields.One2many('campos.ckr.check', 'participant_id', string='CKR')
    ckr_active_id = fields.Many2one('campos.ckr.check', 'CKR (Active)', compute = '_compute_ckr_active_id', store=True)
    ckr_date_last_state_update = fields.Datetime('CKR Last State change', related='ckr_active_id.date_last_state_update', readonly=True)
    ckr_state = fields.Selection(related='ckr_active_id.state', string='CKR State')
    
    @api.depends('ckr_ids.state', 'ckr_ids.write_date')
    @api.multi
    def _compute_ckr_active_id(self):
        for par in self:
            if par.ckr_ids:
                approved_ids = par.ckr_ids.filtered('appr_date')
                if approved_ids:
                    par.ckr_active_id = approved_ids.sorted(key=lambda r: r.appr_date)[-1]
                else:
                    par.ckr_active_id = par.ckr_ids.sorted(key=lambda r: r.date_last_state_update)[-1]
            else:
                par.ckr_active_id = False
    
    @api.multi 
    def action_request_ckr(self):
        self.ensure_one
        ckr_id = self.env['campos.ckr.check'].suspend_security().create({'state': 'draft',
                                                                         'participant_id': self.id,
                                                                        })
        if self.partner_id.user_ids:
            self.suspend_security().partner_id.user_ids[0].action_id = self.env.ref('campos_ckr.campos_ckr_fetch_wiz_act_window').id
        template = self.env.ref('campos_ckr.template_ckr_request_mail')
        assert template._name == 'email.template'
        return self.action_send_mail(template)

    @api.multi 
    def action_request_own_ckr(self):
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
        
    