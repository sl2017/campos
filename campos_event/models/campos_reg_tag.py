# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposRegTag(models.Model):

    _name = 'campos.reg.tag'
    _description = 'Campos Reg Tag'  # TODO

    name = fields.Char()
