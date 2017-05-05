# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposActivityPeriod(models.Model):

    _name = 'campos.activity.period'
    _description = 'Campos Activity Period'

    name = fields.Char('Name', size=128, translate=True)
    date_begin = fields.Datetime('Start Date/Time', required=True)
    date_end = fields.Datetime('End Date/Time', required=True) 
    
    @api.multi
    @api.depends('name', 'date_begin', 'date_end')
    def name_get(self):
        result = []
        for period in self:
            date_begin = fields.Datetime.from_string(period.date_begin)
            date_end = fields.Datetime.from_string(period.date_end)
            dates = [fields.Datetime.to_string(fields.Datetime.context_timestamp(period, dt)) for dt in [date_begin, date_end] if dt]
            dates = sorted(set(dates))
            result.append((period.id, '%s (%s)' % (period.name, ' - '.join(dates))))
        return result