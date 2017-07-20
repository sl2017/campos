# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class EventRegistration(models.Model):

    _inherit = 'event.registration'

    catering_note = fields.Text('Catering Note')
    catering_ticket_ids = fields.One2many('campos.cat.ticket', 'registration_id', 'Catering Tickets')
    
    @api.multi
    def generate_catering_tickets(self):
        for reg in self:
            if not reg.catering_ticket_ids:
                for day in self.env['event.day'].search([('event_date', '>=', reg.tocampdate),('event_date', '>=', reg.fromcampdate)]):
                    cat_inst = self.env['campos.cat.inst'].search([('subcamp_id', '=', reg.subcamp_id),('date','=', day.event_date)])
                    tck = self.env['campos.cat.ticket'].create({'regisstration_id': reg.id,
                                                                'cat_inst_id': cat_inst.id})
                    meatlist = self.env['event.registration.meatlist'].search([('registration_id', '=', reg.id),('event_date','=', day.event_date)])
                    if meatlist:
                        meatlist.write({'ticket_id': tck.id})