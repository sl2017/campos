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
                                   'Canteen Committee', help="Committee operation this Canteen")
    pre_camp = fields.Boolean('Pre Camp', help="This Canteen is open during Pre Camp")
    post_camp = fields.Boolean('Post Camp', help="This Canteen is open during Post Camp")
    max_cap = fields.Integer('Max Capacity pr Meal')
    is_open = fields.Boolean('Can be selected', default=True)
