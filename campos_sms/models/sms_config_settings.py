from openerp import models, fields, api, exceptions, SUPERUSER_ID, _

class SMSConfigSettings(models.TransientModel):
    _name = 'sms.config.settings'
    _inherit = 'res.config.settings'

    national_cost_price = fields.Float('National cost price', readonly=True)
    national_price_adjust = fields.Float('National adjustment')
    national_price_adjust_method = fields.Selection([('percent', 'Percent surcharge'),
                                                     ('amount', 'Amount surcharge'),
                                                     ('fixed', 'Fixed sell price')], default='percent')
    national_sell_price = fields.Float('National sell price', compute='_compute_national_sell_price')
    national_prefix = fields.Char('National prefix', default='+45', readonly=True)

    international_cost_price = fields.Float('International cost price', readonly=True)
    international_price_adjust = fields.Float('International adjustment')
    international_price_adjust_method = fields.Selection([('percent', 'Percent surcharge'),
                                                          ('amount', 'Amount surcharge'),
                                                          ('fixed', 'Fixed sell price')], default='percent')
    international_sell_price = fields.Float('International sell price', compute='_compute_international_sell_price')

    def compute_sell_price(self, cost, adjust, method):
        if method == 'fixed':
            return adjust
        if method == 'percent':
            # Round before dividing limits sell price to two decimals
            return round(cost * (100+adjust)) / 100
        if method == 'amount': 
            return cost + adjust
        raise exceptions.Warning(_('Unknown price adjustment method: %s') % method)

    @api.one
    @api.depends('national_cost_price', 'national_price_adjust', 'national_price_adjust_method')
    def _compute_national_sell_price(self):
        self.national_sell_price = self.compute_sell_price(self.national_cost_price, self.national_price_adjust, self.national_price_adjust_method)

    @api.one
    @api.depends('international_cost_price', 'international_price_adjust', 'international_price_adjust_method')
    def _compute_international_sell_price(self):
        self.international_sell_price = self.compute_sell_price(self.international_cost_price, self.international_price_adjust, self.international_price_adjust_method)

    @api.model
    def default_get(self, fields):
        result = super(SMSConfigSettings, self).default_get(fields)

        # Get float values
        for field in ['national_cost_price', 'national_price_adjust', 
                      'international_cost_price', 'international_price_adjust']:
            result[field] = float(self.env['ir.config_parameter'].get_param('sms_' + field, 0))

        # Get string values
        for field in ['national_price_adjust_method', 'national_prefix', 'international_price_adjust_method']:
            value = self.env['ir.config_parameter'].get_param('sms_' + field, False)
            if value:
                result[field] = value 

        return result

    @api.multi
    def execute(self):
        if not (self.env.uid == SUPERUSER_ID or self.user_has_groups('campos_event.group_campos_admin')):
            raise exceptions.AccessDenied(_('Only administrator may change these settings'))

        result = super(SMSConfigSettings, self).execute()

        for field in ['national_price_adjust', 'national_price_adjust_method', 'national_sell_price',
                      'international_price_adjust', 'international_price_adjust_method', 'international_sell_price']:
            self.env['ir.config_parameter'].set_param('sms_' + field, str(getattr(self, field)))

        return result
