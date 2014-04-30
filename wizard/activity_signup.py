import logging

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import email_re
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)

class activity_signup_wizard_members(osv.osv_memory):
    _name = 'dds_camp.activity.signup.members'
    _description = 'Activity Signup Members'    
    _columns = {
                'name': fields.char('Own Note', size=64),
                'par_id': fields.many2one('dds_camp.event.participant', 'Participation',  ondelete='cascade'),
                'reg_id': fields.many2one('event.registration', 'Registration', ondelete='cascade'),
                'wiz_id': fields.many2one('dds_camp.activity.signup', 'Wizard', ondelete='cascade'),
                }

class activity_signup_wizard(osv.osv_memory):
    _name = 'dds_camp.activity.signup'
    _description = 'Activity Signup'    
    
    def _get_participants(self, cr, uid, ids, name, args, context=None):
        res = {}
        wiz = self.browse(cr, uid, ids, context)[0] 
        
        chk_pts = wiz.act_ins_id.activity_id.points
        #Build possible members
        if wiz.reg_id.participant_ids:
            valid_part = ''
            for par in wiz.reg_id.participant_ids:
                print "Testing:", par.name, par.calc_age, par.spare_act_pts
                if par.calc_age < wiz.act_ins_id.activity_id.age_from or par.calc_age > wiz.act_ins_id.activity_id.age_to:
                    print "kill", wiz.act_ins_id.activity_id.age_from, wiz.act_ins_id.activity_id.age_to
                    continue
                if chk_pts:
                    if par.spare_act_pts < chk_pts:
                        continue
                period_ok = True
                if par.ticket_ids:
                    for tck in par.ticket_ids:
                        if tck.act_ins_id.period_id.date_begin <= wiz.act_ins_id.period_id.date_end and tck.act_ins_id.period_id.date_end >= wiz.act_ins_id.period_id.date_begin:
                            period_ok = False
                            break
                if not period_ok:
                    print "kill period"
                    continue
                print "Create", par.name, wiz.id, ids[0]
                valid_part += ','.join(str(par.id))
            res[wiz.id] = {'valid_part' : valid_part.strip(','),
                           }
        return res    
    
    def onchange_activity_id(self, cr, uid, ids, activity_id, context=None):       
                
        res = {}
        values = {}
        print "on_ch", activity_id
        act_obj = self.pool.get('dds_camp.activity.activity')
        for act in act_obj.browse(cr,uid, [activity_id], context):
            res['value'] = {'info' : act.desc + _('\nAge: %d - %d\nPoints: %d') % (act.age_from, act.age_to, act.points)} 
        
        print "res", res
        return res     

            
    _columns = {
              'reg_id': fields.many2one('event.registration', 'Registration', required=True, select=True, ondelete='cascade'),
              
              'name': fields.char('Own Note', size=128, help='You can add a Note for own use. It will be shown on activity list etc. I will NOT be read/answered by the Staff.'),
              'seats': fields.integer('3. Reserve Seats'),
              'state': fields.selection([('step1', 'step1'), ('step2', 'step2'), ('expired','Expired'), ('done','Done')]),
              'message': fields.char('Message', size=128),
              'info': fields.text('Info'),
              #'members_ids': fields.many2many('dds_camp.activity.signup.members', 'dds_camp_activity_signup_rel','wizard_id', 'member_id','Registered'),
              'parti_ids': fields.many2many('dds_camp.event.participant', 'dds_camp_activity_part_rel','wizard_id', 'member_id','Registered'),
              
              'valid_part': fields.function(_get_participants, type='char', string='Valid Partners', method=True, multi="par"),
              'activity_id': fields.many2one('dds_camp.activity.activity', '1. Select Activity', required=True, select=True, ondelete='cascade'),
              'act_ins_id': fields.many2one('dds_camp.activity.instanse', '2. Select Period', required=True, select=True, ondelete='cascade'),
              'ticket_id': fields.many2one('dds_camp.activity.ticket', 'Ticket', ondelete='cascade'),
              }
    
    _defaults = {'message' : lambda *a: 'Select Activity, Period and number of required seats'}
    
    def action_signup(self, cr, uid, ids, context=None):
        # your treatment to click  button next 
        # ...
        # update state to  step2
        
#         mbr_obj = self.pool.get('dds_camp.activity.signup.members')
        wiz = self.browse(cr, uid, ids, context)[0] 
#         
#         chk_pts = wiz.act_ins_id.activity_id.points
#         #Build possible members
#         if wiz.reg_id.participant_ids:
#             for par in wiz.reg_id.participant_ids:
#                 print "Testing:", par.name, par.calc_age, par.spare_act_pts
#                 if par.calc_age < wiz.act_ins_id.activity_id.age_from or par.calc_age > wiz.act_ins_id.activity_id.age_to:
#                     print "kill", wiz.act_ins_id.activity_id.age_from, wiz.act_ins_id.activity_id.age_to
#                     continue
#                 if chk_pts:
#                     if par.spare_act_pts < chk_pts:
#                         continue
#                 period_ok = True
#                 if par.ticket_ids:
#                     for tck in par.ticket_ids:
#                         if tck.act_ins_id.period_id.date_begin <= wiz.act_ins_id.period_id.date_end and tck.act_ins_id.period_id.date_end >= wiz.act_ins_id.period_id.date_begin:
#                             period_ok = False
#                             break
#                 if not period_ok:
#                     print "kill period"
#                     continue
#                 print "Create", par.name, wiz.id, ids[0]
#                 mbr_obj.create(cr, SUPERUSER_ID, {'wiz_id' : wiz.id,
#                                                   'par_id' : par.id,
#                                                   'name'   : par.name,
#                                                   'reg_id' : wiz.reg_id.id})
#                 
        
        # Create ticket
        ticket_obj = self.pool.get('dds_camp.activity.ticket')
        ticket_id = ticket_obj.create(cr, SUPERUSER_ID, {'reg_id' : wiz.reg_id.id,
                                                         'state' : 'open',
                                                         'act_ins_id' : wiz.act_ins_id.id,
                                                         'seats' : wiz.seats,
                                                         })
        #return to wizard
        self.write(cr, uid, ids, {'state': 'step2', 
                                  'message' : 'Click Add to add participants to this activity. Your reservation will expire in 15 min.',
                                  'ticket_id' : ticket_id, 
                                  }, context=context)
        return {
              'type': 'ir.actions.act_window',
              'res_model': 'dds_camp.activity.signup',
              'view_mode': 'form',
              'view_type': 'form',
              'res_id': ids[0],
              'views': [(False, 'form')],
              'target': 'new',
               }
        
    def action_done(self, cr, uid, ids, context=None):
       
        wiz = self.browse(cr, uid, ids, context)[0]
        
        ticket_obj = self.pool.get('dds_camp.activity.ticket')
        if wiz.ticket_id.state == 'open' or wiz.ac_ins_id.seats_available > 0:
            ticket_obj.write(cr, SUPERUSER_ID, [wiz.ticket_id], {'par_ids' : [(6,0, [p.id for p in wiz.parti_ids])],
                                                                 'name' : wiz.name,
                                                                 'seats' : len(wiz.parti_ids),
                                                                 'state' : 'done'})
            self.write(cr, uid, ids, {'state': 'done', 
                                      'message' : 'Activty booked!.',})
        else:    
            ticket_obj.unlink(cr, SUPERUSER_ID, [wiz.ticket_id])
            self.write(cr, uid, ids, {'state': 'expired', 
                                      'message' : 'Reservation has expired and activity is full.',
                                      'ticket_id' : None,
                                      }) 
        
        return {
              'type': 'ir.actions.act_window',
              'res_model': 'dds_camp.activity.signup',
              'view_mode': 'form',
              'view_type': 'form',
              'res_id': ids[0],
              'views': [(False, 'form')],
              'target': 'new',
               }
            