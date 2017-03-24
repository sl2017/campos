# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposFeeSsRegistration(models.Model):

    _name = 'campos.fee.ss.registration'
    _description = 'Campos Fee Ss Registration'  # TODO

    name = fields.Char()
    
    snapshot_id = fields.Many2one('campos.fee.snapshot', 'Snapshot')
    registration_id = fields.Many2one('event.registration', 'Registration')
    sspar_ids = fields.One2many('campos.fee.ss.participant', 'ssreg_id', 'Snapshot')
    
    #Mirrored from the Group Registration
    state = fields.Selection([
        ('draft', 'Unconfirmed'),
        ('cancel', 'Cancelled'),
        ('open', 'Confirmed'),
        ('done', 'Attended'),
        ('deregistered', 'Deregistered')
        ], string='Status')
    number_participants = fields.Integer('Number of participants')
    fee_participants = fields.Float('Participants Fees')
    fee_transport = fields.Float('Transport Fee/Refusion')
    material_cost = fields.Float('Material orders')
    fee_total = fields.Float('Total Fee')
