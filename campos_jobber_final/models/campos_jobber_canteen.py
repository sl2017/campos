# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposJobberCanteen(models.Model):

    _name = 'campos.jobber.canteen'
    _description = 'Campos Jobber Canteen'  # TODO

    name = fields.Char()
    participant_id = fields.Many2one('campos.event.participant', 'Participant')
    date_from = fields.Date('From date')
    date_to = fields.Date('To date')
    eat_at = fields.Selection([('group', 'With Scoutgroup'),
                               ('canteen', 'Canteen')], default='canteen', string='Eating')
    canteen_id = fields.Many2one('event.registration', 'Canteen')
    registration_id = fields.Many2one('event.registration', 'Group')
    state = fields.Selection([('draft', 'Draft'),
                              ('cancelled', 'Cancelled'),
                              ('approved', 'Approved'),
                              ('refused', 'Refused')], default='draft', string='State')
    approved_date = fields.Datetime('Approved')
    approved_user_id = fields.Many2one('res.users', 'Approved By')

