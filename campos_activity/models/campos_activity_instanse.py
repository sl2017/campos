# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import Warning

class CamposActivityInstanse(models.Model):

    _name = 'campos.activity.instanse'
    _description = 'Campos Activity Instanse' 
    _order = 'actins_date_begin'
    _inherit = 'mail.thread'
    
    name = fields.Char('Name', size=128, translate=True)
    seats_max = fields.Integer('Maximum Avalaible Seats')
    seats_hard = fields.Boolean('Hard limit')
    seats_reserved = fields.Integer('Reserved Seats', compute='_compute_seats')
    seats_available = fields.Integer('Available Seats', compute='_compute_seats')
    seats_used = fields.Integer('Number of Participations', compute='_compute_seats')
    ticket_ids = fields.One2many('campos.activity.ticket', 'act_ins_id', 'Tickets')
    
    #'complete_name': fields.function(_name_get_fnc, type="char", string='Full Name', multi='seats_reserved'),
    activity_id = fields.Many2one('campos.activity.activity', 'Activity')
    act_code = fields.Char(related='activity_id.code', readonly=True)
    period_id = fields.Many2one('campos.activity.period', 'Period')
    staff_ids = fields.Many2many('campos.event.participant','campos_activity_staff_rel', 'act_ins_id','par_id','Staff', domain=[('staff', '=', True)])
    #ticket_ids = fields.One2many('campos.activity.ticket', 'act_ins_id', 'Tickets')
    actins_date_begin = fields.Datetime(related='period_id.date_begin', string='Start Date/Time', store=True)
    actins_date_end = fields.Datetime(related='period_id.date_end', string='End Date/Time', store=True)
    location_id = fields.Many2one('campos.activity.location', 'Location')
    booking = fields.Selection([('dropin', 'Drop In'),
                                # ('dropin_prebook', 'Drop In & Pre Booking'),
                                ('dropin_at_time', 'Dropin at time'),
                                ('precamp', 'Pre Camp Booking Required'),
                                ('prebook', 'Booking required'),
                                ('joint', 'Joint arrangement')], 'Booking')
    booking_date_begin = fields.Datetime('Booking opens')
    booking_date_end = fields.Datetime('Booking closes')
    
    state = fields.Selection([('open', 'Open'),
                                ('cancelled', 'Cancelled'),
                                ('canc_weather', 'Cancelled due to weather'),
                                ('canc_risk', 'At risk of cancellation due to weather conditions')], 'State', default='open', track_visibility='onchange')
    
    @api.multi
    def unlink(self):
        if any(act.ticket_ids for act in self):
            raise Warning(_('You can only delete unused instanse! You need to Cancel it.'))
        return super(CamposActivityInstanse, self).unlink()
        
    @api.multi
    def write(self, vals):
        cancel = False
        if 'state' in vals and vals['state'] in ['cancelled', 'canc_weather']:
            cancel = True
        ret = super(CamposActivityInstanse, self).write(vals)
        if cancel:
            for ai in self:
                ai.ticket_ids.write({'state': 'cancelled'})
        
        return ret
    
    
    @api.onchange('activity_id','period_id')
    def on_change_actper(self):
        if self.activity_id and self.period_id:
            self.name = '%s - %s' % (self.activity_id.display_name, self.period_id.display_name)

    @api.depends('ticket_ids')
    @api.multi
    def _compute_seats(self):
        res = {}
        state_field = {
                'open':'seats_reserved',
                'done': 'seats_used',
            }
        where_params = [tuple(self.ids)]
        self._cr.execute("""SELECT act_ins_id, state, SUM(seats)
                      FROM campos_activity_ticket
                      WHERE act_ins_id IN %s
                      GROUP BY act_ins_id, state
                      """, where_params)
        for aid, state, val in self._cr.fetchall():
            if state in state_field.keys():
                ai = self.browse(aid)
                ai[state_field[state]] = val
        
        for a in self:    
            a.seats_available = a.seats_max - (a.seats_used + a.seats_reserved) if a.seats_max > 0 else None
                
    @api.multi
    @api.depends('name', 'seats_available')
    def name_get(self):
        result = []
        for ai in self:
            if ai.seats_available <= 0:
                result.append((ai.id, '%s - No available seats' % (ai.name)))
            else:
                result.append((ai.id, '%s - Available seats: %d' % (ai.name, ai.seats_available)))
        return result
    
    