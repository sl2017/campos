# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposCanteenInstanse(models.Model):

    _name = 'campos.canteen.instanse'
    _description = 'Campos Canteen Instanse'  # TODO

    name = fields.Char()
    canteen_id = fields.Many2one('campos.canteen', 'Canteen')
    date = fields.Date('Date')
    meal = fields.Selection([('1breakfast', 'Breakfast'),
                             ('2lunch', 'Lunch'),
                             ('3dinner', 'Dinner')], string='Meal')
    ticket_ids = fields.One2many('campos.canteen.ticket', 'canteen_inst_id', 'Tickets')
    stat_ids = fields.One2many('campos.canteen.stat', 'canteen_inst_id', 'Stats')
    
    ticket_no = fields.Integer('Expected', compute='_compute_figures')
    ticket_used = fields.Integer('Scanned', compute='_compute_figures')
    
    @api.multi
    def _compute_figures(self):
        for i in self:
            i.ticket_no = len(i.ticket_ids)
            i.ticket_used = self.env['campos.canteen.ticket'].search_count([('canteen_inst_id', '=', i.id),('attended_time', '!=', False)])

    @api.multi
    @api.depends('canteen_id', 'date', 'meal')
    def name_get(self):
        result = []
        for inst in self:
            result.append((inst.id, '%s - %s - %s' % (inst.canteen_id.name, inst._fields['meal'].convert_to_export(inst.meal, inst.env), inst._fields['date'].convert_to_export(inst.date, inst.env))))
        return result
    
    @api.model
    def generate_instanses(self):
        for day in self.env['event.day'].search([('event_id', '=', 1)]):
            domain = []
            if day.event_period == 'precamp':
                domain = [('pre_camp', '=', True)]
            if day.event_period == 'postcamp':
                domain = [('post_camp', '=', True)]

            for c in self.env['campos.canteen'].search(domain):
                for meal in ['1breakfast', '2lunch', '3dinner']:
                    self.env['campos.canteen.instanse'].create({'canteen_id': c.id,
                                                                'date': day.event_date,
                                                                'meal': meal,
                                                                })
