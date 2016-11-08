# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.addons.base_geoengine import geo_model
from openerp.addons.base_geoengine import fields as geo_fields


class CamposSubcamp(geo_model.GeoModel):

    _name = 'campos.subcamp'
    _description = 'Campos Subcamp'  # TODO

    name = fields.Char()
    color = fields.Char('Color')
    the_geom = geo_fields.GeoMultiPolygon('NPA Shape')
    committee_id = fields.Many2one('campos.committee',
                                   'Committee',
                                   ondelete='cascade')
    part_function_ids = fields.One2many(related='committee_id.part_function_ids', string='Coordinators')
    
