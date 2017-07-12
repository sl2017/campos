# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposCanteenSlot(models.Model):

    _name = 'campos.canteen.slot'
    _description = 'Campos Canteen Slot'  # TODO

    name = fields.Char()
    code = fields.Char()
    meal = fields.Selection([('1breakfast', 'Breakfast'),
                             ('2lunch', 'Lunch'),
                             ('3dinner', 'Dinner')], string='Meal')
