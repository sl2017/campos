# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of CampOS Event,
#     an Odoo module.
#
#     Copyright (c) 2015 Stein & Gabelgaard ApS
#                        http://www.steingabelgaard.dk
#                        Hans Henrik Gabelgaard
#
#     CampOS Event is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     CampOS Event is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with CampOS Event.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import random
from datetime import date
from dateutil.relativedelta import relativedelta
from urlparse import urljoin
import werkzeug

from openerp.addons.base_geoengine import geo_model
from openerp import models, fields, api
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


def random_token():
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.SystemRandom().choice(chars) for i in xrange(20))


class EventParticipantReject(models.Model):

    '''
    Jobber Reject
    '''
    _name = 'campos.event.par.reject'
    _description = 'Event Participant Reject'

    reason = fields.Text(required=True)
    committee_id = fields.Many2one('campos.committee',
                                   'Committee',
                                   ondelete='set null')
    participant_id = fields.Many2one('campos.event.participant',
                                     'Paricipant',
                                     ondelete='set null')
    job_id = fields.Many2one('campos.job',
                             'Job',
                             ondelete='set null')

    @api.multi
    def write(self, vals):
        ret = models.Model.write(self, vals)
        for rej in self:
            rej.participant_id.state = 'rejected'
        return ret


class EventParticipant(geo_model.GeoModel):

    '''
    Detail participant/Jobber Info
    '''
    _name = 'campos.event.participant'
    _description = 'Event Participant'
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'name'

    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict')  # Relation to inherited res.partner
    registration_id = fields.Many2one('event.registration', 'Registration')
    staff_qty_pre_reg = fields.Integer(related='registration_id.staff_qty_pre_reg', string='Number of Staff - Pre-registration', readonly=True)
    reg_organization_id = fields.Many2one(
        'campos.scout.org',
        'Scout Organization', related='registration_id.organization_id', store=True, readonly=True)
    scout_color = fields.Char('Scout Org Color', related='registration_id.organization_id.color')

    # Scout Leader Fiedls

    appr_leader = fields.Boolean('Leder godkendt', track_visibility='onchange')
    att_received = fields.Boolean(
        'Attest modtaget',
        track_visibility='onchange')
    leader = fields.Boolean('Is Leader')
    birthdate = fields.Date('Date of birth')
    birthdate_short = fields.Char(compute='_compute_birthdate_short')
    age = fields.Integer('Age', compute='_compute_age', store=True)
    camp_age = fields.Integer('Age (On Camp)', compute='_compute_camp_age', store=True)
    context_age = fields.Integer('Age', compute='_compute_context_age')

    # Jobber fields
    committee_id = fields.Many2one('campos.committee',
                                   'Have agreement with committee',
                                   track_visibility='onchange',
                                   ondelete='set null')
    comm_approver_ids = fields.Many2many(
        'campos.committee', 'committee_approvers_rel',
        'member_id', 'committee_id',
        'Approver for')
    sent_to_comm_date = fields.Date('Sent to Committee')
    reject_ids = fields.One2many('campos.event.par.reject', 'participant_id', string='Rejects')
    jobfunc_ids = fields.One2many('campos.committee.function', 'participant_id', string='Committee/Function')
    state = fields.Selection([('reg', 'Registered'),
                              ('duplicate','Duplicate' ),
                              ('draft', 'Received'),
                              ('standby', 'Standby'),
                              ('sent', 'Sent to committee'),
                              ('inprogress', 'Work in Progress'),
                              ('approved', 'Approved by the committee'),
                              ('rejected', 'Rejected'),
                              ('deregistered', 'Deregistered'),
                              ('arrived', 'Arrived'),
                              ('checkin', 'Check In Completed')],
                             'Approval Procedure',
                             track_visibility='onchange', default='draft')

    standby_until = fields.Date('Standby until')
    agreements = fields.Text('Agreements')
    internal_note = fields.Text('Internal Note')

    job_id = fields.Many2one('campos.job',
                             'Job',
                             ondelete='set null')
    newsletter = fields.Boolean('Newsletter')

    sharepoint_mail = fields.Boolean('Sharepoint mail wanted')
    sharepoint_mailaddress = fields.Char('Sharepoint mail address')
    sharepoint_clienttype = fields.Selection([('client', 'Client'),
                                              ('online', 'Online')], "Sharepoint Client")
    sharepoint_mail_created = fields.Date('Sharepoint mail created')
    sharepoint_mail_requested = fields.Datetime('Sharepoint mail requested')
    private_mailaddress = fields.Char('Private mail address')

    zexpense_access_wanted = fields.Boolean('zExpense access wanted')
    zexpense_access_created = fields.Date('zExpense access created')
    zexpense_access_requested = fields.Datetime('zExpense access requested')
    zexpense_firsttime_pwd = fields.Char('zExpense First time password')

    workwish = fields.Text('Want to work with')
    my_comm_contact = fields.Char('Aggreement with')
    profession = fields.Char(
        'Profession',
        size=64,
        help='What do you do for living')

    par_internal_note = fields.Text('Internal note')
    complete_contact = fields.Text("contact", compute='_get_complete_contact')
    qualifications = fields.Text('Qualifications')

    workas_planner = fields.Boolean('Camp Planner')
    workas_jobber = fields.Boolean('Jobber on Camp')

    # confirm links
    confirm_token = fields.Char('Confirm Token')
    reg_confirm_url = fields.Char('Confirm registration URL', compute='_compute_confirm_urls')
    zexpense_confirm_url = fields.Char('Confirm zExpense URL', compute='_compute_confirm_urls')
    sharepoint_confirm_url = fields.Char('Confirm sharepoint URL', compute='_compute_confirm_urls')
    # participant_url = fields.Char('Participant URL', compute='_compute_confirm_urls')

    meeting_registration_ids = fields.One2many('event.registration', compute='_compute_meeting_registration')
    staff_del_prod_ids = fields.One2many('campos.staff.del.prod', 'participant_id')
    
    primary_committee_id = fields.Many2one('campos.committee',
                                           'Primary committee',
                                           track_visibility='onchange',
                                           ondelete='set null')

    # Pay4it fields
    participant_number = fields.Char(related='partner_id.ref', string='Skejser ID')
    wristband_date = fields.Date('wristband issued', groups='campos_event.group_campos_info', track_visibility='onchange')
    pay4it_created = fields.Boolean('Created on skejser.dk')
    pay4it_cardactive = fields.Boolean('Card/Wristband attached')
    pay4it_cardnumber = fields.Char('Wristband number', groups='campos_event.group_campos_admin')
    
    tag_ids = fields.Many2many('campos.par.tag', string='Tags', groups='campos_event.group_campos_admin')
    
    # Doublet mamagement
    doublet_id = fields.Many2one('campos.event.participant', 'Doublet')
    reverse_doublet_id = fields.Many2one('campos.event.participant', 'Reverse doublet', compute='_compute_reverse_doublet_id', compute_sudo=True)
    

    api.multi
    def _compute_reverse_doublet_id(self):
        where_params = [tuple(self.ids)]
        self._cr.execute("""SELECT doublet_id as our_id, id as reverse_id
                      FROM campos_event_participant
                      WHERE doublet_id IN %s
                      """, where_params)
        for id, reverse_id in self._cr.fetchall():
            par = self.browse(id)
            par.reverse_doublet_id = reverse_id
            
    
    @api.one
    def _compute_meeting_registration(self):
        self.meeting_registration_ids = self.partner_id.event_registration_ids.filtered(lambda r: r.id != self.registration_id.id)

    @api.one
    def _compute_confirm_urls(self):
        if not self.sudo().confirm_token:
            token = random_token()
            while self.sudo().search_count([('confirm_token', '=', token)]):
                token = random_token()

            self.sudo().write({'confirm_token': token})
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        query = {'db': self._cr.dbname}
        self.reg_confirm_url = urljoin(base_url, 'campos/confirm/reg/%s?%s' % (self.confirm_token, werkzeug.url_encode(query)))
        self.zexpense_confirm_url = urljoin(base_url, 'campos/confirm/zx/%s?%s' % (self.confirm_token, werkzeug.url_encode(query)))
        self.sharepoint_confirm_url = urljoin(base_url, 'campos/confirm/sp/%s?%s' % (self.confirm_token, werkzeug.url_encode(query)))


    def age_on_date(self, age_date=date.today()):
        '''
        Calculate the members age on a given date
        :param age_date: date object or string in Odoo date format (YYYY-MM-DD)
        '''
        if isinstance(age_date, basestring): 
            age_date = fields.Date.from_string(age_date)
        return relativedelta(age_date, fields.Date.from_string(self.birthdate)).years

    @api.multi
    @api.depends('birthdate')
    def _compute_age(self):
        for part in self:
            part.age = relativedelta(date.today(), fields.Date.from_string(part.birthdate)).years if part.birthdate else False

    @api.multi
    @api.depends('birthdate')
    def _compute_camp_age(self):
        for part in self:
            part.camp_age = relativedelta(date(2017,7,22), fields.Date.from_string(part.birthdate)).years if part.birthdate else False

    @api.multi
    @api.depends('birthdate')
    def _compute_context_age(self):
        for part in self:
            part.context_age = part.age_on_date(self.env.context.get('context_age_date')) if part.birthdate else False

    @api.one
    @api.depends('birthdate')
    def _compute_birthdate_short(self):
        if self.birthdate:
            self.birthdate_short = '%s%s%s' % (self.birthdate[8:10], self.birthdate[5:7], self.birthdate[2:4])


    def check_duplicate(self):
        if self.email and self.staff:
            if self.search_count([('id', '!=', self.id), ('state', '!=', 'deregistered'), ('staff','=',True), '|', '|', ('email', '=', self.email), ('sharepoint_mailaddress', '=', self.email), ('private_mailaddress', '=', self.email)]):
                self.state = 'duplicate'
    @api.model
    def create(self, vals):
        par = super(EventParticipant, self).create(vals)
        if not par.registration_id:
            par.registration_id = self.env['event.registration'].create({
                'event_id': 1,
                'partner_id': par.partner_id.id,
                'contact_partner_id': par.partner_id.id,
                'econ_partner_id': par.partner_id.id, })
            # par.staff = True
        if par.state == 'draft':
            par.check_duplicate()
        par.assign_participant_number()
        return par

    @api.multi
    def write(self, vals):
        _logger.info("Par Write Entered %s", vals.keys())
        ret = super(EventParticipant, self).write(vals)
        for par in self:
            if 'sharepoint_mail_created' in vals and par.sharepoint_mail_created:
                template = self.env.ref('campos_event.info_sharepoint')
                assert template._name == 'email.template'
                try:
                    template.send_mail(par.id)
                except:
                    pass
                par.action_create_user()
                if par.zexpense_access_wanted and not par.zexpense_access_created:
                    template = self.env.ref('campos_event.request_zexpense')
                    assert template._name == 'email.template'
                    try:
                        template.send_mail(par.id)
                    except:
                        pass
                    par.zexpense_access_requested = fields.Datetime.now()
        
            if 'zexpense_access_created' in vals and par.zexpense_access_created:
                template = self.env.ref('campos_event.info_zexpense')
                assert template._name == 'email.template'
                try:
                    template.send_mail(par.id)
                except:
                    pass
            if 'state' in vals and vals['state'] == 'draft':
                par.check_duplicate()
        return ret

    @api.one
    @api.depends('name', 'email', 'mobile', 'sharepoint_mailaddress')
    def _get_complete_contact(self):
        self.complete_contact = '\n'.join(filter(None, [self.name, self.sharepoint_mailaddress if self.sharepoint_mailaddress else self.email, self.mobile]))

    @api.onchange('committee_id')
    def onchange_committee_id(self):
        self.state = 'draft'
        self.sent_to_comm_date = False

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        template = self.env.ref('campos_event.new_staff_member')
        assert template._name == 'email.template'

        partner_list = ','.join([str(par.partner_id.id) for par in self.committee_id.approvers_ids])
        _logger.info('Partner list: %s', partner_list)
        try:
            template.with_context({'partner_list': partner_list}).send_mail(self.id)
        except:
            pass

        self.state = 'sent'
        self.sent_to_comm_date = fields.Date.context_today(self)
        return True

    @api.multi
    def action_standby(self):
        self.ensure_one()
        self.state = 'standby'
        view = self.env.ref('campos_event.view_event_participant_standby_form')
        return {
            'name': _("Set to standby: %s" % self.name),
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view.id,
            'res_model': 'campos.event.participant',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'res_id': self.id,
        }

    @api.multi
    def action_send_standby_mail(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        template = self.env.ref('campos_event.staff_on_standby', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='campos.event.participant',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',

        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
        
    @api.multi
    def action_send_mail(self, template):
        """ Open a window to compose an email, with the template
            message loaded by default
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='campos.event.participant',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',

        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def action_approve(self):
        self.ensure_one()
        form = self.env.ref('campos_event.view_campos_committee_function_form2', False)
        context = {
            'default_participant_id': self.id,
            'default_committee_id': self.committee_id.id,
            'default_job_id': self.job_id.id,
            'new_func': True,
        }
        if self.sharepoint_mail:
            context['default_sharepoint_mail'] = "yes"
        if self.zexpense_access_wanted:
            context['default_zexpense_access_wanted'] = "yes"
        return {
            'name': _("Approval of %s" % self.name),
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(form.id, 'form')],
            'view_id': form.id,
            'res_model': 'campos.committee.function',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context
        }

    @api.multi
    def action_inprogress(self):
        self.ensure_one()
        self.state = 'inprogress'
        
    @api.multi
    def action_reject(self):
        self.ensure_one()
        return {
            'name': _("Reject %s" % self.name),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'campos.event.par.reject',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                    'default_participant_id': self.id,
                    'default_committee_id': self.committee_id.id,
            }
        }

    @api.multi
    def action_create_user(self):
        for par in self:
            old_user = self.env['res.users'].sudo().search([('participant_id', '=', par.id)])
            if len(old_user) == 0:
                # Swap mails?
                if (not par.private_mailaddress or par.private_mailaddress == par.email) and '@sl2017.dk' not in par.email:
                    par.private_mailaddress = par.email
                    if par.sharepoint_mailaddress:
                        par.email = par.sharepoint_mailaddress
        
                old_user = self.env['res.users'].sudo().search([('login', '=', par.email)])
                if old_user:
                    old_user.write({'participant_id': par.id,
                                    'groups_id': [(4, self.env.ref('campos_event.group_campos_staff').id)]
                                    })
                    old_user.action_reset_password()
                else:
                    new_user = self.env['res.users'].sudo().create({'login': par.email,
                                                             'partner_id': par.partner_id.id,
                                                             'participant_id' : par.id,
                                                             'groups_id': [(4, self.env.ref('campos_event.group_campos_staff').id)],
                                                             # 'groups_id': [(4, self.env.ref('base.group_portal').id)]
                                                             })
                # new_user.with_context({'create_user': True}).action_reset_password()

            else:
                old_user.write({'participant_id' : par.id,
                                'groups_id': [(4, self.env.ref('campos_event.group_campos_staff').id)],
                                })
                par.partner_id = old_user.partner_id
                old_user.action_reset_password()

    @api.multi
    def action_deregister_participant(self):
        for par in self:
            old_user = self.env['res.users'].suspend_security().search([('participant_id', '=', par.id)])
            if len(old_user):
                old_user.suspend_security().write({'active': False,
                                                   'login' : '%s-invalid-%d' % (old_user.login, old_user.id)})
            par.state = 'deregistered'
            par.jobfunc_ids.write({'active': False})
            if par.sharepoint_mailaddress:
                template = self.env.ref('campos_event.deregister_sharepoint')
                assert template._name == 'email.template'
                try:
                    template.send_mail(par.id)
                except:
                    pass
            if par.zexpense_access_wanted or par.zexpense_access_created:
                template = self.env.ref('campos_event.deregister_zexpense')
                assert template._name == 'email.template'
                try:
                    template.send_mail(par.id)
                except:
                    pass
            par.comm_approver_ids = None
            for comm in self.env['campos.committee'].search([('par_contact_id.id', '=', par.id)]):
                comm.par_contact_id = False


    @api.multi
    @api.depends('partner_id.name')
    def name_get(self):

        result = []
        for part in self:
            result.append((part.id, part.complete_contact if self.env.context.get('add_email') else part.partner_id.display_name))

        return result

    @api.v7
    def onchange_address(
            self, cr, uid, ids, use_parent_address, parent_id, context=None):
        """ Wrapper on the user.partner onchange_address, because some calls to the
            partner form view applied to the user may trigger the
            partner.onchange_type method, but applied to the user object.
        """
        partner_ids = [
            user.partner_id.id for user in self.browse(
                cr,
                uid,
                ids,
                context=context)]
        return self.pool['res.partner'].onchange_address(
            cr, uid, partner_ids, use_parent_address, parent_id, context=context)

    @api.model
    def _needaction_domain_get(self):
        """
        Show a count of Participants that need action on the menu badge.
        
        For Event Managers (Followers of the Event): 
            Participants in status "Received" or "Rejected"
        For Committee Managers (Followers of Committee): 
            Participants in status "Sent to Committee"
        
        """

        regs = self.env['event.registration'].search([('event_id.message_follower_ids', '=', self.env.user.partner_id.id)])
        coms = self.env['campos.committee'].search([('message_follower_ids', '=', self.env.user.partner_id.id)])

        return ['|',
                '&', ('registration_id', 'in', regs.ids), ('state', 'in', ['draft', 'rejected']),
                '&', ('committee_id', 'in', coms.ids), ('state', 'in', ['sent']),
                ]

    def message_get_suggested_recipients(self, cr, uid, ids, context=None):
        recipients = super(EventParticipant, self).message_get_suggested_recipients(cr, uid, ids, context=context)
        for lead in self.browse(cr, uid, ids, context=context):
                if lead.partner_id:
                    self._message_add_suggested_recipient(cr, uid, recipients, lead, partner=lead.partner_id, reason=_('Participant'))
        return recipients
    
    @api.model
    def init_primary_committee_id(self):
        for par in self.search([('primary_committee_id', '=', False)]):
            if par.jobfunc_ids:
                par.primary_committee_id = par.jobfunc_ids[0].committee_id 
                
    @api.multi
    def assign_participant_number(self):
        for par in self:
            if not par.participant_number:
                par.participant_number = self.env['ir.sequence'].next_by_code('participant.number')
            if par.partner_id.ref != par.participant_number:
                 par.partner_id.ref = par.participant_number