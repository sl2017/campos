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

from openerp import models, fields, api
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)

class EventRegistration(models.Model):

    '''
    Scout Group or Jobber "Head" registration

    '''
    _inherit = 'event.registration'

    participant_ids = fields.One2many(
        'campos.event.participant',
        'registration_id', string="Participants")

    name = fields.Char(related='partner_id.name', store=True)
    scoutgroup = fields.Boolean(related='partner_id.scoutgroup')
    staff = fields.Boolean(related='partner_id.staff')
    staff_qty_pre_reg = fields.Integer('Number of Staff - Pre-registration')
    country_id = fields.Many2one('res.country', 'Country')
    organization_id = fields.Many2one(
        'campos.scout.org',
        'Scout Organization')

    scout_division = fields.Char('Division/District', size=64)
    municipality_id = fields.Many2one(
        'campos.municipality',
        'Municipality',
        select=True,
        ondelete='set null')
    ddsgroup = fields.Integer('DDS Gruppenr')
    region = fields.Char('Region', size=64)

    # Contact
    contact_partner_id = fields.Many2one(
        'res.partner', 'Contact', states={
            'done': [
                ('readonly', True)]})
    contact_email = fields.Char(
        string='Email',
        related='contact_partner_id.email')

    # Economic Contact
    econ_partner_id = fields.Many2one(
        'res.partner', 'Economic Contact', states={
            'done': [
                ('readonly', True)]})
    econ_email = fields.Char(string='Email', related='econ_partner_id.email')


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
        ret =  models.Model.write(self, vals)
        for rej in self:
            rej.participant_id.state = 'rejected'
        return ret
    
    
class EventParticipant(models.Model):

    '''
    Detail participant/Jobber Info
    '''
    _name = 'campos.event.participant'
    _description = 'Event Participant'
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict') # Relation to inherited res.partner
    registration_id = fields.Many2one('event.registration','Registration')
    reg_organization_id = fields.Many2one(
        'campos.scout.org',
        'Scout Organization', related='registration_id.organization_id')

    # Scout Leader Fiedls

    appr_leader = fields.Boolean('Leder godkendt', track_visibility='onchange')
    att_received = fields.Boolean(
        'Attest modtaget',
        track_visibility='onchange')
    leader = fields.Boolean('Is Leader')

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
    state = fields.Selection([('draft', 'Received'),
                              ('standby','Standby'),
                              ('sent', 'Sent to committee'),
                              ('approved', 'Approved by the committee'),
                              ('rejected', 'Rejected'),
                              ('deregistered', 'Deregistered')],
                             'Approval Procedure',
                             track_visibility='onchange', default='draft')
    
    standby_until = fields.Date()
    agreements = fields.Text()
    internal_note = fields.Text()
    
    job_id = fields.Many2one('campos.job',
                             'Job',
                             ondelete='set null')
    newsletter  = fields.Boolean()
    
    sharepoint_mail = fields.Boolean('Sharepoint mail wanted')
    sharepoint_mailaddress = fields.Char()
    sharepoint_clienttype = fields.Selection([('client', 'Client'),
                                              ('online', 'Online')], "Sharepoint Client")
    sharepoint_mail_created = fields.Date()
    sharepoint_mail_requested = fields.Datetime()
    
    zexpense_access_wanted = fields.Boolean('zExpense access wanted')
    zexpense_access_created = fields.Date()
    zexpense_access_requested = fields.Datetime()
    
    workwish = fields.Text('Want to work with')
    my_comm_contact = fields.Char('Aggreement with')
    profession = fields.Char(
        'Profession',
        size=64,
        help='What do you do for living')

    par_internal_note = fields.Text('Internal note')
    
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
            'name':_("Set to standby: %s" % self.name),
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
    def action_approve(self):
        self.ensure_one()
        return {
            'name':_("Approval of %s" % self.name),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'campos.committee.function',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                    'default_participant_id': self.id,
                    'default_committee_id': self.committee_id.id,
                    'default_job_id' : self.job_id.id,
                    }
            }
        
#         template = self.committee_id.template_id
#         if template:
#             template.send_mail(self.id)
# 
#         self.state = 'approved'
        return True

    @api.multi
    def action_reject(self):
        self.ensure_one()
        return {
            'name':_("Reject %s" % self.name),
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
            old_user =  self.env['res.users'].search([('partner_id', '=', par.id)])
            if len(old_user) == 0:
                new_user = self.env['res.users'].create({'login': par.email,
                                                         'partner_id': par.partner_id.id,
                                                         'participant_id' : par.id,
                                                         'groups_id': [(4, self.env.ref('base.group_portal').id)]})
                new_user.with_context({'create_user': True}).action_reset_password()
            else:
                old_user.action_reset_password()
                
    @api.multi
    def action_deregister_participant(self):
        for par in self:
            old_user =  self.env['res.users'].search([('partner_id', '=', par.id)])
            if len(old_user):
                old_user.write({'active': False})
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
            for comm in self.env['campos.committee'].search([('contact_id', '=', par.partner_id.id)]):
                comm.contact_id = False
                
    
    @api.multi
    @api.depends('partner_id.name')
    def name_get(self):

        result = []
        for part in self:
            result.append((part.id, part.partner_id.display_name))

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
        coms =  self.env['campos.committee'].search([('message_follower_ids', '=', self.env.user.partner_id.id)])
        
        return ['|', 
                '&', ('registration_id', 'in', regs.ids),('state', 'in',['draft','rejected']),
                '&', ('committee_id', 'in', coms.ids),('state', 'in',['sent']),
                ]
        
    def message_get_suggested_recipients(self, cr, uid, ids, context=None):
        recipients = super(EventParticipant, self).message_get_suggested_recipients(cr, uid, ids, context=context)
        for lead in self.browse(cr, uid, ids, context=context):
                if lead.partner_id:
                    self._message_add_suggested_recipient(cr, uid, recipients, lead, partner=lead.partner_id, reason=_('Participant'))
        return recipients