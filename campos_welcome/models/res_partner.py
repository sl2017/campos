# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
import odoorpc


import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):

    _inherit = 'res.partner'

    remote_system_id = fields.Many2one('campos.remote.system')
    # Internal ID in remote system. For MemberService, always res.partner id
    remote_int_id = fields.Integer("Remote system internal ID", index=True)
    # External identifer. Member number for perosns, Org Code for Scout Groups
    remote_ext_id = fields.Integer("Remote system external ID", index=True)
    # Link ID in Remote Systems. For MemberService: Profile ID for persons, Organization ID for Scout Groups
    remote_link_id = fields.Integer("Remote System link ID")
    last_import = fields.Datetime()

    @api.multi
    def change_remote_group(self):
        for rp in self:
            if rp.remote_system_id.systype == 'bm':
                remote = self.env['campos.remote.system'].search([('host', '=', 'medlem.dds.dk')])
                msodoo = odoorpc.ODOO(remote.host, protocol=remote.protocol, port=remote.port)
                msodoo.login(remote.db_name, remote.db_user, remote.db_pwd)
                org_id = msodoo.env['member.organization'].search([('organization_code', '=', str(rp.remote_ext_id))])
                org = msodoo.execute('member.organization', 'read', org_id, ['id','partner_id'])
                _logger.info('ORG: %s', org)
                if org:
                    rp.write({'remote_system_id': remote.id,
                              'remote_int_id': org[0]['partner_id'][0],
                              'remote_link_id': org_id[0],
                              })
