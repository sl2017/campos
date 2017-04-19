# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposActivityTag(models.Model):

    _name = 'campos.activity.tag'
    _description = 'Campos Activity Tag'  # TODO

    name = fields.Char()
