# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class ResCountry(models.Model):

    _inherit = 'res.country'
    
    visa_req = fields.Boolean('Visa required')
