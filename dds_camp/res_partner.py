# -*- coding: utf-8 -*-
##############################################################################
#
#    DDS Camp
#    Copyright (C) 2013 Hans Henrik Gabelgaard
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv


           
class res_partner(osv.osv):
    """ Inherits partner and adds DDS information in the partner form """
    _inherit = 'res.partner'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if record.parent_id and not record.is_company and not context.get('without_company'):
                name =  "%s, %s" % (record.parent_id.name, name)
            if context.get('show_address'):
                name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
                name = name.replace('\n\n','\n')
                name = name.replace('\n\n','\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            if context.get('add_email') and record.email:
                name = "%s\n<%s>" % (name, record.email)    
            if context.get('name_only'):
                name = record.name    
            res.append((record.id, name))
        return res
    
    def create_camp_invoice(self, cr, uid, ids, product_id=None, datas=None, context=None):
        """ Create Customer Invoice for partners.
        @param datas: datas has dictionary value which consist Id of Membership product, Line Name and Cost Amount of Membership.
                      datas = {'invoice_product_id': None, 'amount': None, 'line_name' : 'text'}
        """
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoice_tax_obj = self.pool.get('account.invoice.tax')
        product_id = product_id or datas.get('invoice_product_id', False)
        amount = datas.get('amount', 0.0)
        invoice_list = []
        if type(ids) in (int, long,):
            ids = [ids]
        for partner in self.browse(cr, uid, ids, context=context):
            account_id = partner.property_account_receivable and partner.property_account_receivable.id or False
            fpos_id = partner.property_account_position and partner.property_account_position.id or False
            addr = self.address_get(cr, uid, [partner.id], ['invoice'])
            
            if not addr.get('invoice', False):
                raise osv.except_osv(_('Error!'),
                        _("Partner doesn't have an address to make the invoice."))
            quantity = 1
            line_value =  {
                'product_id': product_id,
            }

            line_dict = invoice_line_obj.product_id_change(cr, uid, {},
                            product_id, False, quantity, '', 'out_invoice', partner.id, fpos_id, price_unit=amount, context=context)
            line_value.update(line_dict['value'])
            line_value['price_unit'] = amount
            if datas.get('line_name', False):
                line_value['name'] = datas.get('line_name', False)
            if line_value.get('invoice_line_tax_id', False):
                tax_tab = [(6, 0, line_value['invoice_line_tax_id'])]
                line_value['invoice_line_tax_id'] = tax_tab

            invoice_id = invoice_obj.create(cr, uid, {
                'partner_id': partner.id,
                'account_id': account_id,
                'fiscal_position': fpos_id or False
                }, context=context)
            line_value['invoice_id'] = invoice_id
            invoice_line_id = invoice_line_obj.create(cr, uid, line_value, context=context)
            invoice_obj.write(cr, uid, invoice_id, {'invoice_line': [(6, 0, [invoice_line_id])]}, context=context)
            invoice_list.append(invoice_id)
            if line_value['invoice_line_tax_id']:
                tax_value = invoice_tax_obj.compute(cr, uid, invoice_id).values()
                for tax in tax_value:
                    invoice_tax_obj.create(cr, uid, tax, context=context)
        #recompute the membership_state of those partners
        #self.pool.get('res.partner').write(cr, uid, ids, {})
        return invoice_list
    
    def create_camp_invoice_mul(self, cr, uid, ids, data=None, context=None):
        """ Create Customer Invoice for partners.
        @param datas: datas has dictionary value which consist Id of Membership product, Line Name and Cost Amount of Membership.
                      datas = {'invoice_product_id': None, 'amount': None, 'line_name' : 'text'}
        """
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoice_tax_obj = self.pool.get('account.invoice.tax')
        #product_id = product_id or datas.get('invoice_product_id', False)
        
        invoice_list = []
        if type(ids) in (int, long,):
            ids = [ids]
        for partner in self.browse(cr, uid, ids, context=context):
            account_id = partner.property_account_receivable and partner.property_account_receivable.id or False
            fpos_id = partner.property_account_position and partner.property_account_position.id or False
            addr = self.address_get(cr, uid, [partner.id], ['invoice'])
            
            if not addr.get('invoice', False):
                raise osv.except_osv(_('Error!'),
                        _("Partner doesn't have an address to make the invoice."))
            invoice_id = invoice_obj.create(cr, uid, {
                'partner_id': partner.id,
                'account_id': account_id,
                'fiscal_position': fpos_id or False
                }, context=context)
            
            invoice_line_ids = []
            for datas in data:
                quantity = datas.get('quantity', 1)
                amount = datas.get('amount', 0.0)
                print "Create line, ", quantity, amount
                line_value =  {
                               'product_id': datas['invoice_product_id'],
                               'quantity': quantity
                               }

                line_dict = invoice_line_obj.product_id_change(cr, uid, {},
                                                               datas['invoice_product_id'], False, quantity, '', 'out_invoice', partner.id, fpos_id, price_unit=amount, context=context)
                line_value.update(line_dict['value'])
                line_value['price_unit'] = amount
                if datas.get('line_name', False):
                    line_value['name'] = datas.get('line_name', False)
                if line_value.get('invoice_line_tax_id', False):
                    tax_tab = [(6, 0, line_value['invoice_line_tax_id'])]
                    line_value['invoice_line_tax_id'] = tax_tab

            
                line_value['invoice_id'] = invoice_id
                invoice_line_id = invoice_line_obj.create(cr, uid, line_value, context=context)
                invoice_line_ids.append(invoice_line_id)    
            invoice_obj.write(cr, uid, invoice_id, {'invoice_line': [(6, 0, invoice_line_ids)]}, context=context)
            invoice_list.append(invoice_id)
            if line_value['invoice_line_tax_id']:
                tax_value = invoice_tax_obj.compute(cr, uid, invoice_id).values()
                for tax in tax_value:
                    invoice_tax_obj.create(cr, uid, tax, context=context)
        #recompute the membership_state of those partners
        #self.pool.get('res.partner').write(cr, uid, ids, {})
        return invoice_list
    
res_partner()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
