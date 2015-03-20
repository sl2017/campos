# -*- coding: utf-8 -*-
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

from urllib import urlopen
from xml.etree import ElementTree as ET
import mechanize
from datetime import date, datetime, timedelta

def bmdate2oedate(bmdate):
    if bmdate:
        dtm = datetime.strptime(bmdate, "%d-%m-%Y %H:%M:%S")
    
        return datetime.strftime(dtm, "%Y-%m-%d")
    else:
        return False

class bm_import_wirzard_members(osv.osv_memory):
    _name = 'dds_camp.bmimportwizard.members'
    _description = 'BM Import Participants'    
    _columns = {
                'registration_id': fields.many2one('event.registration', 'Registration', ondelete='cascade'),
                #'wizard_id': fields.many2one('dds_camp.bmimportwizard', 'Import', required=True, select=True, ondelete='cascade'),
                'participation_id': fields.many2one('dds_camp.event.participant', 'Participation',  ondelete='cascade'),
                # The following fields are synced to res_partner on Write      
                'name': fields.char('Name', size=128, required=True, select=True),
                'street': fields.char('Street', size=128),
                'street2': fields.char('Street2', size=128),
                'zip_id': fields.many2one('res.better.zip', 'City/Location'),
                'zip': fields.char('Zip', change_default=True, size=24),
                'city': fields.char('City', size=128),
                
                'email': fields.char('Email', size=240),
                'phone': fields.char('Phone', size=64),
                # end of res_partner fields
                'birth' : fields.date('Birth date'),
        
                'leader' : fields.boolean('Leader'),
                'memberno' : fields.char('Membership number', size=32, help='Own reference number'), 
                'state' : fields.selection([('draft',''),
                                           ('pending', 'Tilmeldes'),
                                           ('done', 'Tilmeldt')], 'Status')     
            }
    
    def button_reg_confirm(self, cr, uid, ids, context=None, *args):
        return self.write(cr, uid, ids, {'state': 'pending'})
             
    def button_reg_cancel(self, cr, uid, ids, context=None, *args):
        return self.write(cr, uid, ids, {'state': 'draft'})

class bm_import_wizard(osv.osv_memory):
    _name = 'dds_camp.bmimportwizard'
    _description = 'BM Import Participants'    
    _columns = {
              'registration_id': fields.many2one('event.registration', 'Registration', required=True, select=True, ondelete='cascade'),
              'bmmember': fields.char(u'Blåt medlemsnr', size=32),
              'bmpassword': fields.char('Adgangskode', size=32),
              'state': fields.selection([('step1', 'step1'), ('step2', 'step2')]),
              'message': fields.char('Message', size=128),
              'members_ids': fields.many2many('dds_camp.bmimportwizard.members', 'dds_camp_bm_import_rel','wizard_id', 'member_id','Members'),
              } 


    def action_login(self, cr, uid, ids, context=None):
        # your treatment to click  button next 
        # ...
        # update state to  step2
        
        wiz = self.browse(cr, uid, ids, context)[0]
        
        br = mechanize.Browser()
        br.open("https://login.dds.dk/login/sso_tickets/require_login")
        br.select_form(nr=2)
        br.form['data[user]'] = wiz.bmmember
        br.form['data[password]'] = wiz.bmpassword
        br.submit()
        email = ''
        for form in br.forms():
            for ct in form.controls:
                if ct.name == 'data[email]' and ct.value > '':
                    email = ct.value
             
        if email > '':
        
            self.write(cr, uid, ids, {'state': 'step2', 'message' : 'Klik på Tilføj for at udpege medlemmer' }, context=context)
            self.bm_member_import( cr, uid, wiz.registration_id.id, ids[0], wiz.registration_id.ddsgroup, context)
        
        else:
            self.write(cr, uid, ids, {'message': 'Login fejlede'}, context=context)
            
        # return view
        return {
              'type': 'ir.actions.act_window',
              'res_model': 'dds_camp.bmimportwizard',
              'view_mode': 'form',
              'view_type': 'form',
              'res_id': wiz.id,
              'views': [(False, 'form')],
              'target': 'new',
               }

    def action_previous(self, cr, uid, ids, context=None):
        # your treatment to click  button previous 
        # ...
        # update state to  step1
        self.write(cr, uid, ids, {'state': 'step1', }, context=context)
        # return view
        return {
              'type': 'ir.actions.act_window',
              'res_model': 'dds_camp.bmimportwizard',
              'view_mode': 'form',
              'view_type': 'form',
              'res_id': ids[0],
              'views': [(False, 'form')],
              'target': 'new',
               }

    def action_done(self, cr, uid, ids, context=None):
       
        wiz = self.browse(cr, uid, ids, context)[0]
        part_obj = self.pool.get('dds_camp.event.participant')
        for member in wiz.members_ids:
            part = dict((name, getattr(member, name)) for name in ['name', 'street', 'street2', 'zip', 'city', 'email', 'phone', 'birth', 'leader', 'memberno'])
            part['registration_id'] = member.registration_id.id
            part['imported_bm'] = True
            if member.leader:
                part['appr_leader'] = True
            part_id = part_obj.create(cr, uid, part, context)
            part_obj.action_create_day_lines(cr, uid, [part_id], context)
        return {
              'type': 'ir.actions.act_window',
              'res_model': 'event.registration',
              'view_mode': 'form',
              'view_type': 'form',
              'res_id': wiz.registration_id.id,
              'views': [(False, 'form')],
              
               }
                                  
    def bm_member_import(self, cr, uid, reg_id, wizard_id, ddsgroup, context=None):
    
        part_obj = self.pool.get('dds_camp.event.participant')
        membernos = []
        part_ids = part_obj.search(cr, uid, [('registration_id','=',reg_id),('imported_bm','=',True)])
        for part in part_obj.browse(cr, uid, part_ids, context):
            membernos.append(part.memberno)
        mbr_obj = self.pool.get('dds_camp.bmimportwizard.members')
        ir_config_parameter = self.pool.get("ir.config_parameter")
        params = eval(ir_config_parameter.get_param(cr, uid, "dds_camp.bm_settings", context=context))
        params.update({'action' : 'memberships',
                       'org' : ddsgroup})
        leaders = []
        rows = ET.parse(urlopen('%(url)s%(action)s?system=%(system)s&password=%(password)s&org=%(org)s' % params))
        for row in rows.getroot():
            membership = dict((e.tag, e.text) for e in row)
            if membership:
                if membership.has_key('trustLeaderType') and membership['trustLeaderType'] == 'True':
                    leaders.append(membership['memberNumber'])
        
        params.update({'action' : 'members'})
        data = []
        fields = ['id', 'name', 'street', 'zip', 'city', 'email', 'phone', 'birth', 'leader', 'memberno', 'registration_id/.id', 'state']
        rows = ET.parse(urlopen('%(url)s%(action)s?system=%(system)s&password=%(password)s&org=%(org)s' % params))
        for row in rows.getroot():
            member = dict((e.tag, e.text) for e in row)
            if member:
                print member
                fullname = ''
                if member.has_key('userFirstname') and member['userFirstname']:
                    fullname = member['userFirstname'] + ' '
                if member.has_key('userLastname') and member['userLastname']:
                    fullname += member['userLastname']    
                data.append([
                         member['userMemberNumber'],  # # id
                         fullname,  # # name
                         member['addressFull'] if member.has_key('addressFull') else False,  # # street
                         member['PostalCity'][:4] if member.has_key('PostalCity') and member['PostalCity'] else False,  # # zip,
                         member['PostalCity'][5:] if member.has_key('PostalCity') and member['PostalCity'] else False,  # # city,
                         member['userEmail'] if member.has_key('userEmail') else False,  # # email
                         member['userPrivatePhone'] if member.has_key('userPrivatePhone') else False,  # #phone
                         bmdate2oedate(member['userBorn']),
                         'True' if member['userMemberNumber'] in leaders else 'False',  # #Leader 
                         member['userMemberNumber'],  # # memberno
                         reg_id,
                         'done' if member['userMemberNumber'] in membernos else 'draft'
                         #wizard_id
                         ])
            
        result = mbr_obj.load(cr, uid, fields, data, context=None)

  
