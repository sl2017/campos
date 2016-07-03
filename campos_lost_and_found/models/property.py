from openerp import models, fields

class Property(models.Model):
    _name = 'lost.property'
    item_id = fields.Many2one('lost.item', 'Item', ondelete='restrict', required=True)
    features = fields.Char('Features')
    registered_date = fields.Date('Registered', required=True)
    handed_over_date = fields.Date('Handed over')
    comments = fields.Text('Comments')
    active = fields.Boolean('Active', default=True)