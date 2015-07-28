# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of CampOS Event,
#     an Odoo module.
#
#     Copyright (c) 2015 Stein & Gabelgaard ApS
#                        http://www.steingabelgaard.dk
#                        Hans Henrik Gabelgaard
#
#     CampOS Event is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     CampOS Event is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with CampOS Event.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields


class CamposScoutOrg(models.Model):

    """ Scout Organizations"""
    _description = 'Scout Organizations'
    _name = 'campos.scout.org'
    _order = 'name'

    name = fields.Char('Name', size=128)
    country_id = fields.Many2one('res.country', 'Country')
    sex = fields.Char('Sex', size=128)
    worldorg = fields.Selection([('wagggs', 'WAGGGS'),
                                 ('wosm', 'WOSM'),
                                 ('w/w', 'WAGGGS/WOSM'),
                                 ('other', 'Other')], string='World Organization')
