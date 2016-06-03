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
from openerp.tools.translate import _



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
    teaser = fields.Char('Teaser', size=128)
    desc = fields.Html('Description')
    active = fields.Boolean('Active', help="The active field allows you to hide the category without removing it.", default=True)
    tag_ids = fields.Many2many('campos.job.tag', 'campos_job_tag_rel', 'job_id', 'tag_id', string='Tags')
    committee_id = fields.Many2one('campos.committee',
                                   'Committee',
                                   ondelete='set null')
    signup_button = fields.Char(default='Signup')
    
    job_where = fields.Char('Where')
    job_when = fields.Char('When')
    min_qty_jobbere = fields.Integer('Minimum numbers of staff')
    wanted_qty_jobbere = fields.Integer('Wanted numbers of staff')
    max_qty_jobbere = fields.Integer('Maximun numbers of staff')
    
    date_public = fields.Date('Publication at')
    date_closing = fields.Date('Close at')
    
    confirmed_job_qty = fields.Integer("Confirmed Applicants", compute='_compute_applicants')
    openapplications_qty = fields.Integer("Open Applicants", compute='_compute_applicants')
    issue_qty = fields.Integer("Questions", compute='_compute_issue')
    openjob = fields.Boolean('Open', compute='_compute_applicants')
    par_contact_id = fields.Many2one('campos.event.participant', string='Contact', ondelete='restrict') # Relation to inherited res.partner
    
    @api.one
    @api.depends('date_public','date_closing','min_qty_jobbere','wanted_qty_jobbere','max_qty_jobbere')
    def _compute_applicants(self):
        confirmed_job_qty = self.env['campos.committee.function'].sudo().search_count([('job_id', '=', self.id)])
        self.confirmed_job_qty = confirmed_job_qty
        self.openapplications_qty = self.env['campos.event.participant'].sudo().search_count([('job_id', '=', self.id),('state', 'in', ['draft','sent','standby'])])
        openjob = True
        if self.date_public and self.date_public > fields.Date.today(): 
            openjob = False
        if self.date_closing and self.date_closing < fields.Date.today():
            openjob = False
        if self.max_qty_jobbere and self.max_qty_jobbere <= confirmed_job_qty:
            openjob = False
        self.openjob = openjob
        
    @api.one
    def _compute_issue(self):
        self.issue_qty = self.env['project.issue'].search_count([('model_reference', '=', 'campos.job,%d' % self.id)])
        
    @api.multi
    def open_issues(self):
        self.ensure_one()
        return {
                'name':_("Questions re %s") % self.name,
                'view_mode': 'kanban,tree,form',
                'view_type': 'form',
                'res_model': 'project.issue',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'domain': [('model_reference', '=', 'campos.job,%d' % self.id)],
                }
    
    
