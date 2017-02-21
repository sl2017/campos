# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
import string, random

SMS_CONFIRM_MAX_TRIES = 3
SMS_CONFIRM_CODE_LENGTH = 6

class SmsConfirmedNumber(models.Model):
    _name = 'sms.confirmed_number'

    user_id = fields.Many2one('res.users', string='User', readonly=True)
    number = fields.Char('Number', size=20)
    state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting'), ('confirmed', 'Confirmed')], default='draft', readonly=True)

    confirm_code = fields.Char('Confirm code', size=SMS_CONFIRM_CODE_LENGTH, groups='base.erp_manager')
    confirm_tries = fields.Integer('Confirm Tries left', readonly=True)

    _sql_constraints = [('sms_confirm_number_unique', 'UNIQUE (user_id, number)', 'A confirmation for this user/number has already been created')]

    @api.model
    def default_get(self, fields):
        result = super(SmsConfirmedNumber, self).default_get(fields)
        result['user_id'] = self.env.uid
        result['number'] = self.env.user.partner_id.mobile_clean
        return result

    @api.multi
    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, '%s (%s)' % (r.number, _('Confirmed') if r.state == 'confirmed' else _('Not confirmed'))))
        return result

    def _generate_code(self):
        '''
        Return SMS_CONFIRM_CODE_LENGTH digit random uppercase string
        '''
        return ''.join(random.choice(string.ascii_uppercase) for _ in range(SMS_CONFIRM_CODE_LENGTH))

    @api.model
    def _clean(self, number):
        # Clean number
        allowed_chars = '+0123456789'
        delete_table  = string.maketrans(allowed_chars, ' ' * len(allowed_chars))
        # Delete illegal chars
        mobile_clean = str(number).translate(None, delete_table)
        # Make sure number starts with country code
        if len(mobile_clean) > 0 and mobile_clean[0] != '+':
            # @todo: Use country prefix from partner's country setting 
            mobile_clean = '+45' + mobile_clean
        # Number can only have '+' as the first char - and length must be less than 18 chars
        # (two numbers will be at least 2 * 8 + 3 = 19 chars (3 for '+45')
        if '+' in mobile_clean[1:] or len(mobile_clean) > 18:
            mobile_clean = False
        return mobile_clean

    @api.model
    def find_or_create(self, number):
        '''
        Find a number - or create an new confirm record if it does not exist
        '''
        number = self._clean(number)
        nr_id = self.search([('number', '=', number), ('user_id', '=', self.env.uid)]) 
        if nr_id:
            return nr_id[0]
        return self.create({'user_id': self.env.uid,
                            'number': number})

    def send_confirm_code(self, data):
        if self.state == 'confirmed':
            raise exceptions.Warning(_('You have already confirmed the number %s') % self.number)

        self.number = self._clean(self.number)

        # Change state and reset tries counter
        self.sudo().state = 'waiting'
        code = self._generate_code()
        self.sudo().confirm_code = code
        self.sudo().confirm_tries = SMS_CONFIRM_MAX_TRIES
        # Send the code by SMS
        data.mobile_to = self.number
        old_text = data.text
        data.text = _('Enter this code to confirm your mobile number: %s') % code
        log_text = _('Enter this code to confirm your mobile number: %s') % ('*' * SMS_CONFIRM_CODE_LENGTH)
        client = self.env['sms.smsclient']
        client.with_context(sms_send_direct=True, sms_log_overwrite=log_text)._send_message(data)
        data.text = old_text

    def check_code(self, code):
        if not code:
            raise exceptions.Warning(_('Please enter the verification code that was send to your phone by SMS.'))

        # Check if user has tried too many times...
        self.confirm_tries = self.confirm_tries -1
        if self.confirm_tries < 0:
            raise exceptions.Warning(_('The confirmation code has expired, because you have tried more than %d times. You may request a new code and try again.') % SMS_CONFIRM_MAX_TRIES)
        # Commit the count before we continue!
        self.env.cr.commit()

        #  Cannot read directly with "code = self.sudo().confirm_code" !
        confirm_code = self.sudo().read(fields=['confirm_code'])[0]['confirm_code']
        if str(code).upper() != str(confirm_code):
            # @TODO: "confirm_tries" is not updated in the user interface, when we throw an exception...
            raise exceptions.Warning(_('The code was not entered correct. Please note that the code contains only letters (no digits).'))

        self.state = 'confirmed'
        self.env.user.sms_last_sender = self
