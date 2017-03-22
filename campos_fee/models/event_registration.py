# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class EventRegistration(models.Model):

    _inherit = 'event.registration'

    number_participants = fields.Integer('Number of participants', compute='_compute_fees')
    fee_participants = fields.Float('Participants Fees', compute='_compute_fees')
    fee_transport = fields.Float('Transport Fee/Refusion', compute='_compute_fees')
    material_cost = fields.Float('Material orders', compute='_compute_fees')
    fee_total = fields.Float('Total Fee', compute='_compute_fees')

    @api.multi
    @api.depends('participant_ids')
    def _compute_fees(self):
        for reg in self:
            fee_participants = 0.0
            fee_transport = 0.0
            number_participants = 0
            for par in reg.participant_ids.filtered(lambda r: r.state not in ['cancel', 'deregistered']):
                fee_participants += par.camp_price
                fee_transport += par.transport_price_total
                number_participants += 1
            reg.fee_participants = fee_participants
            reg.fee_transport = fee_transport
            reg.number_participants = number_participants
            so_cost = 0.0
            for so in self.env['sale.order.line'].search([('order_partner_id', '=', reg.partner_id.id),('order_id.state', '!=', 'cancel')]):
                so_cost += so.price_subtotal
            reg.material_cost = so_cost
            reg.fee_total = fee_participants + fee_transport + so_cost