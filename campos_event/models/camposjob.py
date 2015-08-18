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

from openerp import models, fields, api


class CamposJobTag(models.Model):

    """ Job Tags """
    _description = 'Job Tags'
    _name = 'campos.job.tag'
    _order = 'name'

    name = fields.Char('Name', size=64)
    parent_id = fields.Many2one('campos.job.tag', 'Parent Category', select=True, ondelete='cascade')
    child_ids = fields.One2many('campos.job.tag', 'parent_id', 'Child Categories')
    active = fields.Boolean('Active', help="The active field allows you to hide the category without removing it.", default=True)
    parent_left = fields.Integer('Left parent', select=True)
    parent_right = fields.Integer('Right parent', select=True)
    job_ids = fields.Many2many('campos.job', 'campos_job_tag_rel', 'tag_id', 'job_id', string='Jobs')
    
    _parent_store = True
    _parent_order = 'name'
    
    
    
class CamposJob(models.Model):

    """ Jobs """
    _description = 'Job'
    _name = 'campos.job'
    _order = 'name'
    _inherit = 'mail.thread'

    name = fields.Char('Name', size=64)
    desc = fields.Html('Description')
    active = fields.Boolean('Active', help="The active field allows you to hide the category without removing it.", default=True)
    tag_ids = fields.Many2many('campos.job.tag', 'campos_job_tag_rel', 'job_id', 'tag_id', string='Tags')
    committee_id = fields.Many2one('campos.committee',
                                   'Committee',
                                   ondelete='set null')
    signup_button = fields.Char(default='Signup')
