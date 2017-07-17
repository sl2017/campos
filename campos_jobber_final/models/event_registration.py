# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class EventRegistration(models.Model):

    _inherit = 'event.registration'
    
    jobber_accomodation_ids = fields.One2many('campos.jobber.accomodation', 'registration_id', 'Jobber Accomonodation')
    jobber_pay_for_ids = fields.One2many('campos.event.participant', 'registration_id', 'Jobbers to Pay for', domain=[('staff', '=', True)])
    jobber_catering_ids = fields.One2many('campos.jobber.canteen', 'registration_id', 'Jobbers Catering')
    
    @api.one
    @api.returns('ir.ui.view')
    def get_formview_id(self):
        """ Update form view id of action to open the participant """
        view_ref = False
        if self.env.user.has_group('campos_event.group_campos_committee') or self.env.user.has_group('campos_event.group_campos_info'):
             view_ref = 'campos_final_registration.view_form_finalregistration_admin'
        else:
             view_ref = 'campos_final_registration.view_form_finalregistration_gl'
        if view_ref:
            return self.env.ref(view_ref)
        else:
            return False
    
