{
	'name':'Open Academy',
	'description': """ 
			Open Academy module for managing trainings :
				-> Training courses
				-> Training sessions
				-> Attendees registration
			""",

	'version':'1.0',

	'author':'Alain NOUTCHOMWO',

	'website':'https:wwww.team-expert.com',

	'summary': 'This modules help you to manage Training in your Academy',

	'category': 'Test',

	'depends': ['base'],

	# always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views/openacademy.xml',
        'views/partner.xml',
		'views/session_workflow'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}