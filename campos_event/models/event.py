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
                if participant[0].jobfunc_ids:
                    row['s2x'] = participant[0].jobfunc_ids[0].committee_id.root_name
            if reg.reg_survey_input_id and reg.state != 'cancel':
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
        ('deregistered', 'Deregistered')
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
        'Municipality', related="partner_id.municipality_id")

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
    subcamp_id = fields.Many2one('campos.subcamp', 'Sub Camp')

    subcamp_function_view_ids = fields.One2many(related='subcamp_id.committee_id.part_function_view_ids', string='Sub Camp Resp')
    part_function_view_ids = fields.One2many(related='camp_area_id.committee_id.part_function_view_ids', string='Coordinators')
    reg_view_ids = fields.One2many(related='camp_area_id.reg_view_ids', string='Troops')

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
        
    @api.multi
    @api.depends('name', 'organization_id')
    def name_get(self):
        result = []
        show_org = self.env.context.get('show_organization', False)
        _logger.info('SHOW ORG: %s', show_org)
        for reg in self:
            if show_org and reg.organization_id:
                result.append((reg.id, '%s (%s)' % (reg.name, reg.organization_id.name)))
            else:
                result.append((reg.id, reg.name)) 
        return result

