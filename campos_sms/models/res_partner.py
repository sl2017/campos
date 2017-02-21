# -*- coding: utf-8 -*-

from openerp import models, fields, api
import string

class ResPartner(models.Model):
    _inherit = ['res.partner']

    mobile_clean = fields.Char(compute='_compute_mobile_clean')

    @api.multi
    @api.depends('mobile')
    def _compute_mobile_clean(self):
        allowed_chars = '+0123456789'
        for p in self:
            # Filter allowed chars
            mobile_clean = ''.join([c for c in p.mobile if c in allowed_chars]) if p.mobile else ''
            # Make sure number starts with country code
            if len(mobile_clean) > 0 and mobile_clean[0] != '+':
                if len(mobile_clean) >= 2 and mobile_clean[0:2] == '00':
                    mobile_clean = '+' + mobile_clean[2:]
                else:
                    # @todo: Use country prefix from partner's country setting 
                    mobile_clean = '+45' + mobile_clean
            # Number can only have '+' as the first char - and length must be less than 18 chars
            # (two numbers will be at least 2 * 8 + 3 = 19 chars (3 for '+45')
            if '+' in mobile_clean[1:] or len(mobile_clean) > 18:
                mobile_clean = False
            p.mobile_clean = mobile_clean
