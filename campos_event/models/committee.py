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
    _parent_store = True

    name = fields.Char('Name', size=64, translate=True)
    code = fields.Char('Code', size=64)
    parent_left = fields.Integer('Parent Left', index=True)
    parent_right = fields.Integer('Parent Right', index=True)
    account = fields.Char('Account', size=64)
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
    committee_type_id = fields.Many2one('campos.committee.type', 'Type')
    
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
    par_contact_id = fields.Many2one('campos.event.participant', string='Contact', ondelete='restrict') # Relation to inherited res.partner
    job_ids = fields.One2many('campos.job', 'committee_id', string='Jobs')
    part_function_ids = fields.One2many('campos.committee.function', 'committee_id', string='Members')
    website_published = fields.Boolean('Visible in Website')
    partner_list = fields.Char(
        string="Approver list",
        compute='_compute_partner_list')
    
    @api.one
    @api.depends('name', 'code', 'parent_id.name', 'parent_id.display_name', 'parent_id.code')
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

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('display_name', operator, name)] + args, limit=limit)
        return recs.name_get()
    
    @api.one
    @api.depends('part_function_ids','member_ids')
    def _compute_member_no(self):
        '''
        Count members in the Committee
        '''
        self.member_no = len(self.sudo().part_function_ids)
        self.applicants_count = self.env['campos.event.participant'].sudo().search_count([('committee_id', '=', self.id),('state', 'in', ['sent'])])

    @api.one
    @api.depends('approvers_ids')
    def _compute_partner_list(self):    
        self.partner_list = ','.join([str(par.partner_id.id) for par in self.approvers_ids])
        
class CampCommitteeType(models.Model):

    """ Committee Types"""
    _description = 'Committee Type'
    _name = 'campos.committee.type'
    
    name = fields.Char('Committee Type')        
        
class CampCommitteeFunctionType(models.Model):

    """ Committee Job Functions"""
    _description = 'Committee FunctionsType'
    _name = 'campos.committee.function.type'
    
    name = fields.Char('Function Title')
    chairman = fields.Boolean()

class CampCommitteeJobTitle(models.Model):

    """ Committee Job Title"""
    _description = 'Committee Job Title'
    _name = 'campos.committee.job.title'
   
    name = fields.Char('Job Title')


    
class CampCommitteeFunction(models.Model):

    """ Committee Participant Function"""
    _description = 'Committee Functions'
    _name = 'campos.committee.function'
    _order = 'committee_id'
    
    name = fields.Char()
    participant_id = fields.Many2one('campos.event.participant', ondelete='cascade', string="Participant")
    committee_id = fields.Many2one('campos.committee',
                                   'Committee',
                                   ondelete='cascade')
    function_type_id = fields.Many2one('campos.committee.function.type', string="Function", ondelete='cascade')
    job_id = fields.Many2one('campos.job',
                         'Job annonce',
                         ondelete='set null')
    email = fields.Char('Email', related='participant_id.partner_id.email')
    mobile = fields.Char('Mobile', related='participant_id.partner_id.mobile')
    com_contact = fields.Text(string='Contact', related='committee_id.par_contact_id.complete_contact')
    active = fields.Boolean(default=True)
    job_title_id = fields.Many2one('campos.committee.job.title',
                         'Job Title',
                         ondelete='set null')

        
    @api.multi
    def write(self, vals):
        _logger.info("New func Write Entered %s", vals.keys())
        ret =  super(CampCommitteeFunction, self).write(vals)
        for app in self:
            if vals.has_key('new_func'):
                _logger.info("New func mail %s %s", app.committee_id.name, app.participant_id.name)
                template = app.committee_id.template_id
                assert template._name == 'email.template'
                try:
                    template.send_mail(app.participant_id.id)
                except:
                    _logger.info("New func mail %s %s FAILED", app.committee_id.name, app.participant_id.name)
                    pass
                if app.participant_id.sharepoint_mail and not app.participant_id.sharepoint_mail_created:
                    template = self.env.ref('campos_event.request_sharepoint')
                    assert template._name == 'email.template'
                    try:
                        template.send_mail(app.participant_id.id)
                    except:
                        pass
                    app.participant_id.sharepoint_mail_requested = fields.Datetime.now()
                else:
                    if app.participant_id.zexpense_access_wanted:
                        if not app.participant_id.zexpense_access_created:
                            template = self.env.ref('campos_event.request_zexpense')
                            assert template._name == 'email.template'
                            try:
                                template.send_mail(app.participant_id.id)
                            except:
                                pass
                            app.participant_id.zexpense_access_requested = fields.Datetime.now()
                        else:
                            template = self.env.ref('campos_event.request_zexpense_change')
                            assert template._name == 'email.template'
                            try:
                                template.send_mail(app.participant_id.id)
                            except:
                                pass
                    old_user =  self.env['res.users'].sudo().search([('participant_id', '=', app.participant_id.id)])
                    if len(old_user) == 0:
                        app.participant_id.action_create_user()
                app.participant_id.write({'committee_id': False,
                                          'job_id': False,
                                          'my_comm_contact': False,
                                          'state': 'approved'
                                          })
        return ret
    
    @api.multi
    def action_open_participant(self):
        self.ensure_one()
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
        
    
