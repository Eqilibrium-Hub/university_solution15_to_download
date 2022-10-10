
from odoo import fields, models, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import pdb
from datetime import date


class alifzerocmsMeritRegisterWizardLine(models.TransientModel):
    _name = 'alifzerocms.merit.register.wizard.line'
    _description = 'Merit Register Wizard Lines'

    register_id = fields.Many2one('alifzerocms.merit.register.wizard', string='Register')
    serial_start = fields.Integer('Serial Start')
    serial_end = fields.Integer('Serial End')
    date_interview = fields.Date('Date Interview')


class alifzerocmsMeritRegisterWizard(models.TransientModel):
    _name = 'alifzerocms.merit.register.wizard'
    _description = 'Merit Register Wizard'

    @api.model
    def _get_register(self):
        if self._context.get('active_model', False) == 'alifzerocms.admission.register' and self._context.get('active_id', False):
            return self.env['alifzerocms.admission.register'].browse(self._context.get('active_id', False))

    register_id = fields.Many2one('alifzerocms.admission.register', string='Register',default=_get_register, required=True)
    name = fields.Many2one('alifzerocms.merit.list', 'Merit List',compute='_get_list')
    date_list = fields.Date('Date List',required=True, default=date.today())
    total_seats = fields.Integer('Total Seats',compute='_get_list')
    merit_seats = fields.Integer('Merit List For',compute='_get_list')
    comment = fields.Char('Warning')
    remarks = fields.Text('Remarks',default='Please bring your Documents along with Fee')
    line_ids = fields.One2many('alifzerocms.merit.register.wizard.line','register_id','Interview Schedule')
    date_end = fields.Date('Closing Date')

    # In Case of Change
    # #new_rep = fields.Selection([('new','New'),('edit','Edit')],'List', default='new')
    # #merit_list = fields.Many2one('alifzerocms.merit.register','Merit List')

    @api.depends('register_id')
    def _get_list(self):
        if self.register_id:
            if self.register_id.merit_register_id:
                # This is just to ensure all the applicants are processeed before generating next merit list.
                if any([app.state == 'draft' for app in self.register_id.merit_register_id.merit_application_ids]):
                    self.comment = "Please Process %s first before generating next." % (self.register_id.merit_register_id.merit_list_id.name,)

            next_number = self.register_id.merit_register_id and self.register_id.merit_register_id.merit_list_id.number + 1 or 1
            merit_list = self.env['alifzerocms.merit.list'].search([('number', '=', next_number)])
            if merit_list:
                self.name = merit_list.id
            else:
                self.comment = "There is no Merit List defined for Number %s" % (next_number,)

            allocation_id = self.env['alifzerocms.admission.allocation'].search([
                ('academic_session_id','=',self.register_id.academic_session_id.id),('career_id','=',self.register_id.career_id.id)
            ])
            self.total_seats = sum(program.seats for program in allocation_id.seat_ids)
            locked = len(self.register_id.application_ids.filtered(lambda l: l.locked == True))
            self.merit_seats = self.total_seats - locked

    def generate_merit_register(self):
        req = self.merit_seats
        planned = 0
        for line in self.line_ids:
            if line.serial_end > planned:
                planned = line.serial_end
            if line.date_interview < self.date_list:
                raise UserError("Interview Date cannot be Prior to Merit List Date")
        if planned < req:
            raise UserError("Interview Date not Scheduled for all Seats")

        data = {
            'register_id': self.register_id.id,
            'name': self.name.name + ' / ' + self.register_id.name,
            'date_list': self.date_list,
            'merit_list_id': self.name.id,
            'remarks': self.remarks,
        }
        merit_register = self.env['alifzerocms.merit.register'].create(data)
        if self.register_id.merit_register_id:
            self.register_id.merit_register_id.next_merit_register_id = merit_register.id
            merit_register.prev_merit_register_id = self.register_id.merit_register_id.id
        else:
            self.register_id.first_merit_register_id = merit_register.id

        self.register_id.merit_register_id = merit_register.id
        self.register_id.merit_list(merit_register, self.line_ids)


