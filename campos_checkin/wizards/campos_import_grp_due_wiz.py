# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import base64
from StringIO import StringIO
from openerp.tools import ustr

import unicodecsv
import re
from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class CamposImportGrpDueWiz(models.TransientModel):

    _name = 'campos.import.grp.due.wiz'

    data_file = fields.Binary('NAV Saldo Fil', required=True)
    filename = fields.Char('Filename')


    @api.model
    def _prepare_csv_encoding(self):
        '''This method is designed to be inherited'''
        return 'latin1'
    
    @api.model
    def _csv_convert_amount(self, amount_str):
        '''This method is designed to be inherited'''
        valstr = re.sub(r'[^\d,.-]', '', amount_str)
        valstrdot = valstr.replace('.', '')
        valstrdot = valstrdot.replace(',', '.')
        return float(valstrdot)
    
    @api.multi
    def import_file(self):
        """Process the file chosen in the wizard, create bank statement(s) and
        go to reconciliation."""
        self.ensure_one()
        data_file = base64.b64decode(self.data_file)
        f = StringIO()
        f.write(data_file.lstrip())
        f.seek(0)
        n = 0
        try:
            for line in unicodecsv.DictReader(
                    f, encoding=self._prepare_csv_encoding(), delimiter=';'):
                refnr = line['Nummer']
                n += 1
                grp = self.env['event.registration'].search([('partner_id.ref','=', refnr)])
                if grp:
                    grp[0].nav_due_amount = self._csv_convert_amount(line['Saldo (RV)'])
                    if line['Valutakode'] == 'EUR':
                        grp[0].nav_due_amount_eur = self._csv_convert_amount(line['Saldo'])
        except Exception as e:
            raise UserError(_('File parse error:\n%s\nLine: %d') % (ustr(e), n))

    