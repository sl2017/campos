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


class EventRegistration(models.Model):

    '''
    Scout Group or Jobber "Head" registration

    '''
    _inherit = 'event.registration'

    participant_ids = fields.One2many(
        'campos.event.participant',
        'registration_id')

    name = fields.Char(related='partner_id.name', store=True)
    scoutgroup = fields.Boolean(related='partner_id.scoutgroup')
    staff = fields.Boolean(related='partner_id.staff')
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


class EventParticipant(models.Model):

    '''
    Detail participant/Jobber Info
    '''
    _name = 'campos.event.participant'
    _description = 'Event Participant'
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict') # Relation to inherited res.partner
    registration_id = fields.Many2one('event.registration')

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
    state = fields.Selection([('draft', 'Received'),
                              ('sent', 'Sent to committee'),
                              ('approved', 'Approved by the committee'),
                              ('rejected', 'Rejected')],
                             'Approval Procedure',
                             track_visibility='onchange', default='draft')

    job_id = fields.Many2one('campos.job',
                             'Job',
                             ondelete='set null')
    newsletter  = fields.Boolean()
    
    sharepoint_mail = fields.Boolean('Sharepoint mail wanted')
    sharepoint_mailaddress = fields.Char()
    sharepoint_mail_created = fields.Date()
    
    zexpense_access_wanted = fields.Boolean('zExpense access wanted')
    zexpense_access_created = fields.Date()
    
    workwish = fields.Text('Want to work with')
    profession = fields.Char(
        'Profession',
        size=64,
        help='What do you do for living')

    par_internal_note = fields.Text('Internal note')

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        template = self.env.ref('campos_event.new_staff_member')
        assert template._name == 'email.template'

        template.send_mail(self.id)

        self.state = 'sent'
        return True

    @api.multi
    def action_approve(self):
        self.ensure_one()
        template = self.committee_id.template_id
        if template:
            template.send_mail(self.id)

        self.state = 'approved'
        return True

    def action_reject(self):
        self.ensure_one()
        self.state = 'rejected'
        return True

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
        