# -*- coding: utf-8 -*-

from openerp import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class CamposCampArea(models.Model):
    _name = 'campos.camp.area'

    name = fields.Char('Name', size=64)
    desc = fields.Text('Description')
    max_cap = fields.Integer('Max')
    event_id = fields.Many2one('event.event', 'Event')
    reg_ids = fields.One2many('event.registration', 'camp_area_id', 'Troops')
    addreg_id = fields.Many2one('event.registration', 'Add Registration', ondelete='set null', domain=[('state','!=', 'cancel')])
    allocated = fields.Integer('Allocated', compute="_compute_allocated")
    
    @api.one
    @api.depends('reg_ids')
    def _compute_allocated(self):
        self.allocated = len(self.reg_ids)   