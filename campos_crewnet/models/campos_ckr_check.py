# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposCkrCheck(models.Model):

    _inherit = 'campos.ckr.check'

    @api.multi
    def action_approve(self):
        super(CamposCkrCheck, self).action_approve()
        self.participant_id.crewnet_ok = True
        self.participant_id.message_post(body=_("Crewnet auto accepted on CKR approval."))
