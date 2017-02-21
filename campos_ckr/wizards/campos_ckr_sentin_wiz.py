# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)


class CamposCkrSentinWiz(models.TransientModel):

    _name = 'campos.ckr.sentin.wiz'

    message = fields.Text(
        string="Message",
        readonly=True
        )
    
    ckr_ids = fields.Many2many('campos.ckr.check')

    @api.multi
    def action_mark_req(self):
        for wizard in self:
            for ckr in wizard.ckr_ids:
                _logger.info('STATE: %s', ckr.state)
                if ckr.state == 'timeout':
                    ckr.action_re_req_ckr()
                else:
                    ckr.action_req_ckr()
        