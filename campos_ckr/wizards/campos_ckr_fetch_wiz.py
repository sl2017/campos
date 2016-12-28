# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, exceptions, _


class CamposCkrFetchWiz(models.TransientModel):

    _name = 'campos.ckr.fetch.wiz'

    @api.model
    def default_get(self, fields):
        result = super(CamposCkrFetchWiz, self).default_get(fields)
        result['participant_id'] = self.env.user.participant_id.id

        ckr_ids = self.env['campos.ckr.check'].search([('participant_id', '=', self.env.user.participant_id.id),('state', '=', 'draft')])
        if ckr_ids:
            result['ckr_id'] = ckr_ids[0].id

        return result

    ckr_id = fields.Many2one('campos.ckr.check')
    participant_id = fields.Many2one('campos.event.participant')
    name = fields.Char(related='participant_id.partner_id.name')
    birthdate = fields.Date(related='participant_id.birthdate', string='Date of birth')
    birthdate_short = fields.Char(related='participant_id.birthdate_short')
    cpr = fields.Char('CPR', size=4)  # Last 4 digits of the Danish social security number

    @api.constrains('cpr')
    def _check_description(self):
        if self.cpr and not (len(self.cpr) == 4 and self.cpr.isdigit()):
            raise exceptions.ValidationError("CPR number must be 4 digits")
        
    @api.multi
    def doit(self):
        for wizard in self:
            if wizard.ckr_id:
                wizard.ckr_id.suspend_security().write({'cpr' : wizard.cpr,
                                                       'state': 'sentin',
                                                       })
            else:
                wizard.ckr_id = self.env['campos.ckr.check'].suspend_security().create({'cpr' : wizard.cpr,
                                                                                        'state': 'sentin',
                                                                                        'participant_id': wizard.participant_id.id,
                                                                                        })
        self.env.user.action_id = False

        return self.env['warning_box'].info(title=_('Thank you'), message=_('Your CKR request will be processed and you can expect a message in E-Boks soon.'))
