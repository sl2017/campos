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
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from urlparse import urljoin
import werkzeug

from openerp.addons.base_geoengine import geo_model
from openerp import models, fields, api
from openerp.tools.translate import _

import base64
try:
    import xlwt
except ImportError:
    xlwt = None
import re
from cStringIO import StringIO

import logging
_logger = logging.getLogger(__name__)


def random_token():
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.SystemRandom().choice(chars) for i in xrange(20))

class EventEvent(models.Model):

    '''
    Event ID

    '''
    _inherit = 'event.event'

    survey_id = fields.Many2one('survey.survey', 'Signup survey')
    attachment_id = fields.Many2one('ir.attachment', string="Attachments")
    camp_area_ids = fields.One2many(
        'campos.camp.area',
        'event_id', string="Rooms/Camp Areas")

    regform = fields.Selection([('register_free', 'Std. Free Register'),
                                ('register_meeting', 'Meeting register (with survey)'),
                                ('intl_groups', 'International Groups')], string='Registration Form', default='register_meeting')

    @api.multi
    def action_export_survey(self):
        fields = []
        self.ensure_one()

        # Standard field
        fields = [{'id': "s1", 'fieldname': 'Navn'},
                  {'id': 's1s', 'fieldname': 'Status'},
                  {'id': "s2", 'fieldname': 'Udvalg'},
                  {'id': "s2x", 'fieldname': 'Udvalg Kort'},
                  {'id': "s3", 'fieldname': 'Funktion'},
                  {'id': "s3r", 'fieldname': 'Rum'},
                  {'id': "s4", 'fieldname': 'adresse'},
                  {'id': 's5', 'fieldname': 'Postnr'},
                  {'id': 's6', 'fieldname': 'By'},
                  {'id': 's7', 'fieldname': 'Email'},
                  {'id': 's7p', 'fieldname': 'Privat Email'},
                  {'id': 's8', 'fieldname': 'Tlf'},
                  {'id': 's9', 'fieldname': 'Mobil'},
                  {'id': 's10', 'fieldname': 'Opdateret'},
                  ]
        for page in self.survey_id.page_ids:
            for q in page.question_ids:
                if q.type == 'multiple_choice':
                    for l in q.labels_ids:
                        fields.append({'q': q,
                                       'label': l,
                                       'id': "%d-%d" % (q.id, l.id),
                                       'fieldname': "%s/%s" % (q.question, l.value)})
                else:
                    fields.append({'q': q,
                                   'id': "%d" % (q.id),
                                   'fieldname': "%s" % (q.question)})
                if q.comments_allowed:
                    fields.append({'q': q,
                                   'id': "%d-comm" % (q.id),
                                   'fieldname': "%s" % (q.comments_message)})

        rows = []
        for reg in self.registration_ids:
            # if reg.state == 'cancel':
            #    continue
            row = {}
            row['s1'] = reg.partner_id.name
            row['s3r'] = reg.camp_area_id.name
            row['s4'] = ''.join(filter(None, [reg.partner_id.street, reg.partner_id.street2]))
            row['s5'] = reg.partner_id.zip
            row['s6'] = reg.partner_id.city
            row['s7'] = reg.partner_id.email
            row['s8'] = reg.partner_id.phone
            row['s9'] = reg.partner_id.mobile
            row['s1s'] = reg.state
            participant = self.env['campos.event.participant'].search([('partner_id', '=', reg.partner_id.id)])
            if participant:
                row['s7p'] = participant[0].private_mailaddress
                comm_list = None
                func_list = None
                for j in participant[0].jobfunc_ids:
                    comm_list = '|'.join(filter(None, [comm_list, j.committee_id.display_name]))
                    func_list = '|'.join(filter(None, [func_list, j.function_type_id.name]))
                row['s2'] = comm_list
                row['s3'] = func_list
                if participant[0].jobfunc_ids[0]:
                    row['s2x'] = participant[0].jobfunc_ids[0].committee_id.root_name
            if reg.reg_survey_input_id:
                row['s10'] = reg.reg_survey_input_id.write_date
                for ans in reg.reg_user_input_line_ids:
                    if ans.question_id.comments_allowed and ans.answer_type == 'text':
                        row['%d-comm' % (ans.question_id.id)] = ans.value_text
                    if ans.question_id.type == 'multiple_choice' and ans.value_suggested:
                        row['%d-%d' % (ans.question_id.id, ans.value_suggested.id)] = 'X'
                    elif ans.question_id.type == 'simple_choice' and ans.value_suggested:
                        row['%d' % (ans.question_id.id)] = ans.value_suggested.value
                        _logger.info('%s ROW simple: %d %s', row['s1'], ans.question_id.id, ans.value_suggested.value)
                    elif ans.question_id.type in ['free_text', 'textbox', 'text'] and ans.value_text:
                        row['%d' % (ans.question_id.id)] = ans.value_text
                        _logger.info('%s ROW text: %d %s', row['s1'], ans.question_id.id, ans.value_text)
                    elif ans.question_id.type in ['free_text'] and ans.value_free_text:
                        row['%d' % (ans.question_id.id)] = ans.value_free_text
                        _logger.info('%s ROW FREE text: %d %s', row['s1'], ans.question_id.id, ans.value_free_text)
            rows.append(row)

        data = base64.encodestring(self.from_data(fields, rows))
        attach_vals = {
                 'name':'%s.xls' % (self.name),
                 'datas':data,
                 'datas_fname':'%s.xls' % (self.name),
                 }

        doc_id = self.env['ir.attachment'].create(attach_vals)
        if self.attachment_id :
            try :
                self.attachment_id.unlink()
            except :
                pass
        self.write({'attachment_id':doc_id.id})
        return {
            'type' : 'ir.actions.act_url',
            'url':   '/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=%s' % (doc_id.id),
            'target': 'self',
            }

    def from_data(self, fields, rows):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        header_title = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;align:horizontal left, indent 1,vertical center")
        for i, field in enumerate(fields):
            worksheet.write(0, i, field['fieldname'], header_title)
            worksheet.col(i).width = 8000  # around 220 pixels
        base_style = xlwt.easyxf('align: horizontal left,wrap yes,indent 1,vertical center')
        date_style = xlwt.easyxf('align: horizontal left,wrap yes, indent 1,vertical center', num_format_str='YYYY-MM-DD')
        datetime_style = xlwt.easyxf('align: horizontal left,wrap yes,indent 1,vertical center', num_format_str='YYYY-MM-DD HH:mm:SS')
        worksheet.row(0).height = 400
        for row_index, row in enumerate(rows):
            worksheet.row(row_index + 1).height = 350
            for cell_index, field in enumerate(fields):
                cell_style = base_style
                if row.has_key(field['id']) and field['id']:
                    worksheet.write(row_index + 1, cell_index, row[field['id']], cell_style)
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return data


class EventRegistration(models.Model):

    '''
    Scout Group or Jobber "Head" registration

    '''
    _inherit = 'event.registration'

    participant_ids = fields.One2many(
        'campos.event.participant',
        'registration_id', string="Participants")

    state = fields.Selection([
        ('draft', 'Unconfirmed'),
        ('cancel', 'Cancelled'),
        ('open', 'Confirmed'),
        ('done', 'Attended'),
    ], string='Status', default='draft', readonly=True, copy=False,
        track_visibility='onchange')

    name = fields.Char(related='partner_id.name', store=True)
    scoutgroup = fields.Boolean(related='partner_id.scoutgroup')
    staff = fields.Boolean(related='partner_id.staff')
    staff_qty_pre_reg = fields.Integer('Number of Staff - Pre-registration')
    scout_qty_pre_reg = fields.Integer('Number of Scouts - Pre-registration')
    leader_qty_pre_reg = fields.Integer('Number of Leaders - Pre-registration')
    country_id = fields.Many2one('res.country', 'Country')
    organization_id = fields.Many2one(
        'campos.scout.org',
        'Scout Organization')

    scout_division = fields.Char('Division/District', size=64)
    natorg = fields.Char('National Organization', size=64)
    intl_org = fields.Many2one(
        'campos.scout.org',
        'Scout Organization')
    friendship = fields.Char('Friendship group', size=64)
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

    reg_survey_input_id = fields.Many2one('survey.user_input', 'Registration survay')
    reg_user_input_line_ids = fields.One2many(related='reg_survey_input_id.user_input_line_ids')

    camp_area_id = fields.Many2one(
        'campos.camp.area',
        'Room/Camp Area',
        select=True,
        ondelete='set null')

    @api.multi
    def action_edit_survey_response(self):
        fields = []
        self.ensure_one()
        if not self.reg_survey_input_id:
            self.reg_survey_input_id = self.env['survey.user_input'].create({'survey_id': self.event_id.survey_id.id,
                                                                             'partner_id': self.partner_id.id})
        self.reg_survey_input_id.state = 'new'
        return {'type': 'ir.actions.act_url',
                'url': '/survey/fill/%s/%s' % (self.event_id.survey_id.id, self.reg_survey_input_id.token),
                'nodestroy': True,
                'target': 'new' }

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
    staff_qty_pre_reg = fields.Integer(related='registration_id.staff_qty_pre_reg', string='Number of Staff - Pre-registration')
    reg_organization_id = fields.Many2one(
        'campos.scout.org',
        'Scout Organization', related='registration_id.organization_id', store=True)
    scout_color = fields.Char('Scout Org Color', related='registration_id.organization_id.color')

    # Scout Leader Fiedls

    appr_leader = fields.Boolean('Leder godkendt', track_visibility='onchange')
    att_received = fields.Boolean(
        'Attest modtaget',
        track_visibility='onchange')
    leader = fields.Boolean('Is Leader')
    birthdate = fields.Date('Date of birth')
    age = fields.Integer('Age', compute='_compute_age', store=True)
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
                              ('draft', 'Received'),
                              ('standby', 'Standby'),
                              ('sent', 'Sent to committee'),
                              ('approved', 'Approved by the committee'),
                              ('rejected', 'Rejected'),
                              ('deregistered', 'Deregistered')],
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
    def _compute_context_age(self):
        for part in self:
            part.context_age = part.age_on_date(self.env.context.get('context_age_date')) if part.birthdate else False

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
                new_user = self.env['res.users'].sudo().create({'login': par.email,
                                                         'partner_id': par.partner_id.id,
                                                         'participant_id' : par.id,
                                                         # 'groups_id': [(4, self.env.ref('base.group_portal').id)]
                                                         })
                # new_user.with_context({'create_user': True}).action_reset_password()

            else:
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

