# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class EventRegistration(models.Model):

    _inherit = 'event.registration'

    sale_order_line_ids = fields.One2many('campos.mat.report', 'reg_id')
    tocampdate = fields.Date('Arrival date', compute='_compute_dates', store=True)
    fromcampdate = fields.Date('Departure date', compute='_compute_dates')

    checkin_info_html = fields.Html('Check In Notes', compute='compute_checkin')
    checkin_ok = fields.Boolean('Check In possible', compute='compute_checkin')
    arrive_time = fields.Datetime('Arrival')
    checkin_completed = fields.Datetime('Check In Time')
    arr_date_ids = fields.One2many('campos.reg.arrdate', 'registration_id', 'Arrival dates', domain=[('arr_date', '!=', False)])
    nav_due_amount = fields.Float('Due amount')
    nav_due_amount_eur = fields.Float('Due amount EUR')
    checkin_participant_id = fields.Many2one('campos.event.participant', 'Check in by', track_visibility='onchange')

    @api.multi
    @api.depends('participants_camp_day_ids.will_participate')
    def _compute_dates(self):
        where_params = [tuple(self.ids)]
        self._cr.execute("""SELECT 
                                registration_id_stored as reg_id, 
                                min(the_date) as tocampdate, 
                                max(the_date) as fromcampdate 
                            FROM campos_event_participant_day d 
                            JOIN campos_event_participant cep ON cep.id = d.participant_id 
                            JOIN res_partner p ON p.id=cep.partner_id  
                            WHERE d.will_participate = 't' AND 
                                cep.state <> 'deregistered' AND 
                                p.participant = 't' AND 
                                registration_id_stored in %s 
                            GROUP BY registration_id_stored;
                      """, where_params)
        for reg_id, tocampdate, fromcampdate in self._cr.fetchall():
            reg = self.browse(reg_id)
            reg.tocampdate = tocampdate
            reg.fromcampdate = fromcampdate
 
    @api.multi
    #@api.depends()
    def compute_checkin(self):
        for reg in self:
            ckr_clc = False
            checkin_ok = True
            infotext = []
            if reg.group_country_code2 == 'DK':
                if not reg.child_certificates_accept:
                    infotext.append(_('Indhentning af børneattester ikke bekræftiget'))
                    checkin_ok = False
            else:
                if reg.clc_stat_ids.filtered(lambda r: r.clc_state in ['required', 'enrolled']):
                    infotext.append(_('CLC not completed'))
                    checkin_ok = False
#             #Economy
#             if reg.partner_id.credit > 0:
#                 infotext.append(_('Unpaid invoices. Total due: DKK %.2f') % (reg.partner_id.credit))
#                 checkin_ok = False
#             elif reg.partner_id.credit == 0 and not reg.fee_total > 0:
#                 if self.env['account.invoice'].search_count([('partner_id', '=', reg.partner_id.id), ('state', 'in', ['open','paid'])]) == 0:
#                     checkin_ok = False
#                     infotext.append(_('Invoice not yet generated!'))
#                 else:
#                     infotext.append(_('Payment recived'))
#             else:
#                 if reg.fee_total > 0:
#                     infotext.append(_('Payment recived'))
#                 else:
#                     infotext.append(_('No Payment'))

            
            if reg.nav_due_amount > 0:
                infotext.append(_('Unpaid invoices. Total due: DKK %.2f') % (reg.nav_due_amount))
                checkin_ok = False
            else:
                infotext.append(_('Payment recived'))
#             EUR figures is not valid
#             else:
#                 if reg.nav_due_amount_eur > 0:
#                     infotext.append(_('Unpaid invoices. Total due: EUR %.2f') % (reg.nav_due_amount_eur))
#                     checkin_ok = False
#                 else:
#                     infotext.append(_('Payment recived'))
#                     
            if checkin_ok:
                reg.checkin_info_html = '<div class="campos_info_box">%s</div>' % '<br />'.join(infotext) if infotext else False
            else:
                reg.checkin_info_html = '<div class="campos_warning_box">%s</div>' % '<br />'.join(infotext) if infotext else False
            reg.checkin_ok = checkin_ok
            
            
    @api.multi
    def action_checkin(self):
        self.ensure_one()
        
        if not self.checkin_ok and not self.env.user.has_group('campos_checkin.group_campos_checkin_mgr'):
            return self.env['warning_box'].info(title=_('Checkin'), message=_(u'Checkin for %s is not possible here\nGo to Løkkegård for Checkin.\n\nPlease show the location on the map for the Group') %  (self.name))

        action = {
            'name': _("Checkin for %s") % (self.name),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'campos.checkin.grp.wiz',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {
                'default_registration_id': self.id,
                },
        }
        return action

    @api.multi
    def action_cancel_checkin(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window.message',
            'title': _('Cancel Checkin'),
            'message': _("Change to 'Arrived' or 'Not yet arrived'"),
            'buttons': [
                {
                    'type': 'method',
                    'name': _('Arrived'),
                    'model': self._name,
                    'method': 'action_execute_cancel_checkin',
                    # list of arguments to pass positionally
                    'args': [self.ids],
                    # dictionary of keyword arguments
                    'kwargs': {'force_state': 'arrived'},
                },
                {
                    'type': 'method',
                    'name': _('Not yet arrived'),
                    'model': self._name,
                    'method': 'action_execute_cancel_checkin',
                    # list of arguments to pass positionally
                    'args': [self.ids],
                    # dictionary of keyword arguments
                    'kwargs': {'force_state': 'open'},
                }
            ]
        }

    @api.multi
    def action_execute_cancel_checkin(self, force_state=None):
        self.ensure_one()
        if force_state:
            self.state = force_state
            if force_state == 'open':
                self.arrive_time = False


    @api.multi
    def action_checkout(self):
        self.ensure_one()
        
        self.state = 'checkout'
        
