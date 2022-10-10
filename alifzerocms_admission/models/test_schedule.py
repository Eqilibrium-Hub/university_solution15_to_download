from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import pdb


class alifzerocmsEntryTestCenter(models.Model):
    _name = "alifzerocms.admission.test.center"
    _description = "Admission Test Center"

    name = fields.Char(string='City Name', required=True)
    code = fields.Char(string='City Code', required=True)
    test_type = fields.Selection([('cbt', 'Computer Based Test'), ('pbt', 'Paper Based Test')], default="cbt")
    time_ids = fields.One2many('alifzerocms.admission.test.time', 'time_id', 'Test Time')
    #discipline_id = fields.Many2one('alifzerocms.discipline', required=True)
    # center_id = fields.Many2one('alifzerocms.application')


class alifzerocmsEntryTestTime(models.Model):
    _name = "alifzerocms.admission.test.time"
    _description = "Admission Test Time"
    _rec_name = 'date'

    date = fields.Date('Test Date', required=True)
    time = fields.Float(string='Test Time', required=True)
    active_time = fields.Boolean('Active', default=True)
    capacity = fields.Integer('Capacity')
    time_id = fields.Many2one('alifzerocms.admission.test.center')

    # slot_id = fields.Many2one('alifzerocms.application')

    def name_get(self):
        res = []
        for record in self:
            if record.date:
                time = '%02d:%02d' % (divmod(record.time * 60, 60))
                name = str(record.date) + ' ( ' + str(time) + ' )'
                res.append((record.id, name))
        return res
