# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class EventRegistration(models.Model):

    _inherit = 'event.registration'
    
    sale_order_line_ids = fields.One2many('campos.mat.report', 'reg_id')
    
