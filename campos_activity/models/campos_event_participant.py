# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposEventParticipant(models.Model):

    _inherit = 'campos.event.participant'
    
    ticket_ids = fields.Many2many('campos.activity.ticket', 'campos_activity_par_rel', 'par_id', 'ticket_id', 'Activity Tickets', domain=[('state', '=', 'done')])
