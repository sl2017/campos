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


class CampCommittee(models.Model):

    """ Committee """
    _description = 'Committee'
    _name = 'campos.committee'
    _inherit = 'mail.thread'

    name = fields.Char('Name', size=64, translate=True)
    code = fields.Char('Code', size=64, translate=True)
    desc = fields.Text('Description', translate=True)
    email = fields.Char('Email', size=128)
    member_ids = fields.One2many(
        'campos.event.participant',
        'committee_id',
        'Members')
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
    @api.depends('member_ids')
    def _compute_member_no(self):
        '''
        Count members in the Committee
        '''
        self.member_no = len(
            self.member_ids.filtered(
                lambda record: record.state in [
                    'sent',
                    'approved']))
