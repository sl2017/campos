# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposActivityInstanse(models.Model):

    _name = 'campos.activity.instanse'
    _description = 'Campos Activity Instanse' 
    _order = 'actins_date_begin'
    
    name = fields.Char('Name', size=128, translate=True)
    seats_max = fields.Integer('Maximum Avalaible Seats')
    seats_hard = fields.Boolean('Hard limit')
    seats_reserved': fields.function(_get_seats, string='Reserved Seats', type='integer', multi='seats_reserved'),
        'seats_available': fields.function(_get_seats, string='Available Seats', type='integer', multi='seats_reserved', fnct_search=_search_seats),
        'seats_used': fields.function(_get_seats, string='Number of Participations', type='integer', multi='seats_reserved'),
        #'complete_name': fields.function(_name_get_fnc, type="char", string='Full Name', multi='seats_reserved'),
    activity_id = fields.Many2one('campos.activity.activity', 'Activity'),
    period_id =  fields.Many2one('campos.activity.period', 'Period'),
    staff_ids = fields.Many2many('campos.event.participant','campos_activity_staff_rel', 'act_ins_id','par_id','Staff')
    ticket_ids = fields.One2many('campos.activity.ticket', 'act_ins_id', 'Tickets')
    actins_date_begin = fields.Datetime(related='period_id.date_begin', string='Start Date/Time', store=True)