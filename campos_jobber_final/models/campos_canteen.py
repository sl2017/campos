# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposCanteen(models.Model):

    _name = 'campos.canteen'
    _description = 'Campos Canteen'  # TODO

    name = fields.Char()
    subcamp_id = fields.Many2one('campos.subcamp', 'Sub camp')
    committee_id = fields.Many2one('campos.committee',
                                   'Committee')
