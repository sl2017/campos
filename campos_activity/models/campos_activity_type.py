# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposActivityType(models.Model):

    _name = 'campos.activity.type'
    _description = 'Campos Activity Type'  # TODO

    name = fields.Char()
