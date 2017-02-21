# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


SMS_MAX_SENDER_LENGTH = 10

class part_sms(models.TransientModel):
    _inherit = 'part.sms'

    # The organization that the SMS are charged to
    # @TODO: User must have SMS access to the organizations
    organization_id = fields.Many2one('campos.committee', string='Paying Committee', required=True,
                                      domain="[('sms_max_monthly_cost', '>', 0),('user_sms_ids', 'in', uid)]",
                                      context={'name_with_sms_budget': True})

    # The sender of the SMS (can be text or a confirmed number)
    # If a number is selected, it will also be copied to sender_text 
    sender_id = fields.Many2one('sms.confirmed_number', string='Confirmed sender numbers')
    sender_text = fields.Char('Sender', size=15)
    user_has_confirmed_numbers = fields.Boolean('User has confirmed numbers')
    sender_is_number = fields.Boolean(compute='_compute_sender_is_number')
    sender_state = fields.Selection(related='sender_id.state', string='Number state')
    # Fields used to confirm sender
    confirm_tries = fields.Integer(related='sender_id.confirm_tries')
    confirm_code = fields.Char('Confirm code', size=10) # Field for the user to enter the code!
    confirm_price = fields.Float('Confirm price', compute='_compute_confirm_price')

    # The actual content of the SMS
    text = fields.Text('Text', required=False)

    # Receivers
    receiver_ids = fields.Many2many('res.partner', 'part_sms_res_partner_rel', string='Receivers')
    receivers_count = fields.Integer('Total receivers with a valid mobile number', compute='_compute_receivers_count')
    receivers_foreign_count = fields.Integer('Receivers with a foreign mobile number', compute='_compute_receivers_count')
    total_price = fields.Float('Total price', compute='_compute_receivers_count')

    # SMS allowed?
    def _sms_allowed(self):
        allowed_dbs = self.env['ir.config_parameter'].sudo().get_param('sms_allowed_dbs', '')
        return self.env.cr.dbname in allowed_dbs.split(',')

    sms_allowed = fields.Boolean('SMS allowed', compute='_compute_sms_allowed', default=_sms_allowed)

    @api.model
    def default_get(self, fields):
        result = super(part_sms, self).default_get(fields)
        if self.env.user.comm_sms_ids:
            result['organization_id'] = self.env.user.comm_sms_ids[0].id

        # Build receivers lists
        model = self.env.context.get('active_model', 'res.partner')
        if model != 'res.partner':
            record_ids = self.env[model].browse(self.env.context.get('active_ids', []))
            partner_field = 'object.' + self.env.context.get('partner_id_field', 'partner_id')
            receivers = set()
            for r_id in record_ids:
                _logger.info('Adding: %d', r_id.id)
                receivers.add(eval(partner_field, {'object': r_id}).id)
                
            result['receiver_ids'] = self.env['res.partner'].sudo().search([('id', 'in', list(receivers))], order='name').ids
        else:
            result['receiver_ids'] = self.env.context.get('active_ids', [])

        # Set default sender
        sms_senders = self.env['sms.confirmed_number'].search([], order='state, number')
        result['sender_id'] = self.env.user.sms_last_sender.id or \
            sms_senders[0].id if sms_senders else False
        if not result['sender_id']:
            result['sender_text'] = _('SL2017')

        result['user_has_confirmed_numbers'] = len(sms_senders) > 0

        _logger.info('RESULT: %s', result)
        return result

    @api.multi
    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, _('Send SMS')))
        return result

    @api.one
    @api.depends('text')
    def _compute_receivers_count(self):
        '''
        Compute counts and price for the total SMS sending
        '''
        config = self.env['ir.config_parameter'].sudo()
        np = config.get_param('sms_national_prefix', '')
        self.receivers_count = len(self.receiver_ids.filtered('mobile_clean'))
        self.receivers_foreign_count = len(self.receiver_ids.filtered(lambda r: r.mobile_clean and r.mobile_clean[0:3] != np))
        self.total_price = sum(self.env['sms.smsclient.queue'].get_sell_price(r.mobile_clean, self.text) for r in (self.receiver_ids.filtered('mobile_clean')))


    @api.one
    @api.depends('sender_text')
    def _compute_confirm_price(self):
        self.confirm_price = self.env['sms.smsclient.queue'].get_sell_price(self.sender_text) if self.sender_text else 0

    @api.one
    @api.depends('sender_text')
    def _compute_sender_is_number(self):
        self.sender_is_number = self.sender_text and any(char.isdigit() for char in self.sender_text) and not any(char.isalpha() for char in self.sender_text)

    @api.one
    def _compute_sms_allowed(self):
        self.sms_allowed = self._sms_allowed()

    @api.onchange('sender_id')
    def _update_sender_id(self):
        if self.sender_id:
            self.sender_text = self.sender_id.number

    @api.onchange('sender_text')
    def _update_sender_text(self):
        if self.sender_text:
            if self.sender_is_number:
                # Sender is a number
                self.sender_text = self.env['sms.confirmed_number']._clean(self.sender_text)
                self.sender_id = self.env['sms.confirmed_number'].search([('number', '=', self.sender_text), ('user_id', '=', self.env.uid)])
            else:
                # Sender is a text
                if len(self.sender_text) > SMS_MAX_SENDER_LENGTH:
                    raise exceptions.ValidationError(_('When sender is a text string, it cannot be more than %d chars.') % SMS_MAX_SENDER_LENGTH)
                self.sender_id = False

    @api.constrains('organization_id')
    def _check_organization_id(self):
        if not self.env.user.can_sms_organization(self.organization_id):
            raise exceptions.ValidationError(_('You are not allowed to send SMSs charged to %s') % self.organization_id.name)

    @api.multi
    def action_send_confirm_code(self):
        self.ensure_one()

        if not self.sender_id:
            self.sender_id = self.env['sms.confirmed_number'].find_or_create(self.sender_text)
        self.with_context(sms_payer_organization_id=self.organization_id.id).sender_id.send_confirm_code(self)

        self.confirm_code = False # Clear currently entered confirm code in the wizard

        # Re-open current wizard
        return {'name': _('Send SMS'),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'part.sms',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'res_id': self.id}

    @api.multi
    def action_check_confirm_code(self):
        self.ensure_one()

        code = self.confirm_code # Save the wizard's entered code
        self.confirm_code = False # Reset the wizard's code
        self.env.cr.commit() # Commit in case of exceptions!
        self.sender_id.check_code(code) # Test with saved code

        # Re-open current wizard
        return {'name': _('Send SMS'),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'part.sms',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'res_id': self.id}


    @api.multi
    def action_confirm_number(self):
        self.ensure_one()

        if self.sender_id:
            # Confirm existing unconfirmed number
            self.sender_id.write({'return_res_id': self.id,
                                   'return_res_model': 'part.sms'})
            return {'name': _('Confirm mobile number'),
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_model': 'sms.confirmed_number',
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'res_id' : self.sender_id.id}
        else:
            # Add new unconfirmed number
            return self.action_add_number()
            # @TODO Remove next unused lines
            return {'name': _('Confirm mobile number'),
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_model': 'sms.confirmed_number',
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'context': {'default_return_res_id': self.id,
                                'default_return_res_model': 'part.sms'}
                     }

    @api.multi
    def action_add_number(self):
        self.ensure_one()

        return {'name': _('Confirm mobile number'),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'sms.confirmed_number',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': {'default_return_res_id': self.id,
                            'default_return_res_model': 'part.sms'}
                 }

    @api.multi
    def sms_mass_send(self):
        self.ensure_one()

        if not self.text:
            raise exceptions.ValidationError(_('Please enter a text to send'))

        gateway_id = self.env['sms.smsclient'].search([])[0]
        if not gateway_id:
            raise exceptions.Warning(_('No Gateway Found'))

        sms_master_id = self.env['sms.master'].suspend_security().create({'organization_id': self.organization_id.id,
                                                                          'sender_text': self.sender_text,
                                                                          'msg': self.text})

        data = {'gateway_id': gateway_id.id,
                'sms_master_id': sms_master_id.id,
                'state': 'draft',
                'msg': self.text}

        for r_id in self.receiver_ids:
            data['mobile'] = r_id.mobile_clean
            if data['mobile']:
                self.env['sms.smsclient.queue'].with_context(sms_log_overwrite=False).create(data)

        # Price is NOT computed automatically
        sms_master_id._compute_price()

        return True
