# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, SUPERUSER_ID, _


from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError

import logging
_logger = logging.getLogger(__name__)

def related_action_generic(session, job):
            model = job.args[0]
            res_id = job.args[1]
            model_obj = session.env['ir.model'].search([('model', '=', model)])
            action = {
                'name': model_obj.name,
                'type': 'ir.actions.act_window',
                'res_model': model,
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': res_id,
            }
            return action

@job(default_channel='root.inv')
@related_action(action=related_action_generic)
def do_delayed_snapshot(session, model, ssreg_id):
    _logger.info("DO SSREG: %d", ssreg_id)
    ssreg = session.env['campos.fee.ss.registration'].browse(ssreg_id)
    if ssreg.exists():
        ssreg.do_delayed_snapshot()



class EventRegistration(models.Model):

    _inherit = 'event.registration'

    number_participants = fields.Integer('Number of participants', compute='_compute_fees', compute_sudo=True)
    number_participants_stored = fields.Integer('# of participants', compute='_compute_fees', compute_sudo=True, store=True)
    number_accomondations = fields.Integer('# accomdation', compute='_compute_fees', compute_sudo=True, store=True)
    fee_participants = fields.Float('Participants Fees', compute='_compute_fees', compute_sudo=True)
    fee_transport = fields.Float('Transport Fee/Refusion', compute='_compute_fees', compute_sudo=True)
    material_cost = fields.Float('Material orders', compute='_compute_fees', compute_sudo=True)
    fee_total = fields.Float('Total Fee', compute='_compute_fees', compute_sudo=True)
    ssreg_ids = fields.One2many('campos.fee.ss.registration', 'registration_id', 'Snapshot')
    ssreginv_ids = fields.One2many('campos.fee.ss.registration', 'registration_id', 'Invoices', domain=[('invoice_id', '!=', False), ('invoice_id.state', 'in', ['open','paid'])])
    cmp_currency_id = fields.Many2one(related='event_id.company_id.currency_id', readonly=True)
    rent_participants = fields.Integer('Number of participants (Campsite Rent)', compute='_compute_fees', compute_sudo=True)
    rent_nights = fields.Integer('Number of Nigths (Campsite Rent)', compute='_compute_fees', compute_sudo=True)
    rent_total = fields.Float('Total Campsite Rent', compute='_compute_fees', compute_sudo=True)

    @api.multi
    @api.depends('participant_ids', 'participant_ids.state', 'participant_ids.staff', 'jobber_accomodation_ids')
    def _compute_fees(self):
        
        for reg in self:
            fee_participants = 0.0
            fee_transport = 0.0
            number_participants = 0
            number_accomondations = 0
            rent_participants = 0
            rent_nights = 0
            rent_total = 0.0
            if self.env.uid == SUPERUSER_ID:
                pars = reg.participant_ids.filtered(lambda r: r.state not in ['cancel', 'deregistered'])
            else:
                pars = reg.participant_ids.suspend_security().filtered(lambda r: r.state not in ['cancel', 'deregistered'])
            for par in pars:
                if not par.sudo().no_invoicing:
                    fee_participants += par.camp_price
                    fee_transport += par.transport_price_total
                    number_participants += 1
                    rent_participants += 1
                    rent_nights += par.nights
                    rent_total += par.rent_price
                if not par.staff:
                    number_accomondations += 1
            number_accomondations += len(reg.jobber_accomodation_ids)
            reg.fee_participants = fee_participants
            reg.fee_transport = fee_transport
            reg.number_participants = number_participants
            reg.number_participants_stored = number_participants
            reg.number_accomondations = number_accomondations
            reg.rent_participants = rent_participants
            reg.rent_nights = rent_nights
            reg.rent_total = rent_total
            _logger.info('Calc # %d %s', number_participants, reg.name)
            so_cost = 0.0
            if self.env.uid == SUPERUSER_ID:
                for so in self.env['sale.order.line'].search([('order_partner_id', '=', reg.partner_id.id),('order_id.state', '!=', 'cancel')]):
                    so_cost += so.price_subtotal
            else:
                for so in self.env['sale.order.line'].suspend_security().search([('order_partner_id', '=', reg.partner_id.id),('order_id.state', '!=', 'cancel')]):
                    so_cost += so.price_subtotal
            reg.material_cost = so_cost
            reg.fee_total = fee_participants + fee_transport + so_cost
            
    @api.multi
    def do_snapshot(self, snapshot):
        _logger.info('SS: %s %d', snapshot, snapshot.id)
        for reg in self:
            ssreg = self.env['campos.fee.ss.registration'].create({'snapshot_id': snapshot.id,
                                                                   'registration_id': reg.id})
            
            session = ConnectorSession.from_env(self.env)
            do_delayed_snapshot.delay(session, 'campos.fee.ss.registration', ssreg.id)
            
#             for par in reg.participant_ids:
#                 par.do_snapshot(ssreg)
#             
#             ssreg.write({'number_participants': reg.number_participants,
#                          'fee_participants': reg.fee_participants,
#                          'fee_transport': reg.fee_transport,
#                          'material_cost': reg.material_cost,
#                          'fee_total': reg.fee_total,
#                          'state': reg.state,
#                          'name': reg.name})
#             if snapshot.execute_func:
#                 func = getattr(ssreg, snapshot.execute_func)
#                 func()

    @api.multi
    def do_instant_snapshot(self, snapshot):
        _logger.info('SS: %s %d', snapshot, snapshot.id)
        for reg in self:
            ssreg = self.env['campos.fee.ss.registration'].create({'snapshot_id': snapshot.id,
                                                                   'registration_id': reg.id})
            ssreg.do_delayed_snapshot()
            
     

    @api.multi
    def assign_group_number(self):
        for reg in self:
            if not reg.partner_id.ref:
                reg.partner_id.ref = self.env['ir.sequence'].next_by_code('group.number')
