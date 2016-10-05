# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.addons.base_geoengine import geo_model
from openerp.addons.base_geoengine import fields as geo_fields

import logging
_logger = logging.getLogger(__name__)

class CamposCampArea(geo_model.GeoModel):
    _description = 'Camp Area'
    _name = 'campos.camp.area'
    
    name = fields.Char('Name', size=64)
    code = fields.Char('Code', size=16)
    desc = fields.Text('Description')
    max_cap = fields.Integer('Max')
    event_id = fields.Many2one('event.event', 'Event')
    reg_ids = fields.One2many('event.registration', 'camp_area_id', 'Troops')
    addreg_id = fields.Many2one('event.registration', 'Add Registration', ondelete='set null', domain=[('state','!=', 'cancel')])
    allocated = fields.Integer('Allocated', compute="_compute_allocated")
    subcamp_id = fields.Many2one('campos.subcamp', 'Sub Camp')
    the_geom = geo_fields.GeoMultiPolygon('NPA Shape')
    
    @api.one
    @api.depends('reg_ids')
    def _compute_allocated(self):
        self.allocated = len(self.reg_ids)   