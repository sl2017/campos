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
                'name': fields.char('Name', size=64),
                'par_id': fields.many2one('dds_camp.event.participant', 'Participation',  ondelete='cascade'),
                'reg_id': fields.many2one('event.registration', 'Registration', ondelete='cascade'),
                'wiz_id': fields.many2one('dds_camp.activity.signup', 'Wizard', ondelete='cascade'),
                }

class activity_signup_wizard(osv.osv_memory):
    _name = 'dds_camp.activity.signup'
    _description = 'Activity Signup'    
    
    def _get_participants(self, cr, uid, ids, name, args, context=None):
        res = {}
        if ids:
            wiz = self.browse(cr, uid, ids, context)[0] 
            print "Wiz_gp", wiz.act_id, wiz.act_ins_id, 'Old', wiz.act_ins_id, wiz.seats
            chk_pts = wiz.act_ins_id.activity_id.points
            #Build possible members
            if wiz.reg_id.participant_ids:
                valid_part = ''
                allowed_ids = [] 
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
                    allowed_ids.append(par.id)
                res[wiz.id] = {'valid_part' : valid_part.strip(','),
                               'allowed_ids': [(6, 0, allowed_ids)],
                               }
        return res    
    
    def onchange_activity_id(self, cr, uid, ids, activity_id, context=None):       
                
        res = {}
        values = {}
        print "on_ch", activity_id
        act_obj = self.pool.get('dds_camp.activity.activity')
        for act in act_obj.browse(cr,uid, [activity_id], context):
            res['value'] = {'info' : (act.desc if act.desc else "") + _('\nAge: %d - %d\nPoints: %d') % (act.age_from, act.age_to, act.points)} 
        
        print "res", res
        return res     

    def _check_seats(self, cr, uid, ids, context=None):
        record = self.browse(cr, uid, ids, context=context)
        for data in record:
            if data.seats <= 0:
                return False
            if data.act_ins_id.seats_hard and not data.ticket_id:
                print "check seats", data.seats, data.act_ins_id.seats_available
                if data.seats > data.act_ins_id.seats_available:
                    return False
        return True
                    
    _columns = {
              'reg_id': fields.many2one('event.registration', 'Registration', required=True, select=True, ondelete='cascade'),
              
              'name': fields.char('Own Note', size=128, help='You can add a Note for own use. It will be shown on activity list etc. I will NOT be read/answered by the Staff.'),
              'seats': fields.integer('3. Reserve Seats', required=True),
              'state': fields.selection([('step1', 'step1'), ('step2', 'step2'), ('expired','Expired'), ('done','Done')]),
              'message': fields.char('Message', size=128),
              'info': fields.text('Info'),
              'members_ids': fields.many2many('dds_camp.activity.signup.members', 'dds_camp_activity_signup_mbr','wizard_id', 'member_id','Registered'),
              'parti_ids': fields.many2many('dds_camp.event.participant', 'dds_camp_activity_part_rel','wizard_id', 'member_id','Registered'),
              "allowed_ids": fields.function (_get_participants, type="many2many", string='Valid Partners', method=True, relation='dds_camp.event.participant', multi="par"),
              'valid_part': fields.function(_get_participants, type='char', string='Valid Partners', method=True, multi="par"),
              'act_id': fields.many2one('dds_camp.activity.activity', '1. Select Activity', required=True, select=True, ondelete='cascade'),
              'act_ins_id': fields.many2one('dds_camp.activity.instanse', '2. Select Period', required=True, select=True, ondelete='cascade'),
              'testact_id': fields.many2one('dds_camp.activity.instanse', '1. Test Select Activity',  ondelete='cascade'),
              'ticket_id': fields.many2one('dds_camp.activity.ticket', 'Ticket', ondelete='set null'),
              }
    
    _defaults = {'message' : lambda self,cr,uid,context: _('Select Activity, Period and number of required seats')}
    
    _constraints = [(_check_seats, 'Error: Reserved seats must be Positive and Less or equal to available seats', ['seats'])]
    
    def action_signup(self, cr, uid, ids, context=None):
        # your treatment to click  button next 
        # ...
        # update state to  step2
        
        mbr_obj = self.pool.get('dds_camp.activity.signup.members')
        wiz = self.browse(cr, uid, ids, context)[0] 
        print "Wiz", wiz.act_id, wiz.act_ins_id, wiz.seats
         
        chk_pts = wiz.act_ins_id.activity_id.points
        dt = wiz.act_ins_id.period_id.date_begin[0:6]
        #Build possible members
        allowed_ids = [] 
        if wiz.reg_id.participant_ids:
            for par in wiz.reg_id.participant_ids:
                #Test aktivitetsdato mod deltagerdage
                days_ok = True
                if par.days_ids:
                    for d in par.days_ids:
                        if d.date == dt:
                            days_ok = d.state
                            break
                if not days_ok:
                    continue
                # Test alderskrav        
                if par.calc_age < wiz.act_ins_id.activity_id.age_from or par.calc_age > wiz.act_ins_id.activity_id.age_to:
                    continue
                # Test aktivitetspoints
                if chk_pts:
                    if par.spare_act_pts < chk_pts:
                        continue
                # Test mod andre bookinger    
                period_ok = True
                if par.ticket_ids:
                    for tck in par.ticket_ids:
                        if tck.act_ins_id.period_id.date_begin <= wiz.act_ins_id.period_id.date_end and tck.act_ins_id.period_id.date_end >= wiz.act_ins_id.period_id.date_begin:
                            period_ok = False
                            break
                if not period_ok:
                    continue
                allowed_ids.append(par.id)
                mbr_obj.create(cr, SUPERUSER_ID, {'wiz_id' : wiz.id,
                                                  'par_id' : par.id,
                                                  'name'   : par.name,
                                                  'reg_id' : wiz.reg_id.id})
                 
        if context:
            ctx = context
        else:
            ctx = {}
            
        ctx['valid_par_ids'] =  allowed_ids
        print "ctx", ctx       
        # Create ticket
        ticket_obj = self.pool.get('dds_camp.activity.ticket')
        ticket_id = ticket_obj.create(cr, SUPERUSER_ID, {'reg_id' : wiz.reg_id.id,
                                                         'state' : 'open',
                                                         'act_ins_id' : wiz.act_ins_id.id,
                                                         'seats' : wiz.seats,
                                                         'reserved_time': fields.datetime.now()
                                                         })
        #return to wizard
        self.write(cr, uid, ids, {'state': 'step2', 
                                  'message' : _('Click Add to add participants to this activity. Your reservation will expire in 15 min.'),
                                  'ticket_id' : ticket_id, 
                                  'info' : (wiz.act_id.desc if wiz.act_id.desc else "") + _('\nAge: %d - %d\nPoints: %d') % (wiz.act_id.age_from, wiz.act_id.age_to, wiz.act_id.points)
                                  }, context=context)
        actins_obj = self.pool.get('dds_camp.activity.instanse')
        if context:
            ctx2 = context
        else:
            ctx2 = {}
        ctx2['no_limit_check'] = True    
        dummy,actins_name = actins_obj.name_get(cr, uid, [wiz.act_ins_id.id], ctx2)[0]
        return {
              'name': actins_name,
              'type': 'ir.actions.act_window',
              'res_model': 'dds_camp.activity.signup',
              'view_mode': 'form',
              'view_type': 'form',
              'res_id': ids[0],
              'views': [(False, 'form')],
              'target': 'new',
              'context': ctx
               }
        
    def action_done(self, cr, uid, ids, context=None):
        wiz = self.browse(cr, uid, ids, context)[0]
        
        if wiz.act_ins_id.seats_hard and len(wiz.parti_ids) > (wiz.seats + wiz.act_ins_id.seats_available):
            self.write(cr, uid, ids, {'state': 'step2', 
                                      'message' : _('Too many participants selected. Only %d seats reserved. Remove participants!.') % (wiz.seats),})
        else:         
            ticket_obj = self.pool.get('dds_camp.activity.ticket')
            if wiz.ticket_id.state == 'open' or wiz.act_ins_id.seats_available > 0:
                pars = [p.id for p in wiz.parti_ids]
                print "pars", pars
                if len(pars):
                    ticket_obj.write(cr, SUPERUSER_ID, [wiz.ticket_id.id], {'par_ids' : [(6,0, pars)],
                                                                            'name' : wiz.name,
                                                                            'seats' : len(pars),
                                                                            'state' : 'done'})
                    self.write(cr, uid, ids, {'state': 'done', 
                                              'message' : _('Activity booked!.'),})
                else:
                    self.write(cr, uid, ids, {'state': 'done', 
                                              'message' : _('No participants selected. Booking cancelled.'),})
                    ticket_obj.unlink(cr, SUPERUSER_ID, [wiz.ticket_id.id])    
            else:    
                ticket_obj.unlink(cr, SUPERUSER_ID, [wiz.ticket_id.id])
                self.write(cr, uid, ids, {'state': 'expired', 
                                          'message' : _('Reservation has expired and activity is fully booked.'),
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
            