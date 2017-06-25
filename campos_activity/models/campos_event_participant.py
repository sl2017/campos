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
