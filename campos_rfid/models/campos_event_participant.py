# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposEventParticipant(models.Model):

    _inherit = 'campos.event.participant'
    
    canteen_ticket_ids = fields.One2many('campos.canteen.ticket', 'participant_id', 'Canteen Tickets')
    
    def add_update_canteen_ticket(self, day, canteen_id):
        for ci in self.env['campos.canteen.instanse'].search([('date', '=', day.the_date), ('canteen_id', '=', canteen_id.id)]):
            if ci.date == self.tocampdate and ci.meal == 'breakfast':
                continue # No breakfast on arrival date
            if ci.date == self.fromcampdate and ci.meal == 'dinner':
                continue # No dinner on departure date
            tck = self.env['campos.canteen.ticket'].search([('participant_id', '=', self.id), ('date', '=', ci.date), ('meal', '=', ci.meal)])
            if tck:
                if not tck.attended_time:
                    tck.canteen_inst_id = ci
            else:
                self.env['campos.canteen.ticket'].create({'participant_id': self.id,
                                                          'canteen_inst_id': ci.id})
    
    @api.multi
    def generate_canteen_tickets(self):
        pre_post_canteen_id = self.env['campos.canteen'].search([('pre_camp', '=', True)])
        for par in self:
            for day in par.camp_day_ids.filtered('will_participate'):
                if day.day_id.event_period in ['precamp','postcamp']:
                    par.add_update_canteen_ticket(day, pre_post_canteen_id)
                if day.day_id.event_period in ['maincamp']:
                    cjc = par.canteen_ids.filtered(lambda r: r.eat_at == 'canteen' and r.date_from <= day.the_date and r.date_to >= day.the_date)
                    if cjc:
                        par.add_update_canteen_ticket(day, cjc.canteen_id)