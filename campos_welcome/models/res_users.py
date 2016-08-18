# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


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
