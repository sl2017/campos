# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class EventDayMeat(models.Model):

    _inherit = 'event.day.meat'
    
    pck_pr_par = fields.Float('Packs pr. Participant')
    