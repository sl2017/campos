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


class ResPartner(models.Model):

    '''
    Add Type Fields to Partner
    '''
    _inherit = 'res.partner'

    scoutgroup = fields.Boolean()
    participant = fields.Boolean()
    staff = fields.Boolean(default=False)
    sponsor = fields.Boolean()
    skype = fields.Char()
    complete_contact = fields.Text("contact", compute='_get_complete_contact')
    event_registration_ids = fields.One2many('event.registration', 'partner_id', string='Event registrations')
    municipality_id = fields.Many2one(
        'campos.municipality',
        'Municipality',
        select=True,
        ondelete='set null')
    scoutorg_id = fields.Many2one('campos.scout.org', 'Scout organization')
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if record.parent_id and not record.is_company and not context.get('without_company'):
                name =  "%s, %s" % (record.parent_id.name, name)
            if context.get('show_address'):
                name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
                name = name.replace('\n\n','\n')
                name = name.replace('\n\n','\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            if context.get('add_email') and record.email:
                name = "%s\n<%s>" % (name, record.email)    
            if context.get('name_only'):
                name = record.name    
            res.append((record.id, name))
        return res

    @api.one
    @api.depends('name', 'email', 'mobile')
    def _get_complete_contact(self):
        self.complete_contact = '\n'.join(filter(None, [self.name, self.email, self.mobile]))
      