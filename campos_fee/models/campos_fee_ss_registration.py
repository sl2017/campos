# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class CamposFeeSsRegistration(models.Model):

    _name = 'campos.fee.ss.registration'
    _description = 'Campos Fee Ss Registration'  # TODO

    name = fields.Char()
    
    snapshot_id = fields.Many2one('campos.fee.snapshot', 'Snapshot')
    registration_id = fields.Many2one('event.registration', 'Registration')
    sspar_ids = fields.One2many('campos.fee.ss.participant', 'ssreg_id', 'Snapshot')
    
    #Mirrored from the Group Registration
    state = fields.Selection([
        ('draft', 'Unconfirmed'),
        ('cancel', 'Cancelled'),
        ('open', 'Confirmed'),
        ('done', 'Attended'),
        ('deregistered', 'Deregistered')
        ], string='Status')
    number_participants = fields.Integer('Number of participants')
    fee_participants = fields.Float('Participants Fees')
    fee_transport = fields.Float('Transport Fee/Refusion')
    material_cost = fields.Float('Material orders')
    fee_total = fields.Float('Total Fee')
    invoice_id = fields.Many2one('account.invoice', 'Invoice')

    @api.multi            
    def make_invoice_50(self):
        aio = self.env['account.invoice']
        for ssreg in self:
            
            if ssreg.registration_id.partner_id.scoutgroup and ssreg.registration_id.partner_id.country_id and ssreg.registration_id.partner_id.country_id.code == 'DK':
            
                query = """  select camp_product_id, count(*) 
                             from campos_fee_ss_participant 
                             where ssreg_id in %s 
                             group by camp_product_id
                        """
                self._cr.execute(query, (tuple([ssreg.id]), ))
                for product_id, quantity in self._cr.fetchall():
                    product = self.env['product.product'].browse(product_id)
                    if product:
                        if not ssreg.invoice_id:
                            vals = self._prepare_create_invoice_vals()
                            _logger.info("Create invoice: %s", vals)
                            ssreg.invoice_id = aio.create(vals)
                        desc = "%s %s" % (product.name_get()[0][1], ' 1. rate 50%')
                        vals = self._prepare_create_invoice_line_vals(product.lst_price * 0.5, quantity, type='out_invoice', description=desc, product=product)
                        vals['invoice_id'] = ssreg.invoice_id.id
                        self.env['account.invoice.line'].create(vals)
                        ssreg.invoice_id.button_compute(set_total=True)
            
    def _prepare_create_invoice_line_vals(self, amount, quantity, type='out_invoice', description=False, product=False):
        '''
        Returns a "Vals" dict ready to create a invoice line.
        Product is taken from self.subscription_product_id
         
        :param per_start_date: Subscription period start date (date type)
        :param per_end_date: Subscription period end date (date type)
        :param amount: Subscription fee on line
        :param type: Invoice type: Default 'out_invoice' for Invoice
        :param description: Optional line desciption. If not provided generates 
                one from product, period and member 
        '''
        ailo = self.env['account.invoice.line']
        
        partner = self.registration_id.partner_id
        
        il_vals = ailo.product_id_change(
            product.id, product.uom_id.id, type=type,
            partner_id=partner.id,
            fposition_id=partner.property_account_position.id)['value']
        il_vals.update({
            'product_id': product.id,
            'price_unit': amount,
            'profile_id': self.id,
            'quantity': quantity
        })
        if description:
            il_vals['name'] = description
        
        return il_vals

    def _prepare_create_invoice_vals(self, type='out_invoice', date_invoice=False):
        '''
        Returns a "Vals" dict ready to create an Invoice (incl. one line)

        :param amount: Subscription fee on line
        :param type: Invoice type: Default 'out_invoice' for Invoice
        :param date_invoice: Default is today
        
        '''
        aio = self.env['account.invoice']
        
        partner = self.registration_id.partner_id
        if not date_invoice:
            date_invoice = fields.Date.today()
        
        vals = {
            'partner_id': partner.id,
            'currency_id': self.env.user.company_id.currency_id.id,
            'type': type,
            'company_id': self.env.user.company_id.id,
            'is_subscription_invoice': True,
            'date_invoice': date_invoice,
            'invoice_line': [],
        
        }
        vals.update(aio.onchange_partner_id(
            type, partner.id, company_id=self.env.user.company_id.id)['value'])

        return vals

    def generate_camp_fee_invoice(self, per_start_date, per_end_date, amount, type='out_invoice', auto=True, description=False, date_invoice=False, date_due=False, product=False, org=False):
        '''
        Create or update an Invoice with the given period and fee
        Product is taken from self.subscription_product_id
        Partner from self.partner_payer_id or, if not set, self.partner_id
        
        :param per_start_date: Subscription period start date (date type)
        :param per_end_date: Subscription period end date (date type)
        :param amount: Subscription fee on line
        :param type: Invoice type: Default 'out_invoice' for Invoice
        :param auto: Set auto_subscription on the Invoice
        :param date_invoice: Default is today
        :param date_due: Default is today + payment days on org.
        '''
        aio = self.env['account.invoice']
        if not org:
            org = self.organization_id
        invoice = False
        if self.partner_payer_id:
            partner = self.partner_payer_id
        else:
            partner = self.partner_id
        if auto:
            # Find invoice to add to
            invoice = aio.search([('partner_id', '=', partner.id),
                                  ('state', '=', 'draft'),
                                  ('auto_subscription', '=', True),
                                  ('company_id', '=', org.legal_company_id.id)],
                                 order='date_invoice', limit=1)

        if not invoice:
            vals = self._prepare_create_invoice_vals(per_start_date, per_end_date, amount, type=type, description=description, date_invoice=date_invoice, date_due=date_due, product=product, org=org)
            _logger.info("Create invoice: %s", vals)
            invoice = aio.create(vals)
        else:
            il_vals = self._prepare_create_invoice_line_vals(per_start_date, per_end_date, amount, type=type, description=description, product=product, org=org)
            il_vals['invoice_id'] = invoice.id
            self.env['account.invoice.line'].create(il_vals)
            invoice.button_compute(set_total=True)

        return invoice

            