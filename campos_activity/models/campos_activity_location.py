# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposActivityLocation(models.Model):

    _name = 'campos.activity.location'
    _description = 'Campos Activity Location'  # TODO

    name = fields.Char(translate=True)
    code = fields.Char('Code', size=20)
    latitude = fields.Float('Geo Latitude', digits=(16, 5))
    longitude =fields.Float('Geo Longitude', digits=(16, 5))

