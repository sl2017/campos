# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposFeeSsRegMeat(models.Model):

    _name = 'campos.fee.ss.reg.meat'
    _description = 'Campos Fee Ss Reg Meat'
    
    ssreg_id = fields.Many2one('campos.fee.ss.registration', 'Snapshot Reg')
    event_day_meat_id = fields.Many2one('event.day.meat','Meat type choice', required=True)
    meat_count = fields.Integer('Count', required=True)
