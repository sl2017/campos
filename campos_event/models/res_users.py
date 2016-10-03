# -*- coding: utf-8 -*-

import openerp
from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, ustr
from openerp.osv import osv

import logging

_logger = logging.getLogger(__name__)


def now(**kwargs):
    dt = datetime.now() + timedelta(**kwargs)
    return dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)


class ResUsers(models.Model):
    _inherit = 'res.users'

    participant_id = fields.Many2one('campos.event.participant', ondelete='set null')
    committee_ids = fields.Many2many('campos.committee', compute='_compute_committeeaccess')
    participant_ids = fields.Many2many('campos.event.participant', compute='_compute_committeeaccess')

    @api.one
    def _compute_committeeaccess(self):
        if self.participant_id:
            top = self.env['campos.committee'].search(['|',('approvers_ids', 'in', self.participant_id.id),('par_contact_id.id','=',self.participant_id.id)])
            for f in self.participant_id.jobfunc_ids:
                if f.function_type_id.chairman:
                    top += f.committee_id
            coms = top
            for c in top:
                childs = self.env['campos.committee'].search([('id', 'child_of', c.id)])
                coms |= childs
            members = set()
            self.committee_ids = coms
            for c in coms:
                for a in c.sudo().member_ids:
                    members.add(a.sudo().id)
                for f in c.sudo().part_function_ids:
                    members.add(f.sudo().participant_id.id)
            _logger.info("Part list for %s (%d): %s", self.name, len(members), list(members))
            self.participant_ids = self.env['campos.event.participant'].sudo().browse(list(members))
            _logger.info("Part list for %s : %s", self.name, self.participant_ids.ids)
        else:
            self.committee_ids = False
            
    def action_reset_password(self, cr, uid, ids, context=None):
        """ create signup token for each user, and send their signup url by email """
        # prepare reset password signup
        res_partner = self.pool.get('res.partner')
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context)]
        res_partner.signup_prepare(cr, uid, partner_ids, signup_type="reset", expiration=now(days=+1), context=context)

        context = dict(context or {})

        # send email to users with their signup url
        template = False
        if context.get('template_ref'):
            try:
                # get_object() raises ValueError if record does not exist
                ref = context.get('template_ref').split('.')
                template = self.pool.get('ir.model.data').get_object(cr, uid, ref[0], ref[1])
            except ValueError:
                pass
        
        
        if not bool(template) and context.get('create_user'):
            try:
                # get_object() raises ValueError if record does not exist
                template = self.pool.get('ir.model.data').get_object(cr, uid, 'auth_signup', 'set_password_email')
            except ValueError:
                pass
        if not bool(template):
            template = self.pool.get('ir.model.data').get_object(cr, uid, 'auth_signup', 'reset_password_email')
        assert template._name == 'email.template'

        for user in self.browse(cr, uid, ids, context):
            if not user.email:
                raise osv.except_osv(_("Cannot send email: user has no email address."), user.name)
            context['lang'] = user.lang  # translate in targeted user language
            self.pool.get('email.template').send_mail(cr, uid, template.id, user.id, force_send=True, raise_exception=True, context=context)
