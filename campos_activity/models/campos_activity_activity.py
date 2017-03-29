# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposActivityActivity(models.Model):

    _name = 'campos.activity.activity'
    _description = 'Campos Activity Activity'  # TODO

    name = fields.Char()
