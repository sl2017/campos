# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import base64
from StringIO import StringIO
from openerp.tools import ustr

import unicodecsv
from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class CamposImportGrpDueWiz(models.TransientModel):

    _name = 'campos.import.grp.due.wiz'

    data_file = fields.Binary('NAV Saldo Fil', required=True)
    filename = fields.Char('Filename')


    @api.multi
    def import_file(self):
        """Process the file chosen in the wizard, create bank statement(s) and
        go to reconciliation."""
        self.ensure_one()
        data_file = base64.b64decode(self.data_file)
        f = StringIO()
        f.write(data_file.lstrip())
        f.seek(0)
        try:
            for line in unicodecsv.DictReader(
                    f, encoding=self._prepare_csv_encoding(), delimiter=';', fieldnames=['date', 'ref', 'partner', 'amount']):
                pass
        except Exception as e:
            raise UserError(_('File parse error:\n%s') % ustr(e))

    