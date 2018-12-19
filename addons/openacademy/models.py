from odoo import models, fields, api 
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class Course(models.Model):
	"""
		Model to manage Courses
	"""
	_name = "openacademy.course"

	name = fields.Char(string="Title", required=True)
	description = fields.Text()

	responsible_id = fields.Many2one("res.users", ondelete="set null", string="Responsable", index=False)
	session_ids = fields.One2many("openacademy.session", "course_id", string="Sessions")

	#Re-implemente copy method because the name of course is unique so we cannot duplicate the course
	@api.multi 
	def copy(self, default=None):
		default = dict(default or {})

		copied_count = self.search_count(
			[('name', '=like', u"Copy of {}%".format(self.name))]
		)
		if not copied_count:
			new_name = u"Copy of {}".format(self.name)
		else:
			new_name = u"Copy of {} ({})".format(self.name, copied_count)

		default['name'] = new_name
		return super(Course, self).copy(default)

	# Contrais who check if the name of course is unique and if the the title and the description are differents
	_sql_constraints = [
		(
			'name_description_check',
			'CHECK(name != description)',
			'The Title of the course should not be the desciption'
		),
		(
			'name_unique',
			'UNIQUE(name)',
			'The course title must be unique',
		),
	]
	


class Session(models.Model):
	"""
		This model manage session of courses
	"""
	_name = "openacademy.session"

	name = fields.Char(required=True)
	start_date = fields.Date(defaul=fields.Date.today)
	duration = fields.Float(digits=(6,2), help="Duration in days")
	seats = fields.Integer(string="Number of seats")
	active = fields.Boolean(string="Active/Desactive", default=True)

	instructor_id = fields.Many2one("res.partner", string="Instructor")
	course_id = fields.Many2one("openacademy.course", ondelete="cascade", string="Course", required=True)
	attendee_ids = fields.Many2many("res.partner", string="Attendees")

	taken_seats = fields.Float(string="Taken seats", compute="_taken_seats")
	end_date = fields.Date(string="End Date", store=True, compute="_get_end_date", inverse="_set_end_date")

	attendees_count = fields.Integer(string="Attendees count", compute="_get_attentdees_count", store=True)

	state = fields.Selection(
		string=u'state',
		selection=[
			('draft', 'Draft'),
			('confirmed', 'Confirmed'),
			('done','Done')
		],
		default="draft"
	)
	
	@api.multi   
	def action_draft(self):
		self.state = 'draft'

	@api.multi   
	def action_confirm(self):
		self.state = 'confirmed'
	
	@api.multi   
	def action_done(self):
		self.state = 'done'
	
	# This decorator manage computer field
	@api.depends("seats", "attendee_ids")
	def _taken_seats(self):
		for r in self:
			if not r.seats:
				r.taken_seats = 0.0
			else:
				if r.seats >= len(r.attendee_ids):
					r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats	
				else:
					r.taken_seats = 100.0

	#Trigger change of seats and attendee_ids field and make update
	@api.onchange('seats', 'attendee_ids')
	def _verify_valid_seats(self):
		if self.seats < 0:
			return {
				'warning': {
					'title': "Incorrrect 'Number of seats' value",
					'message': 'The number of available seats may not be negative value'
				},
			}
		if self.seats < len(self.attendee_ids):
			return {
				'warning': {
					'title': "Too many attendees",
					'message': "Increase seats or remove excess attendees"
				},
			}


	@api.depends('start_date', 'duration')
	def _get_end_date(self):
		for r in self:
			if not(r.start_date and r.duration):
				r.end_date = r.start_date
				continue

			# Add duration to start_date, but : Munday+5=Saturday, so
			#subtract one second to get on Friday intead
			start = fields.Datetime.from_string(r.start_date)
			duration = timedelta(days=r.duration, seconds=-1)
			r.end_date = start + duration

	def _set_end_date(self):
		for r in self:
			if not (r.start_date and r.end_date):
				continue

			start_date = fields.Datetime.from_string(r.start_date)
			end_date = fields.Datetime.from_string(r.end_date)
			r.duration = (end_date - start_date).days + 1	


	@api.depends('attendee_ids')
	def _get_attentdees_count(self):
		for r in self:
			r.attendees_count = len(r.attendee_ids)
	

	# Add contrain to control that instructor is not in attendee_ids list
	@api.constrains('instructor_id', 'attendee_ids')
	def _check_instructor_not_in_attendees(self):
		for r in self:
			if r.instructor_id and r.instructor_id in r.attendee_ids:
				raise ValidationError("A session's instructor can't be an attendee")

			
	
