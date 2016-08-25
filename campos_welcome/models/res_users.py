# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.addons.auth_signup.res_users import SignupError

class ResUsers(models.Model):

    _inherit = 'res.users'
    
    def auth_blaatlogin(self, cr, uid, member_number, ticket, context=None):
        user_ids = self.search(cr, uid, [("member_number", "=", member_number)])
        if not user_ids:
            crs_id = self.pool['campos.remote.system'].search(cr, uid, [('systype', '=', 'bm')])
            crs = self.pool['campos.remote.system'].browse(cr, uid, crs_id)
            values = crs.getBMuserData(member_number)
            values['member_number'] = member_number
            values['blaatlogin_ticket'] = ticket
            db, login, _ = self.signup(cr, uid, values)
            return {'db': db, 'login': login}
        assert len(user_ids) == 1
        user = self.browse(cr, uid, user_ids[0], context=context)
        user.write({'blaatlogin_ticket': ticket})
        return {'db':cr.dbname, 'login':user.login}

    def signup(self, cr, uid, values, token=None, context=None):
        new_email = values.get('email')
        partner_id = False
        if new_email:
            partner_ids = self.pool['res.partner'].search(cr, uid, [('email', '=', new_email)])
            if partner_ids:
                partner_id = partner_ids[0]
            else:
                part_ids = self.pool['event.participant'].search([('private_mailaddress', '=', new_email)])
                if part_ids:
                    partner_id = self.pool('event.participant').browse(cr, uid, part_ids[0]).partner_id.id
            if partner_id:
                partner = self.pool['res.partner'].browse(cr, uid, partner_id)
                if partner.user_ids:
                    raise SignupError('Email address already in use. Please use Password reset')
                else:
                    values['partner_id'] = partner_id
        return super(ResUsers, self).signup(cr, uid, values, token=token, context=context) 
        