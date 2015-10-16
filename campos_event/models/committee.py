# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of CampOS Event,
#     an Odoo module.
#
#     Copyright (c) 2015 Stein & Gabelgaard ApS
#                        http://www.steingabelgaard.dk
#                        Hans Henrik Gaelgaard
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

import logging

_logger = logging.getLogger(__name__)


class CampCommittee(models.Model):

    """ Committee """
    _description = 'Committee'
    _name = 'campos.committee'
    _inherit = 'mail.thread'
    _order = 'sequence'

    name = fields.Char('Name', size=64, translate=True)
    code = fields.Char('Code', size=64, translate=True)
    account = fields.Char('Account', size=64, translate=True)
    desc = fields.Text('Description', translate=True)
    #email = fields.Char('Email', size=128)
    member_ids = fields.One2many(
        'campos.event.participant',
        'committee_id',
        'Members')
    approvers_ids = fields.Many2many(
        'campos.event.participant', 'committee_approvers_rel',
        'committee_id','member_id',
        'Approvers')
    template_id = fields.Many2one('email.template', 'Email Template', ondelete='set null',
                                  domain=[('model_id', '=', 'campos.event.participant')])
    parent_id = fields.Many2one('campos.committee', 'Main Committee')
    child_ids = fields.One2many(
        'campos.committee',
        'parent_id',
        'Subcommittees')
    sequence = fields.Integer(
        'Sequence',
        select=True,
        help="Gives the sequence order.")
    display_name = fields.Char(
        string="Full Name",
        compute='_compute_display_name',
        store=True)
    member_no = fields.Integer(string='# Member', compute='_compute_member_no')
    applicants_count = fields.Integer(string='# Applicants', compute='_compute_member_no')
    contact_id = fields.Many2one('res.partner', string='Contact', ondelete='restrict') # Relation to inherited res.partner
    job_ids = fields.One2many('campos.job', 'committee_id', string='Jobs')
    part_function_ids = fields.One2many('campos.committee.function', 'committee_id', string='Members')

    @api.one
    @api.depends('name', 'code', 'parent_id.display_name', 'parent_id.code')
    def _compute_display_name(self):
        '''
        Returns the Full path in committee hierarchy
        '''

        def _compute_codename(comm):
            if comm.code:
                return "%s - %s" % (comm.code, comm.name)
            else:
                return comm.name

        names = [self.parent_id.display_name, _compute_codename(self)]
        self.display_name = ' / '.join(filter(None, names))

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        '''
        The name is the topmost committees code + full path name
        '''
        def _compute_codename(comm):
            if comm.code:
                return "%s - %s" % (comm.code, comm.name)
            else:
                return comm.name

        result = []
        for comm in self:

            names = [comm.parent_id.display_name, _compute_codename(comm)]
            result.append((comm.id, ' / '.join(filter(None, names))))

        return result

    @api.one
    @api.depends('part_function_ids','member_ids')
    def _compute_member_no(self):
        '''
        Count members in the Committee
        '''
        self.member_no = len(self.part_function_ids)
        self.applicants_count = self.env['campos.event.participant'].search_count([('committee_id', '=', self.id),('state', 'in', ['sent'])])
        
        
class CampCommitteeFunctionType(models.Model):

    """ Committee Job Functions"""
    _description = 'Committee FunctionsType'
    _name = 'campos.committee.function.type'
    
    name = fields.Char('Function Title')
    
class CampCommitteeFunction(models.Model):

    """ Committee Participant Function"""
    _description = 'Committee Functions'
    _name = 'campos.committee.function'
    _order = 'committee_id'
    
    name = fields.Char()
    participant_id = fields.Many2one('campos.event.participant', ondelete='cascade')
    committee_id = fields.Many2one('campos.committee',
                                   'Committee',
                                   ondelete='cascade')
    function_type_id = fields.Many2one('campos.committee.function.type', string="Function", ondelete='cascade')
    job_id = fields.Many2one('campos.job',
                         'Job',
                         ondelete='set null')
    email = fields.Char('Email', related='participant_id.partner_id.email')
    mobile = fields.Char('Mobile', related='participant_id.partner_id.mobile')
    com_contact = fields.Text(string='Contact', related='committee_id.contact_id.complete_contact')
    active = fields.Boolean()
        
    @api.multi
    def write(self, vals):
        ret =  models.Model.write(self, vals)
        for app in self:
            template = self.env.ref('campos_event.new_staff_member')
            assert template._name == 'email.template'
            template.send_mail(app.id)
            app.participant_id.state = 'approved'
        return ret    
    
    @api.multi
    def action_open_participant(self):
        self.ensure_one()
        _logger.info("In action_open_participant X [%d] %d %s " %(self.env.context.get('active_id'), self.participant_id.id, self.participant_id.name))
        return {
            'name': self.participant_id.name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'campos.event.participant',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'domain': '[]',
            'res_id': self.participant_id.id,
            'context': {'active_id': self.participant_id.id}, 
            }
        
    
