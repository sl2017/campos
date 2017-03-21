# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposFeeAgegroup(models.Model):

    _name = 'campos.fee.agegroup'
    _description = 'Campos Fee Agegroup'  # TODO

    name = fields.Char()
    template_id = fields.Many2one('product.template', 'Camp Fee Product')
    transport_tmpl_id = fields.Many2one('product.template', 'Transport Product')
    transport_incl = fields.Boolean('Transport included')
    birthdate_from = fields.Date('Brithdate From')
    birthdate_to = fields.Date('Brithdate To')
    default_group = fields.Boolean('Default Agegroup', help='Used when birthdate is unknown or outside intervals')
    
