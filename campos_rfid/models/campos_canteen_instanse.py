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
    meal = fields.Selection([('breakfast', 'Breakfast'),
                             ('lunch', 'Lunch'),
                             ('dinner', 'Dinner')], string='Meal')
    ticket_ids = fields.One2many('campos.canteen.ticket', 'canteen_inst_id', 'Tickets')
    stat_ids = fields.One2many('campos.canteen.stat', 'canteen_inst_id', 'Stats')
    
    ticket_no = fields.Integer('Expected', compute='_compute_figures')
    ticket_used = fields.Integer('Scanned', compute='_compute_figures')
    
    @api.multi
    def _compute_figures(self):
        for i in self:
            i.ticket_no = len(i.ticket_ids)
            i.ticket_used = self.env['campos.canteen.ticket'].search_count([('canteen_inst_id', '=', i.id),('attended_time', '!=', False)])
            
            
