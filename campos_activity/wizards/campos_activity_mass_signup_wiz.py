# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposActivityMassSignupWiz(models.TransientModel):
    _name = 'campos.activity.mass.signup.wiz'

    @api.model
    def _default_reg_ids(self):
        res = False
        context = self.env.context
        if (context.get('active_model') == 'event.registration' and
                context.get('active_ids')):
            res = context['active_ids']
        return res

    
    act_ins_id = fields.Many2one('campos.activity.instanse', 'Activity')
    reg_ids = fields.Many2many(comodel_name='event.registration',
                               string='Registrations',
                               default=_default_reg_ids)
    age_from =  fields.Integer('Age from', default=0, track_visibility='onchange')
    age_to = fields.Integer('Age to', default=99, track_visibility='onchange')
    

    @api.multi
    def doit(self):
        for wizard in self:
            for reg in wizard.reg_ids:
                par_ids = reg.participant_ids.filtered(lambda p: p.camp_age >= wizard.age_from and p.camp_age <= wizard.age_to)
                if par_ids:
                    ticket = self.env['campos.activity.ticket'].create({'act_ins_id': wizard.act_ins_id.id,
                                                                        'state': 'done',
                                                                        'seats': len(par_ids),
                                                                        'reg_id': reg.id})
                    ticket.par_ids = par_ids
