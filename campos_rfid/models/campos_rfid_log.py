# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposRfidLog(models.Model):

    _name = 'campos.rfid.log'
    _description = 'Campos Rfid Log'  # TODO

    name = fields.Char()
    device_macid = fields.Char('Device ID', help='MAC id')
    pnum = fields.Char('Participant number')
