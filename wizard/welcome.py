# -*- coding: utf-8 -*-

import logging

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import email_re
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)

class wizard_welcome(osv.osv_memory):
    """
        A model to configure users in the portal wizard.
    """
    _name = 'dds_camp.wizard.welcome'
    _description = 'Welcome'
    
    ##_defaults = {'name' : lambda *a: _('Welcome')}
    
    def open_staffsignup(self, cr, uid, ids, context=None):
        """Method is used to show form view in new windows"""
        staff_id = self.pool.get('dds_camp.staff').search(cr, uid, [('user_id.id', '=', uid)])[0]
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'dds_camp', 'portal_staff_form')
        view_id = view_ref and view_ref[1] or False,
        this = self.browse(cr, uid, ids, context=context)[0]
        return {
             'type': 'ir.actions.act_window',
             'name': 'Staff signup',
             'view_mode': 'form',
             'view_type': 'form',
             'view_id': view_id,
             'res_model': 'dds_camp.staff',
             'nodestroy': True,
             'res_id': staff_id,  # assuming the many2one
             'target':'current',
             'context': context,
             }


wizard_welcome()

def _lang_get(self, cr, uid, context=None):
    lang_pool = self.pool.get('res.lang')
    ids = lang_pool.search(cr, uid, [], context=context)
    res = lang_pool.read(cr, uid, ids, ['code', 'name'], context)
    return [(r['code'], r['name']) for r in res]


class wizard_signupstaff(osv.osv_memory):
    """
        A model to configure users in the portal wizard.
    """
    _name = 'dds_camp.wizard.signup.staff'
    _description = 'Staff signup'
    
    _columns = {
                'name': fields.char('Name', size=128, required=True, select=True),
                'email': fields.char('Email', size=240, required=True),
                'phone': fields.char('Phone', size=64),
                'state': fields.selection([('step1', 'step1'),('step2', 'step2')]),
                'message': fields.char('Message', size=128),
                'lang': fields.selection(_lang_get, 'Language',
                                         help="If the selected language is loaded in the system, all documents related to this contact will be printed in this language. If not, it will be English."),
               } 
    _defaults = {'lang': lambda self, cr, uid, ctx: ctx.get('lang', 'da_DK')}    
                
    def do_staffsignup(self, cr, uid, ids, context=None):                 

        
        staff_obj = self.pool.get('dds_camp.staff')
        reg_obj = self.pool.get('event.registration')
        par_obj = self.pool.get('dds_camp.event.participant')
        partner_obj = self.pool.get('res.partner')
        por_obj = self.pool.get('portal.wizard')
    
        for signup in self.browse(cr, uid, ids, context):
            # Create partner
            partner_id = partner_obj.create(cr, SUPERUSER_ID, {'name': signup.name,
                                                               'email': signup.email,
                                                               'phone' : signup.phone,
                                                               'lang': signup.lang,
                                                               'tz': 'Europe/Copenhagen'})
            # Create user
            por_id = por_obj.create(cr, SUPERUSER_ID, {'portal_id': 11,
                                                       'user_ids': [(0, 0, {'partner_id': partner_id, 
                                                                           'email': signup.email, 
                                                                           'in_portal': True})]
                                                       })
            ctx = context
            ctx = {'mail_template' : context.get('mail_tempalte','email_template_14'), 'mail_tpl_module': '__export__'}
            if ctx.has_key('default_state'):
                del ctx['default_state']
                
            por_obj.action_apply(cr, SUPERUSER_ID, [por_id], ctx)
            # Create Registration
            #partner = partner_obj.browse(cr, SUPERUSER_ID, [partner_id], context)[0]
            reg_id = reg_obj.create(cr, SUPERUSER_ID, {'name': signup.name,
                                                       'email': signup.email,
                                                       'phone' : signup.phone,
                                                       'partner_id': partner_id,
                                                       'contact_partner_id':  partner_id,
                                                       'event_id' : 2,
                                                       #'user_id': partner.user_id
                                                       })
            
            # Create participant
            par_id = par_obj.create(cr, SUPERUSER_ID, {'name': signup.name,
                                                       'email': signup.email,
                                                       'partner_id': partner_id,
                                                       'registration_id': reg_id,
                                                       'state': 'draft',
                                                       'partype' : 'itshead',
                                                       'phone' : signup.phone,
                                                       })
            # Create Staff
            staff_obj.create(cr, SUPERUSER_ID, {'reg_id' : reg_id,
                                                'par_id' : par_id,
                                                })
            
            self.write(cr, uid, ids, {'state': 'step2',
                                      'message': 'Hej ' + signup.name})
        return {
              'type': 'ir.actions.act_window',
              'res_model': 'dds_camp.wizard.signup.staff',
              'name': 'Thank you!',
              'view_mode': 'form',
              'view_type': 'form',
              'res_id': ids[0],
              'views': [(False, 'form')],
              'target': 'new',
               }

        