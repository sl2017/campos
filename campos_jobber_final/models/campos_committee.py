# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposCommittee(models.Model):

    _inherit = 'campos.committee'
    
    camp_area_id = fields.Many2one(
        'campos.camp.area',
        'Camp Area',
        select=True,
        ondelete='set null')
    canteen_id = fields.Many2one('campos.canteen', 'Canteen')
    subcamp_id = fields.Many2one('campos.subcamp', 'Sub Camp')
