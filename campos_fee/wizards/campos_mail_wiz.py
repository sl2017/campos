# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError

import logging
_logger = logging.getLogger(__name__)

@job(default_channel='root.inv')
def do_delayed_mail(session, model, reg_id, template_id):
    _logger.info("DO REG: %d %d", reg_id, template_id)
    template = session.env['email.template'].browse(template_id)
    if template.exists():
        template.with_context(lang=session.env.user.lang).send_mail(reg_id)


class CamposMailWiz(models.TransientModel):

    _name = 'campos.mail.wiz'

    name = fields.Char()
    
    @api.model
    def _default_reg_ids(self):
        res = False
        context = self.env.context
        if (context.get('active_model') == 'event.registration' and
                context.get('active_ids')):
            res = context['active_ids']
        return res

    reg_ids = fields.Many2many(comodel_name='event.registration',
                               string='Registrations',
                               default=_default_reg_ids)
    template_id = fields.Many2one('email.template', 'Template')
    
    @api.multi
    def doit(self):
        for wizard in self:
            session = ConnectorSession.from_env(self.env)
            for reg in wizard.reg_ids:
                do_delayed_mail.delay(session, 'event.registration', reg.id, wizard.template_id.id)
                
        