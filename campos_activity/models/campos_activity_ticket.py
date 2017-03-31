# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposActivityTicket(models.Model):

    _name = 'campos.activity.ticket'
    _description = 'Campos Activity Ticket'  # TODO

    name = fields.Char('Own Note', size=128, help='You can add a Note for own use. It will be shown on activity list etc. I will NOT be read/answered by the Staff.')
    seats = fields.Integer('Seats')
    reserved_time = fields.Datetime('Reserved Date/Time')
    state = fields.Selection([('open', 'Reserved'),
                              ('done', 'Booked'),
                              ('timeout', 'TimeOut'),
                             ], 'Ticket State'
                            )
    act_ins_id = fields.Many2one('campos.activity.instanse', 'Activity')
    reg_id = fields.Many2one('event.registration', 'Scout Group')
    par_ids = fields.Many2many('campos.event.participant', 'campos_activity_par_rel', 'ticket_id', 'par_id', 'Participants')
    actins_date_begin = fields.Datetime(related='act_ins_id.period_id.date_begin', string='Start Date/Time', store=True)
    act_desc = fields.Text(related='act_ins_id.activity_id.desc', string='Description')
