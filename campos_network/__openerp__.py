{
	'name': 'CampOS Network',
	'description': 'Lader udvalg bestille netvaerk paa bestemte koordinater.',
	'author': 'Patrick Bassing',
	'depends': [
			'mail',
			'base',
			'campos_event',
			],
	'application': True,
	'data': [
		'view_createnetwork.xml',
		'security/ir.rule.csv',
		'security/ir.model.access.csv',
        ],
}
