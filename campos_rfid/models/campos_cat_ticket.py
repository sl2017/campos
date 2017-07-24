# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposCatTicket(models.Model):

    _name = 'campos.cat.ticket'
    _description = 'Campos Cat Ticket'  # TODO
    _inherit = 'mail.thread'

    def _get_slots(self):
        slots = [('-', 'Missing')]
        for s in [(str(i / 60) if i / 60 > 9 else "0" + str(i / 60)) + ":" + (str(i % 60) if i % 60 > 9 else "0" + str(i % 60)) for i in xrange(0, 1440, 30)]:
            slots.append((s.replace(':', ''), s))

        return slots
    
    _sql_con_sql_constraints = [
        ('ticket_unique',
         'unique(registration_id,date)',
         'The ticket needs to be unique')
    ]

    name = fields.Char()
    cat_inst_id = fields.Many2one('campos.cat.inst', 'Catering Instanse')
    subcamp_id = fields.Many2one(related='cat_inst_id.subcamp_id', store=True)
    registration_id = fields.Many2one('event.registration', 'Group')
    participant_id = fields.Many2one('campos.event.participant', 'Pick up by', track_visibility='onchange')
    date = fields.Date(related='cat_inst_id.date', store=True)
    attended_time = fields.Datetime('Attended')
    attended_slot = fields.Selection(_get_slots, string='Bucket', default = '-')
    responce = fields.Html('Response')
    responce_status = fields.Boolean('Responce status')
    meat_ids = fields.One2many('event.registration.meatlist', 'ticket_id', 'Meat list')
    state = fields.Selection([('draft', 'Not delivered'),
                              ('open', 'Partly delivered'),
                              ('done', 'Completed')], string='State', default='draft', track_visibility='onchange')
    catering_note = fields.Text(related='registration_id.catering_note', string='Group Note')
    ticket_note = fields.Text('Todays Note', track_visibility='onchange')
    device_id = fields.Many2one('campos.rfid.device', 'Scanner')
    
    
    @api.multi
    @api.depends('registration_id.name', 'date')
    def name_get(self):
        result = []
        for inst in self:
            result.append((inst.id, '%s -  %s' % (inst.registration_id.name, inst._fields['date'].convert_to_export(inst.date, inst.env))))
        return result
    

