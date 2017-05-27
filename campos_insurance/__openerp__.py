{
	'name': 'CampOS Insurance',
	'description': 'Tillader forsikring af udstyr på SL2017',
	'author': 'Patrick Bassing',
	'depends': [
			'mail',
			'base',
			'campos_event'
			],
	'application': True,
	'data': [
        'security/campos_insurance_security.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.csv',
		'views/view_category.xml',
		'views/view_insurance.xml'
        ],
}
