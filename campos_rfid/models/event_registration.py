# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class EventRegistration(models.Model):

    _inherit = 'event.registration'

    catering_note = fields.Text('Catering Note')
    catering_ticket_ids = fields.One2many('campos.cat.ticket', 'registration_id', 'Catering Tickets')

    @api.multi
    def generate_catering_tickets(self):
        _logger.info('CAT TICKETS')
        for reg in self:
            if not reg.catering_ticket_ids:
                for day in self.env['event.day'].search([('event_date', '>=', reg.tocampdate),('event_date', '<=', reg.fromcampdate)]):
                    cat_inst = self.env['campos.cat.inst'].search([('subcamp_id', '=', reg.subcamp_id.id),('date','=', day.event_date)])
                    _logger.info('DAY: %s INST %s', day.event_date, cat_inst)
                    tck = self.env['campos.cat.ticket'].create({'registration_id': reg.id,
                                                                'cat_inst_id': cat_inst.id})
                    _logger.info('GEN: %s', tck)
                    meatlist = self.env['event.registration.meatlist'].search([('registration_id', '=', reg.id),('event_date','=', day.event_date)])
                    if meatlist:
                        _logger.info('MEAT: %s', meatlist)
                        meatlist.write({'ticket_id': tck.id})