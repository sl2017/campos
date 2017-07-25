# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _

from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError

import logging
_logger = logging.getLogger(__name__)





class CamposFeeSsRegistration(models.Model):

    _name = 'campos.fee.ss.registration'
    _description = 'Campos Fee Ss Registration'  # TODO

    name = fields.Char()
    
    snapshot_id = fields.Many2one('campos.fee.snapshot', 'Snapshot')
    registration_id = fields.Many2one('event.registration', 'Registration')
    sspar_ids = fields.One2many('campos.fee.ss.participant', 'ssreg_id', 'Participants')
    ssmeat_ids = fields.One2many('campos.fee.ss.reg.meat', 'ssreg_id', 'Meat')
    
    #Mirrored from the Group Registration
    state = fields.Selection([
        ('draft', 'Unconfirmed'),
        ('cancel', 'Cancelled'),
        ('open', 'Confirmed'),
        ('done', 'Attended'),
        ('deregistered', 'Deregistered'),
        ('arrived', 'Arrived'),
        ('checkin', 'Check In Completed'),
        ('checkout', 'Check OUT Completed'),
        ], string='Status')
    number_participants = fields.Integer('Number of participants')
    fee_participants = fields.Float('Participants Fees')
    fee_transport = fields.Float('Transport Fee/Refusion')
    charged_fee_participants = fields.Float('Participants Fees')
    charged_fee_transport = fields.Float('Transport Fee/Refusion')
    material_cost = fields.Float('Material orders')
    fee_total = fields.Float('Total Fee')
    invoice_id = fields.Many2one('account.invoice', 'Invoice')
    inv_currency_id = fields.Many2one(related='invoice_id.currency_id', readonly=True)
    inv_amount_total = fields.Float(related='invoice_id.amount_total', readonly=True)
    invoice_line = fields.One2many(related='invoice_id.invoice_line', readonly=True)
    inv_date = fields.Date(related='invoice_id.date_invoice', readonly=True)
    audit = fields.Boolean('Audit')
    cmp_currency_id = fields.Many2one(related='registration_id.event_id.company_id.currency_id', readonly=True)
    ref_ssreg_id = fields.Many2one('campos.fee.ss.registration', 'Ref Snapshot')
    count_transport_to = fields.Integer('# Transport to Camp', compute='_compute_count_transport', compute_sudo=True)
    count_transport_from = fields.Integer('# Transport from Camp', compute='_compute_count_transport', compute_sudo=True)
    transport_cost = fields.Float('Transport Cost', compute='_compute_count_transport', compute_sudo=True)
    
    @api.multi
    def _compute_count_transport(self):
        for ssreg in self:
            ssreg.count_transport_to = self.env['campos.fee.ss.participant'].search_count([('ssreg_id', '=', ssreg.id), ('transport_to_camp', '=', True)])
            ssreg.count_transport_from = self.env['campos.fee.ss.participant'].search_count([('ssreg_id', '=', ssreg.id), ('transport_from_camp', '=', True)])
            tran_prices = ssreg.sspar_ids.filtered(lambda r: r.transport_price > 0).mapped('transport_price')
            if tran_prices:
                ssreg.transport_cost = (ssreg.count_transport_to + ssreg.count_transport_from) * tran_prices[0] 


    @api.multi
    def do_delayed_snapshot(self):
        for ssreg in self:
        
            for par in ssreg.registration_id.participant_ids:
                par.do_snapshot(ssreg)
                
            for meat in ssreg.registration_id.meatlist_ids:
                self.env['campos.fee.ss.reg.meat'].create({'ssreg_id': ssreg.id,
                                                           'event_day_meat_id': meat.event_day_meat_id.id,
                                                           'meat_count': meat.meat_count})
            
            ssreg.write({'number_participants': ssreg.registration_id.number_participants,
                         'fee_participants': ssreg.registration_id.fee_participants,
                         'fee_transport': ssreg.registration_id.fee_transport,
                         'material_cost': ssreg.registration_id.material_cost,
                         'fee_total': ssreg.registration_id.fee_total,
                         'state': ssreg.registration_id.state,
                         'name': ssreg.registration_id.name})
            if ssreg.snapshot_id.ref_snapshot_id:
                ssreg.ref_ssreg_id = ssreg.search([('snapshot_id', '=', ssreg.snapshot_id.ref_snapshot_id.id), ('registration_id', '=', ssreg.registration_id.id)])
            if ssreg.snapshot_id.execute_func:
                func = getattr(ssreg, ssreg.snapshot_id.execute_func)
                func()


    @api.multi            
    def assign_participant_number(self):
        for ssreg in self:
            ssreg.registration_id.participant_ids.filtered(lambda p: p.state in ['draft', 'standby', 'sent', 'inprogress', 'approved']).assign_participant_number()

    @api.multi            
    def sync_participant(self):
        for ssreg in self:
            for p in ssreg.registration_id.participant_ids:
                if p.partner_id.remote_system_id and p.camp_age > 15:
                    p.partner_id.remote_system_id.syncPartner(partner=p.partner_id, is_company=False)
    @api.multi            
    def make_invoice_50(self):
        aio = self.env['account.invoice']
        for ssreg in self:
            
            if ssreg.registration_id.partner_id.scoutgroup and ssreg.registration_id.partner_id.country_id and ssreg.registration_id.partner_id.country_id.code == 'DK' and ssreg.registration_id.state in ['open', 'done']:
            
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
    
    @api.multi
    def make_invoice_100(self):
        ''' To use from test button '''
        aio = self.env['account.invoice']
        for ssreg in self:
            
            # Sydslesvig
            if ssreg.registration_id.partner_id.scoutgroup and ssreg.registration_id.partner_id.scoutorg_id.id == 83 and ssreg.registration_id.state in ['open', 'done']:
                ssreg.with_context(lang=ssreg.registration_id.partner_id.lang).make_invoice_spec(subtract1=False)
            elif ssreg.registration_id.partner_id.scoutgroup and ssreg.registration_id.partner_id.country_id and ssreg.registration_id.partner_id.country_id.code == 'DK' and ssreg.registration_id.state in ['open', 'done']:
                ssreg.with_context(lang=ssreg.registration_id.partner_id.lang).make_invoice_spec(subtract1=True)
            elif ssreg.registration_id.partner_id.scoutgroup and ssreg.registration_id.partner_id.country_id and ssreg.registration_id.partner_id.country_id.code != 'DK' and ssreg.registration_id.state in ['open', 'done']:
                ssreg.with_context(lang=ssreg.registration_id.partner_id.lang).make_invoice_spec(subtract1=False)
                
    @api.multi
    def make_invoice_group(self):
        for ssreg in self:
            if ssreg.snapshot_id.segment == 'ss_groups' and ssreg.registration_id.partner_id.scoutgroup and ssreg.registration_id.partner_id.scoutorg_id.id == 83 and ssreg.registration_id.state in ['open', 'done']:
                ssreg.with_context(lang=ssreg.registration_id.partner_id.lang).make_invoice_spec(subtract1=False)
            elif ssreg.snapshot_id.segment == 'dk_groups' and ssreg.registration_id.partner_id.scoutgroup and ssreg.registration_id.partner_id.country_id and ssreg.registration_id.partner_id.country_id.code == 'DK' and ssreg.registration_id.state in ['open', 'done']:
                ssreg.with_context(lang=ssreg.registration_id.partner_id.lang).make_invoice_spec(subtract1=False)
            elif ssreg.snapshot_id.segment == 'non_dk_groups' and ssreg.registration_id.partner_id.scoutgroup and ssreg.registration_id.partner_id.country_id and ssreg.registration_id.partner_id.country_id.code != 'DK' and ssreg.registration_id.state in ['open', 'done']:
                ssreg.with_context(lang=ssreg.registration_id.partner_id.lang).make_invoice_spec(subtract1=False)
            elif ssreg.snapshot_id.segment == 'jobber' and not ssreg.registration_id.partner_id.scoutgroup and ssreg.registration_id.partner_id.staff and ssreg.registration_id.partner_id.country_id.code == 'DK':
                ssreg.with_context(lang=ssreg.registration_id.partner_id.lang).make_invoice_jobber(subtract1=False)
            elif ssreg.snapshot_id.segment == 'jobber_non_dk' and not ssreg.registration_id.partner_id.scoutgroup and ssreg.registration_id.partner_id.staff and ssreg.registration_id.partner_id.country_id.code != 'DK':
                ssreg.with_context(lang=ssreg.registration_id.partner_id.lang).make_invoice_jobber(subtract1=False)
                
    @api.multi            
    def make_invoice_100_dk(self):
        aio = self.env['account.invoice']
        for ssreg in self:
            
            if ssreg.registration_id.partner_id.scoutgroup and ssreg.registration_id.partner_id.country_id and ssreg.registration_id.partner_id.country_id.code == 'DK' and ssreg.registration_id.state in ['open', 'done']:
                ssreg.with_context(lang=ssreg.registration_id.partner_id.lang).make_invoice_spec(subtract1=True)
            
    @api.multi            
    def make_invoice_100_non_dk(self):
        aio = self.env['account.invoice']
        for ssreg in self:
            
            # Sydslesvig
            if ssreg.registration_id.partner_id.scoutgroup and ssreg.registration_id.partner_id.scoutorg_id.id == 83 and ssreg.registration_id.state in ['open', 'done']:
                ssreg.with_context(lang=ssreg.registration_id.partner_id.lang).make_invoice_spec(subtract1=False)
            # Udenlandske
            elif ssreg.registration_id.partner_id.scoutgroup and ssreg.registration_id.partner_id.country_id and ssreg.registration_id.partner_id.country_id.code != 'DK' and ssreg.registration_id.state in ['open', 'done']:
                ssreg.with_context(lang=ssreg.registration_id.partner_id.lang).make_invoice_jobber(subtract1=False)
    
    
    def _get_no_cancel_fee(self):
        current_par_ids = self.sspar_ids.filtered('no_cancel_fee').mapped('participant_id')
        prev_par_ids = self.ref_ssreg_id.sspar_ids.filtered(lambda r: r.participant_id in current_par_ids and not r.no_cancel_fee)
        cancelled_fee = 0
        cancelled_transport_cost = 0
        for p in prev_par_ids:
            cancelled_fee += p.camp_price
            cancelled_transport_cost += (2 - p.transport_co) * self.ref_ssreg_id.par_ids.filtered(lambda r: r.transport_price > 0).mapped('transport_price')
            
        return cancelled_fee, cancelled_transport_cost 
    
    @api.multi            
    def make_invoice_spec(self, subtract1=False):
        aio = self.env['account.invoice']
        for ssreg in self:
            #1 Camp Participations
            query = """  select camp_product_id, count(*) 
                         from campos_fee_ss_participant 
                         where ssreg_id in %s and no_invoicing = 'f'
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
                    desc = product.name_get()[0][1] #product.display_name 
                    vals = self._prepare_create_invoice_line_vals(False, quantity, type='out_invoice', description=desc, product=product)
                    vals['invoice_id'] = ssreg.invoice_id.id
                    self.env['account.invoice.line'].create(vals)
                    ssreg.invoice_id.button_compute(set_total=True)
            
            #2 Transport
            query = """  select transport_product_id, sum(transport_co) 
                         from campos_fee_ss_participant 
                         where ssreg_id in %s and no_invoicing = 'f'
                         group by transport_product_id
                    """
            self._cr.execute(query, (tuple([ssreg.id]), ))
            for product_id, quantity in self._cr.fetchall():
                product = self.env['product.product'].browse(product_id)
                if product:
                    if not ssreg.invoice_id:
                        vals = self._prepare_create_invoice_vals()
                        vals['origin'] = ssreg.snapshot_id.code
                        _logger.info("Create invoice: %s", vals)
                        ssreg.invoice_id = aio.create(vals)
                    desc = product.name_get()[0][1] # product.display_name 
                    vals = self._prepare_create_invoice_line_vals(False, quantity, type='out_invoice', description=desc, product=product)
                    vals['invoice_id'] = ssreg.invoice_id.id
                    self.env['account.invoice.line'].create(vals)
                    ssreg.invoice_id.button_compute(set_total=True)
                    
            # 3 Other orders (Invoice sales orders)
            invoices = {}
            sales_order_line_obj = self.env['sale.order.line']
            sales_order_obj = self.env['sale.order']
            for line in sales_order_line_obj.search([('order_partner_id', '=', self.registration_id.partner_id.id)]):
                _logger.info('SO %s', line)
                if (not line.invoiced) and (line.state not in ('draft', 'cancel')) and line.product_uom_qty != 0:
                    product = line.product_id
                    if product:
                        if not ssreg.invoice_id:
                            vals = self._prepare_create_invoice_vals()
                            _logger.info("Create invoice: %s", vals)
                            ssreg.invoice_id = aio.create(vals)
                        desc = product.name_get()[0][1]
                        vals = self._prepare_create_invoice_line_vals(False, line.product_uom_qty, type='out_invoice', description=desc, product=product)
                        vals['invoice_id'] = ssreg.invoice_id.id
                        ail_id = self.env['account.invoice.line'].create(vals)
                        line.invoice_lines = ail_id
            
                    
            prev_inv_id = False
            prev2_ssreg_id = False
            if ssreg.ref_ssreg_id and ssreg.ref_ssreg_id.invoice_id:
                prev_inv_id = ssreg.ref_ssreg_id.invoice_id
                prev_ssreg_id = ssreg.ref_ssreg_id
            if ssreg.snapshot_id.dyna_ref:
                prev_ssreg_id = ssreg.registration_id.ssreginv_ids.sorted(lambda r: r.invoice_id.date_invoice)
                if prev_ssreg_id:
                    if len(prev_ssreg_id) > 1:
                        prev2_ssreg_id = prev_ssreg_id[-2] 
                    prev_ssreg_id = prev_ssreg_id[-1]
                    prev_inv_id = prev_ssreg_id.invoice_id
                    ssreg.ref_ssreg_id = prev_ssreg_id      
            if prev_inv_id:
                charged_fee_par = ssreg.ref_ssreg_id.charged_fee_participants if ssreg.ref_ssreg_id.charged_fee_participants else ssreg.ref_ssreg_id.fee_participants
                charged_fee_tran = ssreg.ref_ssreg_id.charged_fee_transport if ssreg.ref_ssreg_id.charged_fee_transport else ssreg.ref_ssreg_id.fee_transport
                product = self.env['product.product'].search([('default_code', '=', 'INFO')])
                #1. Prev camp fee
                desc = _('Participant fee charged on invoice %s:') % ssreg.ref_ssreg_id.invoice_id.number
                vals = self._prepare_create_invoice_line_vals(0, 0, type='out_invoice', description=desc, product=product)
                vals['invoice_id'] = ssreg.invoice_id.id
                self.env['account.invoice.line'].create(vals)
                for line in ssreg.ref_ssreg_id.invoice_id.invoice_line:
                    if line.product_id.default_code and line.product_id.default_code.startswith('LK') and line.quantity > 0:
                        if line.product_id.default_code != 'LKREF':
                            vals = self._prepare_create_invoice_line_vals(line.price_unit  if ssreg.ref_ssreg_id.invoice_id.type == 'out_invoice' else -line.price_unit, -line.quantity, type='out_invoice', description=line.name, product=line.product_id)
                            vals['invoice_id'] = ssreg.invoice_id.id
                            self.env['account.invoice.line'].create(vals)
                        
                # Handle "no_cancel_fee
                cancelled_fee, cancelled_transport = ssreg._get_no_cancel_fee()    
                charged_fee_par = charged_fee_par - cancelled_fee
                     
                if charged_fee_par > ssreg.fee_participants and ssreg.number_participants < ssreg.ref_ssreg_id.number_participants:
                    
                    # Find cancelled since last invoice:
                    num_canc = 0
                    num_c100 = 0
                    num_c50 = 0
                    canc_ids = ssreg.sspar_ids.filtered(lambda r: r.state == 'deregistered' and not r.no_cancel_fee and r.participant_id.cancel_dt > ssreg.ref_ssreg_id.invoice_id.create_date)
                    if canc_ids:
                        num_canc = len(canc_ids)
                        for p in canc_ids:
                            if p.participant_id.cancel_dt > '2017-07-01 02:00:00':
                                num_c100 += 1
                            else:
                                num_c50 += 1
                    #2. 50 % refusions
                    if num_canc:
                        charged_fee_par_val = charged_fee_par
                        fee_par_val = ssreg.fee_participants
                        if ssreg.ref_ssreg_id.invoice_id.currency_id != ssreg.ref_ssreg_id.invoice_id.company_id.currency_id:
                             charged_fee_par_val = charged_fee_par * ssreg.ref_ssreg_id.invoice_id.currency_id.rate 
                             fee_par_val = ssreg.fee_participants * ssreg.ref_ssreg_id.invoice_id.currency_id.rate
                        canc_fee = (charged_fee_par_val - fee_par_val) / num_canc
                        if num_c100:
                            product = self.env['product.product'].search([('default_code', '=', 'LKREF100')])
                            desc = _('No refusion after juli 1') 
                            vals = self._prepare_create_invoice_line_vals(canc_fee, num_c100, type='out_invoice', description=desc, product=product)
                            #vals['amount'] = -ssreg1.invoice_id.amount_total
                            vals['invoice_id'] = ssreg.invoice_id.id
                            self.env['account.invoice.line'].create(vals)
                            ssreg.audit = True
                        if num_c50:
                            product = self.env['product.product'].search([('default_code', '=', 'LKREF50')])
                            desc = _('50% refusion after may 1') 
                            vals = self._prepare_create_invoice_line_vals(canc_fee / 2, num_c50, type='out_invoice', description=desc, product=product)
                            #vals['amount'] = -ssreg1.invoice_id.amount_total
                            vals['invoice_id'] = ssreg.invoice_id.id
                            self.env['account.invoice.line'].create(vals)
                            ssreg.audit = True

                product = self.env['product.product'].search([('default_code', '=', 'TRAN')])
                #1. Prev transport fee
                charged_fee_tran_val = charged_fee_tran
                fee_tran_val = ssreg.fee_transport
                if ssreg.ref_ssreg_id.invoice_id.currency_id != ssreg.ref_ssreg_id.invoice_id.company_id.currency_id:
                    charged_fee_tran_val = charged_fee_tran * ssreg.ref_ssreg_id.invoice_id.currency_id.rate
                    fee_tran_val = ssreg.fee_transport * ssreg.ref_ssreg_id.invoice_id.currency_id.rate
                desc = _('Transport fee charged on invoice %s') % ssreg.ref_ssreg_id.invoice_id.number
                vals = self._prepare_create_invoice_line_vals(-charged_fee_tran_val, 1, type='out_invoice', description=desc, product=product)
                vals['invoice_id'] = ssreg.invoice_id.id
                self.env['account.invoice.line'].create(vals)

                # Correction for wrong TREF on previous invoice
                corr = False
                for line in ssreg.ref_ssreg_id.invoice_id.invoice_line:
                    if line.product_id.default_code and line.product_id.default_code == 'TREF' and line.quantity > 0:
                        vals = self._prepare_create_invoice_line_vals(line.price_unit  if ssreg.ref_ssreg_id.invoice_id.type == 'out_invoice' else -line.price_unit, -line.quantity, type='out_invoice', description='Correction: %s' % line.name, product=line.product_id)
                        vals['invoice_id'] = ssreg.invoice_id.id
                        self.env['account.invoice.line'].create(vals)
                        corr = True

                if corr:
                    # Compare with previous
                    if ssreg.transport_cost < (prev2_ssreg_id.transport_cost - cancelled_transport):
                        #2. No refusions
                        transport_refusion = prev2_ssreg_id.transport_cost - ssreg.transport_cost - cancelled_transport 
                        if ssreg.ref_ssreg_id.invoice_id.currency_id != ssreg.ref_ssreg_id.invoice_id.company_id.currency_id:
                            transport_refusion = transport_refusion * ssreg.ref_ssreg_id.invoice_id.currency_id.rate
                        product = self.env['product.product'].search([('default_code', '=', 'TREF2')])
                        desc = _('No refusion after may 1') 
                        vals = self._prepare_create_invoice_line_vals((transport_refusion), 1, type='out_invoice', description=desc, product=product)
                        #vals['amount'] = -ssreg1.invoice_id.amount_total
                        vals['invoice_id'] = ssreg.invoice_id.id
                        self.env['account.invoice.line'].create(vals)
                        ssreg.charged_fee_transport = ssreg.fee_transport + charged_fee_tran - ssreg.fee_transport
                        ssreg.audit = True

                elif ssreg.transport_cost < (ssreg.ref_ssreg_id.transport_cost  - cancelled_transport):
                        #2. No refusions
                        transport_refusion = ssreg.ref_ssreg_id.transport_cost - ssreg.transport_cost - cancelled_transport 
                        if ssreg.ref_ssreg_id.invoice_id.currency_id != ssreg.ref_ssreg_id.invoice_id.company_id.currency_id:
                            transport_refusion = transport_refusion * ssreg.ref_ssreg_id.invoice_id.currency_id.rate
                        product = self.env['product.product'].search([('default_code', '=', 'TREF2')])
                        desc = _('No refusion after may 1') 
                        vals = self._prepare_create_invoice_line_vals((transport_refusion), 1, type='out_invoice', description=desc, product=product)
                        #vals['amount'] = -ssreg1.invoice_id.amount_total
                        vals['invoice_id'] = ssreg.invoice_id.id
                        self.env['account.invoice.line'].create(vals)
                        ssreg.charged_fee_transport = ssreg.fee_transport + charged_fee_tran - ssreg.fee_transport
                        ssreg.audit = True

            ssreg.invoice_id.button_compute(set_total=True)
            if ssreg.invoice_id.amount_total < 0:
                #Change to Credit Nota or drop?
                if ssreg.snapshot_id.make_creditnota:
                    ssreg.invoice_id.type = 'out_refund'
                    for line in ssreg.invoice_id.invoice_line:
                        line.price_unit = - line.price_unit
                    ssreg.invoice_id.button_compute(set_total=True)
                    ssreg.audit = True
                else:
                    ssreg.invoice_id.unlink()
            elif ssreg.invoice_id.amount_total == 0.0:
                ssreg.invoice_id.unlink()
            elif not ssreg.audit and not ssreg.snapshot_id.always_draft:
                ssreg.invoice_id.signal_workflow('invoice_open')

    @api.multi            
    def make_invoice_jobber(self, subtract1=False):
        aio = self.env['account.invoice']
        for ssreg in self:

            #1 Camp PArticipations
            query = """  select name, camp_product_id, count(*) 
                         from campos_fee_ss_participant 
                         where ssreg_id in %s and signup_state = 'oncamp' and no_invoicing = 'f'
                         group by camp_product_id, participant_id, name
                    """
            self._cr.execute(query, (tuple([ssreg.id]), ))
            for jobname, product_id, quantity in self._cr.fetchall():
                product = self.env['product.product'].browse(product_id)
                if product:
                    if not ssreg.invoice_id:
                        vals = self._prepare_create_invoice_vals()
                        vals['origin'] = ssreg.snapshot_id.code
                        _logger.info("Create invoice: %s", vals)
                        ssreg.invoice_id = aio.create(vals)
                    desc = product.name_get()[0][1] + ' ' + jobname #product.display_name 
                    vals = self._prepare_create_invoice_line_vals(False, quantity, type='out_invoice', description=desc, product=product)
                    vals['invoice_id'] = ssreg.invoice_id.id
                    self.env['account.invoice.line'].create(vals)
                    ssreg.invoice_id.button_compute(set_total=True)
            
            #2 Transport
            query = """  select transport_product_id, sum(transport_co) 
                         from campos_fee_ss_participant 
                         where ssreg_id in %s and signup_state = 'oncamp' and no_invoicing = 'f' 
                         group by transport_product_id
                    """
            self._cr.execute(query, (tuple([ssreg.id]), ))
            for product_id, quantity in self._cr.fetchall():
                product = self.env['product.product'].browse(product_id)
                if product:
                    if not ssreg.invoice_id:
                        vals = self._prepare_create_invoice_vals()
                        _logger.info("Create invoice: %s", vals)
                        ssreg.invoice_id = aio.create(vals)
                    desc = product.name_get()[0][1] # product.display_name 
                    vals = self._prepare_create_invoice_line_vals(False, quantity, type='out_invoice', description=desc, product=product)
                    vals['invoice_id'] = ssreg.invoice_id.id
                    self.env['account.invoice.line'].create(vals)
                    ssreg.invoice_id.button_compute(set_total=True)
                    
            # 3 Other orders (Invoice sales orders)
#                 invoices = {}
#                 sales_order_line_obj = self.env['sale.order.line']
#                 sales_order_obj = self.env['sale.order']
#                 for line in sales_order_line_obj.search([('order_partner_id', '=', self.registration_id.partner_id.id)]):
#                     _logger.info('SO %s', line)
#                     if (not line.invoiced) and (line.state not in ('draft', 'cancel')) and line.product_uom_qty != 0:
#                         product = line.product_id
#                         if product:
#                             if not ssreg.invoice_id:
#                                 vals = self._prepare_create_invoice_vals()
#                                 _logger.info("Create invoice: %s", vals)
#                                 ssreg.invoice_id = aio.create(vals)
#                             desc = product.name_get()[0][1]
#                             vals = self._prepare_create_invoice_line_vals(False, line.product_uom_qty, type='out_invoice', description=desc, product=product)
#                             vals['invoice_id'] = ssreg.invoice_id.id
#                             ail_id = self.env['account.invoice.line'].create(vals)
#                             line.invoice_lines = ail_id
            
            if subtract1:
                ssreg1 = self.search([('registration_id', '=', ssreg.registration_id.id),('invoice_id', '!=', False),('snapshot_id', '=', 2)])
                if ssreg1:
                    product = self.env['product.product'].search([('default_code', '=', 'RATE1')])
                    if product:
                        desc = u'Opkrævet på fak %s' % ssreg1.invoice_id.number
                        _logger.info('RATE1 %s %s', desc, ssreg1.invoice_id.amount_total)
                        vals = self._prepare_create_invoice_line_vals(-ssreg1.invoice_id.amount_total, 1, type='out_invoice', description=desc, product=product)
                        #vals['amount'] = -ssreg1.invoice_id.amount_total
                        vals['invoice_id'] = ssreg.invoice_id.id
                        self.env['account.invoice.line'].create(vals)
            
            
                if ssreg.number_participants < ssreg1.number_participants:
                    ssreg.audit = True
            

            prev_inv_id = False
            prev2_ssreg_id = False
            if ssreg.ref_ssreg_id and ssreg.ref_ssreg_id.invoice_id:
                prev_inv_id = ssreg.ref_ssreg_id.invoice_id
                prev_ssreg_id = ssreg.ref_ssreg_id
            if ssreg.snapshot_id.dyna_ref:
                prev_ssreg_id = ssreg.registration_id.ssreginv_ids.sorted(lambda r: r.invoice_id.date_invoice)
                if prev_ssreg_id:
                    if len(prev_ssreg_id) > 1:
                        prev2_ssreg_id = prev_ssreg_id[-2] 
                    prev_ssreg_id = prev_ssreg_id[-1]
                    prev_inv_id = prev_ssreg_id.invoice_id
                    ssreg.ref_ssreg_id = prev_ssreg_id      
            if prev_inv_id:
                charged_fee_par = ssreg.ref_ssreg_id.charged_fee_participants if ssreg.ref_ssreg_id.charged_fee_participants else ssreg.ref_ssreg_id.fee_participants
                charged_fee_tran = ssreg.ref_ssreg_id.charged_fee_transport if ssreg.ref_ssreg_id.charged_fee_transport else ssreg.ref_ssreg_id.fee_transport
                product = self.env['product.product'].search([('default_code', '=', 'INFO')])
                #1. Prev camp fee
                desc = _('Participant fee charged on invoice %s:') % ssreg.ref_ssreg_id.invoice_id.number
                vals = self._prepare_create_invoice_line_vals(0, 0, type='out_invoice', description=desc, product=product)
                vals['invoice_id'] = ssreg.invoice_id.id
                self.env['account.invoice.line'].create(vals)
                for line in ssreg.ref_ssreg_id.invoice_id.invoice_line:
                    if line.product_id.default_code and line.product_id.default_code.startswith('LK') and line.quantity > 0:
                        if line.product_id.default_code != 'LKREF':
                            vals = self._prepare_create_invoice_line_vals(line.price_unit, -line.quantity, type='out_invoice', description=line.name, product=line.product_id)
                            vals['invoice_id'] = ssreg.invoice_id.id
                            self.env['account.invoice.line'].create(vals)
                        
                if charged_fee_par > ssreg.fee_participants and ssreg.number_participants < ssreg.ref_ssreg_id.number_participants:
                    #2. 50 % refusions
                    charged_fee_par_val = charged_fee_par
                    fee_par_val = ssreg.fee_participants
                    if ssreg.ref_ssreg_id.invoice_id.currency_id != ssreg.ref_ssreg_id.invoice_id.company_id.currency_id:
                         charged_fee_par_val = charged_fee_par * ssreg.ref_ssreg_id.invoice_id.currency_id.rate 
                         fee_par_val = ssreg.fee_participants * ssreg.ref_ssreg_id.invoice_id.currency_id.rate
                    product = self.env['product.product'].search([('default_code', '=', 'LKREF')])
                    desc = _('Only  50%% refusion after may 1: %s %.2f - %.2f') % (ssreg.ref_ssreg_id.invoice_id.currency_id.name, charged_fee_par_val, fee_par_val) 
                    vals = self._prepare_create_invoice_line_vals((charged_fee_par_val - fee_par_val) / 2, 1, type='out_invoice', description=desc, product=product)
                    #vals['amount'] = -ssreg1.invoice_id.amount_total
                    vals['invoice_id'] = ssreg.invoice_id.id
                    self.env['account.invoice.line'].create(vals)
                    ssreg.charged_fee_participants = ssreg.fee_participants + (charged_fee_par - ssreg.fee_participants / 2)
                    ssreg.audit = True
                product = self.env['product.product'].search([('default_code', '=', 'TRAN')])
                #1. Prev transport fee
                charged_fee_tran_val = charged_fee_tran
                fee_tran_val = ssreg.fee_transport
                if ssreg.ref_ssreg_id.invoice_id.currency_id != ssreg.ref_ssreg_id.invoice_id.company_id.currency_id:
                    charged_fee_tran_val = charged_fee_tran * ssreg.ref_ssreg_id.invoice_id.currency_id.rate
                    fee_tran_val = ssreg.fee_transport * ssreg.ref_ssreg_id.invoice_id.currency_id.rate
                desc = _('Transport fee charged on invoice %s') % ssreg.ref_ssreg_id.invoice_id.number
                vals = self._prepare_create_invoice_line_vals(-charged_fee_tran_val, 1, type='out_invoice', description=desc, product=product)
                vals['invoice_id'] = ssreg.invoice_id.id
                self.env['account.invoice.line'].create(vals)
                
                
                if charged_fee_tran > ssreg.fee_transport and (ssreg.count_transport_from + ssreg.count_transport_to) <  (ssreg.ref_ssreg_id.count_transport_from + ssreg.ref_ssreg_id.count_transport_to):
                        #2. No refusions
                        product = self.env['product.product'].search([('default_code', '=', 'TRREF')])
                        desc = _('No refusion after may 1: %s %.2f - %.2f') % (ssreg.ref_ssreg_id.invoice_id.currency_id.name,charged_fee_tran_val, fee_tran_val) 
                        vals = self._prepare_create_invoice_line_vals((charged_fee_tran_val - fee_tran_val), 1, type='out_invoice', description=desc, product=product)
                        #vals['amount'] = -ssreg1.invoice_id.amount_total
                        vals['invoice_id'] = ssreg.invoice_id.id
                        self.env['account.invoice.line'].create(vals)
                        ssreg.charged_fee_transport = ssreg.fee_transport + charged_fee_tran - ssreg.fee_transport
                        ssreg.audit = True
            
            ssreg.invoice_id.button_compute(set_total=True)
            if ssreg.invoice_id.amount_total < 0:
                #Change to Credit Nota or drop?
                if ssreg.snapshot_id.make_creditnota:
                    ssreg.invoice_id.type = 'out_refund'
                    for line in ssreg.invoice_id.invoice_line:
                        line.price_unit = - line.price_unit
                    ssreg.invoice_id.button_compute(set_total=True)
                    ssreg.audit = True
                else:
                    ssreg.invoice_id.unlink()
            elif ssreg.invoice_id.amount_total == 0.0:
                ssreg.invoice_id.unlink()
            elif not ssreg.audit and not ssreg.snapshot_id.always_draft:
                ssreg.invoice_id.signal_workflow('invoice_open')


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
        _logger.info('IL Call amount %s', amount)
        
        _logger.info('IL Call %s : %s', partner.property_account_receivable.currency_id.id if partner.property_account_receivable.currency_id else self.env.user.company_id.currency_id.id, self.env.user.company_id.currency_id.id)
        il_vals = ailo.product_id_change(
            product.id, product.uom_id.id, type=type,
            partner_id=partner.id,
            fposition_id=partner.property_account_position.id, 
            currency_id=partner.property_account_receivable.currency_id.id if partner.property_account_receivable.currency_id else self.env.user.company_id.currency_id.id,
            company_id=self.env.user.company_id.id)['value']
        il_vals.update({
            'product_id': product.id,
            'quantity': quantity
        })
        if amount:
            il_vals['price_unit'] = amount
        if description:
            il_vals['name'] = description
        _logger.info('IL Vals %s', il_vals)
        return il_vals

    def _prepare_create_invoice_vals(self, type='out_invoice', date_invoice=False):
        '''
        Returns a "Vals" dict ready to create an Invoice (incl. one line)

        :param amount: Subscription fee on line
        :param type: Invoice type: Default 'out_invoice' for Invoice
        :param date_invoice: Default is today
        
        '''
        aio = self.env['account.invoice']
        
#         if self.registration_id.econ_partner_id:
#             partner = self.registration_id.econ_partner_id
#         else:
        partner = self.registration_id.partner_id
        
        if not date_invoice:
            date_invoice = fields.Date.today()
        
        vals = {
            'partner_id': partner.id,
            'currency_id': partner.property_account_receivable.currency_id.id if partner.property_account_receivable.currency_id else self.env.user.company_id.currency_id.id,
            'type': type,
            'company_id': self.env.user.company_id.id,
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
#         if self.partner_payer_id:
#             partner = self.partner_payer_id
#         else:
        partner = self.partner_id
        if auto:
            # Find invoice to add to
            invoice = aio.search([('partner_id', '=', partner.id),
                                  ('state', '=', 'draft'),
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

            