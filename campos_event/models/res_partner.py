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
from openerp.osv.expression import get_unaccent_wrapper


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
    primary_reg_id = fields.Many2one('event.registration', 'Group registration', compute='_compute_primary_reg', store=True)
    customer_type = fields.Char('Export Type', compute='_compute_customer_type')
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if record.parent_id and not record.is_company and (not context.get('without_company') or (record.staff and not context.get('with_reg'))):
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
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            self.check_access_rights('read')
            where_query = self._where_calc(args)
            self._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            where_str = where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(self.env.cr)

            query = """SELECT id
                         FROM res_partner
                      {where} ({email} {operator} {percent}
                           OR {display_name} {operator} {percent}
                           OR {reference} {operator} {percent})
                           -- don't panic, trust postgres bitmap
                     ORDER BY {display_name} {operator} {percent} desc,
                              {display_name}
                    """.format(where=where_str,
                               operator=operator,
                               email=unaccent('email'),
                               display_name=unaccent('display_name'),
                               reference=unaccent('ref'),
                               percent=unaccent('%s'))

            where_clause_params += [search_name]*4
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            self.env.cr.execute(query, where_clause_params)
            partner_ids = map(lambda x: x[0], self.env.cr.fetchall())

            if partner_ids:
                return self.browse(partner_ids).name_get()
            else:
                return []
        return super(ResPartner, self).name_search(name, args, operator=operator, limit=limit)

    @api.one
    @api.depends('name', 'email', 'mobile')
    def _get_complete_contact(self):
        self.complete_contact = '\n'.join(filter(None, [self.name, self.email, self.mobile]))
        
    @api.multi
    @api.depends('event_registration_ids')
    def _compute_primary_reg(self):
        event_id = self.env['ir.config_parameter'].get_param('campos_welcome.event_id')
        if event_id:
            event_id = int(event_id)
        for par in self:
            regs = par.event_registration_ids.filtered(lambda r: r.event_id.id == event_id and r.state in ['open', 'done'])
            if regs:
                par.primary_reg_id = regs[0]

    @api.multi
    @api.depends('scoutgroup','staff','country_id')
    def _compute_customer_type(self):
        for par in self:
            p1 = ''
            p2 = ''
            if par.staff:
                p1 = 'Jobber'
            elif par.scoutgroup:
                p1 = 'Grupper'

            if par.country_id.code == 'DK':
                p2 = 'In'
            else:
                p2 = 'Ud'
            par.customer_type = '%s %s' % (p1, p2)
