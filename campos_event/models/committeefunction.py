# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of CampOS Event,
#     an Odoo module.
#
#     Copyright (c) 2015 Stein & Gabelgaard ApS
#                        http://www.steingabelgaard.dk
#                        Hans Henrik Gaelgaard
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

# from openerp.addons.base_geoengine import geo_model
# from openerp.addons.base_geoengine import fields
# from openerp import api
from openerp import fields, api
from openerp.addons.base_geoengine import geo_model, fields as geo_fields


import logging

_logger = logging.getLogger(__name__)

class CampCommitteeFunction(geo_model.GeoModel):

    """ Committee Participant Function"""
    _description = 'Committee Functions'
    _name = 'campos.committee.function'
    _order = 'committee_id'
    _inherit = 'mail.thread'
    
    name = fields.Char()
    participant_id = fields.Many2one('campos.event.participant', ondelete='cascade', string="Participant")
    committee_id = fields.Many2one('campos.committee',
                                   'Committee',
                                   ondelete='cascade')
    function_type_id = fields.Many2one('campos.committee.function.type', string="Function", ondelete='cascade')
    job_id = fields.Many2one('campos.job',
                         'Job annonce',
                         ondelete='set null')
    email = fields.Char('Email', related='participant_id.partner_id.email')
    mobile = fields.Char('Mobile', related='participant_id.partner_id.mobile')
    geo_point = geo_fields.GeoPoint('Addresses coordinate', related='participant_id.partner_id.geo_point')
    com_contact = fields.Text(string='Contact', related='committee_id.par_contact_id.complete_contact')
    active = fields.Boolean(default=True)
    job_title_id = fields.Many2one('campos.committee.job.title',
                         'Job Title',
                         ondelete='set null')
    
    sharepoint_mail = fields.Selection([('yes', 'Yes'),('no', 'No')], string='Sharepoint mail wanted')
    sharepoint_mailaddress = fields.Char('Sharepoint mail address', related='participant_id.sharepoint_mailaddress')
    zexpense_access_wanted = fields.Selection([('yes', 'Yes'),('no', 'No')], string='zExpense access wanted')
    

        
    @api.multi
    def write(self, vals):
        _logger.info("New func Write Entered %s", vals.keys())
        ret =  super(CampCommitteeFunction, self).write(vals)
        for app in self:
            if vals.has_key('new_func'):
                if app.sharepoint_mail:
                    app.participant_id.sharepoint_mail = True if app.sharepoint_mail == 'yes' else False
                if app.zexpense_access_wanted:
                    app.participant_id.zexpense_access_wanted = True if app.zexpense_access_wanted == 'yes' else False
                _logger.info("New func mail %s %s", app.committee_id.name, app.participant_id.name)
                template = app.committee_id.template_id
                assert template._name == 'email.template'
                try:
                    template.send_mail(app.participant_id.id)
                except:
                    _logger.info("New func mail %s %s FAILED", app.committee_id.name, app.participant_id.name)
                    pass
                if app.participant_id.sharepoint_mail and not app.participant_id.sharepoint_mail_created:
                    template = self.env.ref('campos_event.request_sharepoint')
                    assert template._name == 'email.template'
                    try:
                        template.send_mail(app.participant_id.id)
                    except:
                        pass
                    app.participant_id.sharepoint_mail_requested = fields.Datetime.now()
                else:
                    if app.participant_id.zexpense_access_wanted:
                        if not app.participant_id.zexpense_access_created:
                            template = self.env.ref('campos_event.request_zexpense')
                            assert template._name == 'email.template'
                            try:
                                template.send_mail(app.participant_id.id)
                            except:
                                pass
                            app.participant_id.zexpense_access_requested = fields.Datetime.now()
                        else:
                            template = self.env.ref('campos_event.request_zexpense_change')
                            assert template._name == 'email.template'
                            try:
                                template.send_mail(app.participant_id.id)
                            except:
                                pass
                    old_user =  self.env['res.users'].sudo().search([('participant_id', '=', app.participant_id.id)])
                    if len(old_user) == 0:
                        app.participant_id.action_create_user()
                app.participant_id.write({'committee_id': False,
                                          'job_id': False,
                                          'my_comm_contact': False,
                                          'state': 'approved'
                                          })
        return ret
    
    @api.multi
    def action_open_participant(self):
        self.ensure_one()
        return {
            'name': self.participant_id.name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'campos.event.participant',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'domain': '[]',
            'res_id': self.participant_id.id,
            'context': {'active_id': self.participant_id.id}, 
            }
