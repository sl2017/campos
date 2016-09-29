# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


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
