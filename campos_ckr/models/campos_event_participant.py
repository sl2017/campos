# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposEventParticipant(models.Model):

    _inherit = 'campos.event.participant'
    
    ckr_ids = fields.One2many('campos.ckr.check', 'participant_id', string='CKR')
