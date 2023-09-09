# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import models, fields, api, _, http
from odoo.exceptions import UserError


class srSalePriceHistory(models.Model):
    _name = 'sr.sale.price.history'
    _description = 'Sale Price History'

    name = fields.Many2one("sale.order.line",string="Sale Order Line")
    partner_id = fields.Many2one("res.partner",string="Customer")
    user_id = fields.Many2one("res.users",string="Sales Person")
    product_tmpl_id = fields.Many2one("product.template",string="Template Id")
    variant_id = fields.Many2one("product.product",string="Product")
    sale_order_id = fields.Many2one("sale.order",string="Sale Order")
    sale_order_date = fields.Datetime(string="Order Date")
    product_uom_qty = fields.Float(string="Quantity")
    #unit_price = fields.Monetary("Price", currency_field="currency_id", compute="_compute_base_unit_price")
    unit_price = fields.Float(string="Price")

   # unit_price = fields.Float(string="Price", required=True, default=0,
       #                             compute='_compute_base_unit_count', inverse='_set_base_unit_count', store=True,
        #                           help="Display base unit price on your eCommerce pages. Set to 0 to hide it for this product.")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id.id)

    #he4i el originale :
    #currency_id = fields.Many2one("res.currency",string="Currency Id")
    total_price = fields.Monetary(string="Total")
"""
    #@api.depends('list_price', 'unit_price')
    def _compute_base_unit_price(self):
        for template in self:
            template.unit_price = template._get_unit_price(template.product_tmpl_id.list_price)
    def _get_unit_price(self, price):
        self.ensure_one()
        return self.unit_price and price / self.unit_price

    def _compute_base_unit_count(self):
        self.unit_price = 0
        for template in self.filtered(lambda template: len(template.variant_id) == 1):
            template.unit_price =template.unit_price
    def _set_base_unit_count(self):
        for template in self:
            if len(template.product_tmpl_id.product_variant_ids) == 1:
                template.unit_price = template.unit_price

"""




