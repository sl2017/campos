# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposActivityPeriod(models.Model):

    _name = 'campos.activity.period'
    _description = 'Campos Activity Period'

    name = fields.Char('Name', size=128, translate=True)
    date_begin = fields.Datetime('Start Date/Time', required=True)
    date_end = fields.Datetime('End Date/Time', required=True) 