
from odoo import fields, models, api


class alifzerocmsApplicationReject(models.TransientModel):
    _name = 'alifzerocms.application.reject'
    _description = 'Choose Reject Reason'

    reject_reason_id = fields.Many2one('alifzerocms.application.reject.reason', string="Reason",
        help="Select Reason for rejecting the Applications")


    def action_reject_reason_apply(self):
        for rec in self:
            application = self.env['alifzerocms.application'].browse(self.env.context.get('active_ids'))
            application.write({'reject_reason': rec.reject_reason_id.id})
            return application.reject_application()

