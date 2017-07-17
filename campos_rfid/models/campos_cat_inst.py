# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposCatInst(models.Model):

    _name = 'campos.cat.inst'
    _description = 'Campos Cat Inst'  # TODO

    name = fields.Char()
    subcamp_id = fields.Many2one('campos.subcamp', 'Subcamp')
    date = fields.Date('Date')
    
    ticket_ids = fields.One2many('campos.cat.ticket', 'cat_inst_id', 'Tickets')
    stat_ids = fields.One2many('campos.cat.stat', 'cat_inst_id', 'Stats')
    
    ticket_no = fields.Integer('Expected', compute='_compute_figures')
    ticket_used = fields.Integer('Scanned', compute='_compute_figures')
    
    @api.multi
    def _compute_figures(self):
        for i in self:
            i.ticket_no = len(i.ticket_ids)
            i.ticket_used = self.env['campos.cat.ticket'].search_count([('cat_inst_id', '=', i.id),('attended_time', '!=', False)])

    @api.multi
    @api.depends('subcamp_id.name', 'date')
    def name_get(self):
        result = []
        for inst in self:
            result.append((inst.id, '%s -  %s' % (inst.subcamp_id.name, inst._fields['date'].convert_to_export(inst.date, inst.env))))
        return result
    
