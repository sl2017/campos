# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposActivityLocation(models.Model):

    _name = 'campos.activity.location'
    _description = 'Campos Activity Location'  # TODO

    name = fields.Char()
