from openerp import models, fields

class Report(models.Model):
    _name = 'lost.report'
    item_id = fields.Many2one('lost.item', 'Item', ondelete='restrict', required=True)
    features = fields.Char('Features')
    last_seen_date = fields.Date('Last seen', required=True)
    handed_over_date = fields.Date('Handed over')
    comments = fields.Text('Comments')
    active = fields.Boolean('Active', default=True)