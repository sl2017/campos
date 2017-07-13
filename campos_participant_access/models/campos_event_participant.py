# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, exceptions, _

from xml.etree import ElementTree as ET
from moodle_rest_api import MDL

class CamposEventParticipant(models.Model):

    _inherit = 'campos.event.participant'

    clc_user_needed = fields.Boolean('CLC User needed', compute='_compute_clc_user_needed')
    clc_state = fields.Selection([('required', 'Not started'),
                                  ('enrolled', 'Started'),
                                  ('passed', 'Completed')], string='CLC state')
    clc_userid = fields.Integer('Moodle Internal User ID')
    clc_grade = fields.Char('CLC Total Grade')
    
    
    def moodle_get_grade(self):
        mdl = MDL()

        server = eval(self.env['ir.config_parameter'].get_param('campos.clc_server'))
        params = {'userid': self.clc_userid}

        grades = mdl.get_course_grades(server, params)
        rows = ET.ElementTree(ET.fromstring(grades))
        for row in rows.getroot():
            for key0 in row:
                if key0.tag == 'KEY' and key0.attrib.get('name') == 'grades':
                    for multiple in key0:
                        for single in multiple:
                            for key in single:
                                if key.tag == 'KEY' and key.attrib.get('name') == 'grade':
                                    val = dict((e.tag, e.text) for e in key)
                                    self.clc_grade = (val['VALUE'])
                                    if self.clc_grade == '400.00':
                                        self.clc_state = 'passed'


    @api.model
    def moodle_get_course_users(self):
        mdl = MDL()
        course = eval(self.env['ir.config_parameter'].get_param('campos.clc_course_id'))
        server = eval(self.env['ir.config_parameter'].get_param('campos.clc_server'))
        params = {'courseid': course}
        mdl_users = mdl.get_course_users(server, params)
        rows = ET.ElementTree(ET.fromstring(mdl_users))
        for row in rows.getroot():
            for single in row:
                moodle_id = False
                moodle_username = False
                for key in single:
                    if key.tag == 'KEY' and key.attrib.get('name') == 'id':
                        val = dict((e.tag, e.text) for e in key)
                        moodle_id = val['VALUE']
                    if key.tag == 'KEY' and key.attrib.get('name') == 'username':
                        val = dict((e.tag, e.text) for e in key)
                        moodle_username = val['VALUE']
                if moodle_id and moodle_username:
                    usr = self.env['res.users'].search([('login', '=', moodle_username)])
                    if usr:
                        part = False
                        if not usr.participant_id:
                            part = self.env['campos.event.participant'].search([('partner_id', '=', usr.partner_id.id)])
                            if part:
                                usr.participant_id = part
                        else:
                            part = usr.participant_id
                        if not part:
                            part = self.env['campos.event.participant'].search([('email', '=', moodle_username),('state', '!=', 'deregistered'), ('camp_age', '>=', 18)])
                            
                        if part and len(part) == 1 and not part.clc_userid:
                            part.clc_userid = moodle_id
                            part.clc_state = 'enrolled'
                        part.moodle_get_grade()
    
    @api.multi
    def _compute_clc_user_needed(self):
        for p in self:
            p.clc_user_needed = False
            if p.camp_age >= 18 and p.registration_id.group_country_code2 != "DK":
                if not self.env['res.users'].search(['|',('partner_id', '=', p.partner_id.id),('login', '=', p.email)]):
                    p.clc_user_needed = True

    @api.multi
    def action_create_clc_user(self):
        self.ensure_one()
        self.create_clc_user()

    def create_clc_user(self, silent=False):
        if not self.email:
            if silent:
                return
            raise exceptions.Warning(_('Email adress missing for %s') % (self.name))
        if self.env['res.users'].search([('partner_id', '=', self.partner_id.id)]):
            if silent:
                return
            raise exceptions.Warning(_('User already created for %s') % (self.name))
        if self.env['res.users'].search([('login', '=', self.email)]):
            if silent:
                return
            raise exceptions.Warning(_('User already created for this email %s') % (self.email))
        self.email = self.email.lower()
        self.partner_id.lang='en_US'
        self.env['res.users'].sudo().with_context(template_ref='campos_participant_access.clc_signup_email').create({'login': self.email,
                                                            'partner_id': self.partner_id.id,
                                                            'groups_id': [(4, self.env.ref('campos_participant_access.group_campos_participant').id)],
                                                         })
        if not self.clc_state:
            self.clc_state = 'required'
