# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposEventCar(models.Model):

    _inherit = 'campos.event.car'
    _rec_name = 'reg_number'
    
    registration_id  = fields.Many2one('event.registration', 'Registration', required=False)
    participant_id = fields.Many2one('campos.event.participant', 'Participant')
    
    _sql_constraints = [
                        ('participant_uniq', 'unique(participant_id)', 'Only ONE Car Ticket pr person.'),
                        ]
    
    