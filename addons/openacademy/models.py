from odoo import models, fields, api 
from odoo.exceptions import UserError, ValidationError


class Course(models.Model):
	"""
		Model to manage Courses
	"""
	_name = "openacademy.course"

	name = fields.Char(string="Title", required=True)
	description = fields.Text()

	responsible_id = fields.Many2one("res.users", ondelete="set null", string="Responsable", index=False)
	session_ids = fields.One2many("openacademy.session", "course_id", string="Sessions")

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

	# Add contrain to control that instructor is not in attendee_ids list
	@api.constrains('instructor_id', 'attendee_ids')
	def _check_instructor_not_in_attendees(self):
		for r in self:
			if r.instructor_id and r.instructor_id in r.attendee_ids:
				raise ValidationError("A session's instructor can't be an attendee")

			
	
