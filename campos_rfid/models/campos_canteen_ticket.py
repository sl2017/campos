# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposCanteenTicket(models.Model):

    _name = 'campos.canteen.ticket'
    _description = 'Campos Canteen Ticket'  # TODO
    
    def _get_slots(self):
        slots = [('-', 'Missing')]
        for s in [(str(i / 60) if i / 60 > 9 else "0" + str(i / 60)) + ":" + (str(i % 60) if i % 60 > 9 else "0" + str(i % 60)) for i in xrange(0, 1440, 30)]:
            slots.append((s.replace(':', ''), s))

        return slots
    
    _sql_con_sql_constraints = [
        ('ticket_unique',
         'unique(participant_id,date,meal)',
         'The ticket needs to be unique')
    ]

    name = fields.Char()
    canteen_inst_id = fields.Many2one('campos.canteen.instanse', 'Canteen Instanse')
    canteen_id = fields.Many2one(related='canteen_inst_id.canteen_id', store=True)
    participant_id = fields.Many2one('campos.event.participant')
    date = fields.Date(related='canteen_inst_id.date', store=True)
    meal = fields.Selection(related='canteen_inst_id.meal', store=True)
    attended_time = fields.Datetime('Attended')
    attended_slot = fields.Selection(_get_slots, string='Bucket', default = '-')
    
