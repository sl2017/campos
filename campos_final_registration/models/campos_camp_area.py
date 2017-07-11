# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposCampArea(models.Model):

    _inherit = 'campos.camp.area'
    
    pole_depot_id = fields.Many2one('event.registration.pioneeringpoledepot', 'Pole depot')
