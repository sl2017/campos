# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

import datetime

class CamposActivityTicket(models.Model):

    _name = 'campos.activity.ticket'
    _description = 'Campos Activity Ticket'
    _inherit = 'mail.thread'

    name = fields.Char('Own Note', size=128, help='You can add a Note for own use. It will be shown on activity list etc. I will NOT be read/answered by the Staff.')
    seats = fields.Integer('Seats')
    reserved_time = fields.Datetime('Reserved Date/Time', default=fields.Datetime.now)
    state = fields.Selection([('open', 'Reserved'),
                              ('done', 'Booked'),
                              ('timeout', 'Reservation Expired'),
                              ('cancelled', 'Cancelled')
                             ], 'Ticket State', track_visibility='onchange', default='open'
                            )
    act_ins_id = fields.Many2one('campos.activity.instanse', 'Activity')
    reg_id = fields.Many2one('event.registration', 'Scout Group')
    par_ids = fields.Many2many('campos.event.participant', 'campos_activity_par_rel', 'ticket_id', 'par_id', 'Participants')
    actins_date_begin = fields.Datetime(related='act_ins_id.period_id.date_begin', string='Start Date/Time', store=True, readonly=True)
    actins_date_end = fields.Datetime(related='act_ins_id.period_id.date_end', string='End Date/Time', store=True, readonly=True)
    act_desc = fields.Html(related='act_ins_id.activity_id.desc', string='Description', readonly=True)
    activity_id = fields.Many2one(related='act_ins_id.activity_id', string='Activity')
    allow_edit = fields.Boolean('Allow edit', compute='_compute_allow_edit')

    @api.multi
    def action_unlink_ticket(self):
        self.suspend_security().unlink()

    @api.multi
    def write(self, vals):
        seats_update = False
        if 'state' in vals and vals['state'] in ['done']:
            seats_update = True
        ret = super(CamposActivityTicket, self).write(vals)
        if seats_update:
            for t in self:
                t.seats = len(t.par_ids)
                
        return ret
    
    @api.multi
    def _compute_allow_edit(self):
        for t in self:
            if t.act_ins_id.booking_date_begin <= fields.Datetime.now() and t.act_ins_id.booking_date_end >= fields.Datetime.now():
                t.allow_edit = True
            else:
                t.allow_edit = False 
    
    @api.multi
    def action_cancel_ticket(self):
        self.suspend_security().write({'state': 'cancelled'})
        
    @api.multi
    def action_edit_ticket(self):
        self.ensure_one()
        
        wiz = self.env['campos.activity.signup.wiz'].create({'name': self.name,
                                                             'ticket_id': self.id,
                                                             'act_id': self.activity_id.id,
                                                             'act_ins_id': self.act_ins_id.id,
                                                             'reg_id': self.reg_id.id,
                                                             'seats': self.seats,
                                                             'seats_reserved': self.seats,
                                                             'state': 'step2'})
        return wiz.prepare_step2()
    
    @api.model
    def cancel_expired_reservations(self):
        expired = (datetime.datetime.now() - datetime.timedelta(minutes=30)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        tickets = self.search([('state', '=', 'open'), ('reserved_time', '<', expired)])
        tickets.write({'state': 'timeout'})

