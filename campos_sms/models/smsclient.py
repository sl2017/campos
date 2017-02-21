# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _, tools
from openerp.exceptions import except_orm

import math
import urllib

import logging
_logger = logging.getLogger(__name__)

class SMSClient(models.Model):
    _inherit = 'sms.smsclient'

    def _check_permissions(self, cr, uid, id, context=None):
        '''
        Overwrite _check_permissions method
        Always return true (actual checks are made in sms.smsclient.queue's create method)
        '''
        return True

    def _get_http_url(self, sender, receiver, msg):
        # @TODO: Implement "sub-group" parameter to gateway
        # (so gateway log can be filtered by organization)
        url = self.url
        if url == 'config':
            url = tools.config.get('sms_gateway_url', False)
        if self.method == 'http':
            prms = {}
            for p in self.property_ids:
                if p.type == 'to':
                    prms[p.name] = receiver
                elif p.type == 'sms':
                    prms[p.name] = msg
                elif p.type == 'sender':
                    prms[p.name] = sender
                else:
                    prms[p.name] = p.value
            params = urllib.urlencode(prms)
            url += ('&' if '?' in url else '?') + params
        return url

    def _check_queue(self, cr, uid, context={}):
        queue_obj = self.pool.get('sms.smsclient.queue')
        sids = queue_obj.search(cr, uid, [('state', '=', 'draft')], limit=30, context=context)
        queue_obj.write(cr, uid, sids, {'state': 'sending'}, context=context)
        queue_obj.send_sms(cr, uid, sids, context=context)
        return True

class SMSQueue(models.Model):
    _inherit = 'sms.smsclient.queue'

    # Remove size limit on msg field
    msg = fields.Text(size=False)

    # Link to master SMS
    sms_master_id = fields.Many2one('sms.master', string='Master SMS', index=True, required=True)

    # Pricing information
    # Parts are computed for each single SMS in case of message merging, where the individual messages may have different lengths
    parts = fields.Integer('Parts', help='How many parts the SMS is split into', _compute='_compute_price', store=True)
    cost_price = fields.Float('Cost price', _compute='_compute_price', store=True, groups='campos_event.group_campos_admin')
    sell_price = fields.Float('Price', _compute='_compute_price', store=True)

    # Related fields for use in views
    organization_id = fields.Many2one(related='sms_master_id.organization_id', store=True, index=True)
    sender_text = fields.Char(related='sms_master_id.sender_text', store=True, index=True)

    @api.model
    def create(self, vals):
        vals['sms_master_id'] = vals.get('sms_master_id', False) or self.env.context.get('sms_master_id', False)
        sms_master_id_is_new = False

        # Create master SMS if it is not given
        if not vals['sms_master_id']:
            sms_master_id_is_new = True

            vals['organization_id'] = vals.get('organization_id', False) or self.env.context.get('sms_payer_organization_id', False)
            if not vals['organization_id']:
                raise exceptions.Warning(_('An error occured. No paying organization set when sending SMS.'))
            if not self.env.user.can_sms_organization(vals['organization_id']):
                raise exceptions.Warning(_('You do not have access to send SMS for %s') % self.env['member.organization'].browse(vals['organization_id'])[0].name)

            vals['sms_master_id'] = self.env['sms.master'].suspend_security().create({'organization_id': vals['organization_id'],
                                                                                      'msg': vals['msg']}).id
            del vals['organization_id'] # Maybe it's not really necessary to delete the key

        # Do not store HTTP url in name field
        vals['name'] = '%s: %s' % (vals['mobile'], self.env.context.get('sms_log_overwrite', vals['msg']))

        queue_id = super(SMSQueue, self.suspend_security()).create(vals)

        # Prices are NOT computed automatically for the new SMS
        queue_id._compute_price()
        if sms_master_id_is_new:
            queue_id.sms_master_id._compute_price()

        # Check SMS budget
        if queue_id.sms_master_id.organization_id._get_sms_amount(self.create_date) > queue_id.sms_master_id.organization_id.sms_max_monthly_cost:
            raise exceptions.Warning(_('The SMS could not be sent because it would exceed the SMS budget for %s.') % (queue_id.organization_id.name))

        # Send immediately if requested
        if self.env.context.get('sms_send_direct', False) or vals.get('sms_send_direct', False):
            queue_id.send_sms()

        return queue_id

    @api.one
    def send_sms_by_http(self, raise_exception=False):
        '''
        Overwrite smsclient module's send by HTTP method
        '''
        raise_exception = self.gateway_id.raise_exception
        try:
            url = self.gateway_id._get_http_url(self.sender_text.encode('latin-1'), self.mobile, self.msg.encode('latin-1'))
            allowed_dbs = self.env['ir.config_parameter'].sudo().get_param('sms_allowed_dbs', '')
            if self.env.cr.dbname in allowed_dbs.split(','):
                _logger.info('SMS: Send by http: %s', url)
                urllib.urlopen(url)
                self.state = 'send'
            else:
                _logger.info('SMS: Rejected (db %s not allowed to send SMS)', self.env.cr.dbname)
                self.state = 'cancel'

            # Overwrite msg text (to mask confirm codes from log)
            log_text = self.env.context.get('sms_log_overwrite', False)
            if log_text:
                self.msg = log_text
                self.sms_master_id.msg = log_text
        except Exception, e:
            if raise_exception:
                raise except_orm(_('Error'), e)
            else:
                # @TODO: Write general warning - store details only in internal log
                self.write({'state': _('Error'),
                            'error': str(e)})

    @api.model
    def get_sell_price(self, number, msg=''):
        '''
        Get sell price for an SMS
        '''
        config = self.env['ir.config_parameter'].sudo()
        np = config.get_param('sms_national_prefix', '')
        national = number[0:len(np)] == np
        str_len = len(msg.encode('latin-1')) if msg else 0
        parts = 1 if str_len <= 160 else math.ceil(str_len / 150.0)
        price = float(config.get_param('sms_national_sell_price', 0)) if national else float(config.get_param('sms_international_sell_price', 0))
        return parts * price

    @api.multi
    @api.depends('msg', 'mobile')
    def _compute_price(self):
        '''
        Compute SMS price - optimized for multiple calculations
        '''
        # Get all parameters in local variables
        config = self.env['ir.config_parameter'].sudo()
        np = config.get_param('sms_national_prefix', '')
        n_cost = float(config.get_param('sms_national_cost_price', 0))
        n_sell = float(config.get_param('sms_national_sell_price', 0))
        i_cost = float(config.get_param('sms_international_cost_price', 0))
        i_sell = float(config.get_param('sms_international_sell_price', 0))

        for q in self.sudo():
            national = q.mobile[0:len(np)] == np
            q.parts = 1 if len(q.msg) <= 160 else math.ceil(len(q.msg) / 150.0)
            q.cost_price = q.parts * (n_cost if national else i_cost)
            q.sell_price = q.parts * (n_sell if national else i_sell)

class SMSMaster(models.Model):
    '''
    Model to bind multiple SMS together (in a mass SMS messages to all receivers will belong to the same sms.master
    - Single messages will also have an sms.master
    '''
    _name = 'sms.master'
    _description = 'Master SMS'

    organization_id = fields.Many2one('campos.committee', string='Organization', index=True, required=True)
    sender_text = fields.Char('Sender', size=15, default='SMSservice')
    msg = fields.Text('Message')
    receivers_count = fields.Integer('Receivers', compute='_compute_receivers_count', store=True)
    cost_price = fields.Float('Cost price', _compute='_compute_price', store=True, groups='campos_event.group_campos_admin')
    sell_price = fields.Float('Price', _compute='_compute_price', store=True)

    sms_queue_ids = fields.One2many('sms.smsclient.queue', 'sms_master_id', 'Individual messages')

    @api.multi
    @api.depends('sms_queue_ids')
    def _compute_receivers_count(self):
        for m in self:
            m.receivers_count = len(m.sms_queue_ids)

    @api.one
    @api.depends('sms_queue_ids.cost_price', 'sms_queue_ids.sell_price')
    def _compute_price(self):
        '''
        Compute total price for this sending
        '''
        # Make new sudo read (reading cost_price with normal sudo() access WILL cause a cache prefetch error)
        sudo_queue_ids = self.sudo().sms_queue_ids.read(fields=['cost_price', 'sell_price'])
        self.sudo().cost_price = sum(s['cost_price'] for s in sudo_queue_ids)
        self.sudo().sell_price = sum(s['sell_price'] for s in sudo_queue_ids)
