# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################
from datetime import datetime
import numpy as np
# import pandas as pd

from odoo import models, fields, api, _, http
from odoo.addons.website.controllers.form import WebsiteForm
from odoo.exceptions import UserError
from odoo.http import request
globalDate = ""
dates = np.array([])
values = np.array([])




class ProductTemplate(models.Model):
    _inherit = 'product.template'

    date_to_predict = fields.Text(string="name")

    def _get_sale_price_history(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        sale_history_obj = self.env['sr.sale.price.history'].sudo()
        sale_history_ids = []
        sale_history_prices = []
        sale_history_dates = []
        sale_history_products = []
        domain = [('product_id', 'in', self.product_variant_ids.ids)]
        sale_order_line_record_limit = int(ICPSudo.get_param('sale_order_line_record_limit'))
        sale_order_status = ICPSudo.get_param('sale_order_status')
        if not sale_order_line_record_limit:
            sale_order_line_record_limit = 30
        if not sale_order_status:
            sale_order_status = 'sale'
        if sale_order_status == 'sale':
            domain += [('state', '=', 'sale')]
        elif sale_order_status == 'done':
            domain += [('state', '=', 'done')]
        else:
            domain += [('state', '=', ('sale', 'done'))]
        current_website = self.env['website'].get_current_website()
        pricelist = current_website.get_current_pricelist()
        currency_converter = request.env['res.currency']._convert
        sale_order_line_ids = self.env['sale.order.line'].sudo().search(domain, limit=sale_order_line_record_limit,
                                                                        order='create_date desc')
        for line in sale_order_line_ids:
            sale_price_history_id = sale_history_obj.create({
                'name': line.id,
                'partner_id': line.order_partner_id.id,
                'user_id': line.salesman_id.id,
                'product_tmpl_id': line.product_id.product_tmpl_id.id,
                'variant_id': line.product_id.id,
                'sale_order_id': line.order_id.id,
                'sale_order_date': line.order_id.date_order,
                'product_uom_qty': line.product_uom_qty,
                'unit_price': currency_converter(
                    line.price_unit, pricelist.currency_id, current_website.company_id, fields.Date.today(), False

                    # line.price_unit, line.currency_id,
                    # request.env['res.currency'].browse(line.currency_id.id),
                    # fields.Date.today(), False
                ),

                'currency_id': line.currency_id.id,
                'total_price': line.price_subtotal
            })
            sale_history_prices.append(line.price_unit)
            sale_history_dates.append(line.order_id.date_order)
            sale_history_products.append(sale_price_history_id)
            sale_history_ids.append(sale_price_history_id.id)

        self.sale_price_history_prices = sale_history_prices
        self.sale_price_history_dates = sale_history_dates
        # -------------> Order ProductsSaleHistory Accourding to sale_order_date methode 2 (meilleure)
        sorted_products = sorted(sale_history_products, key=lambda x: x["sale_order_date"])
        self.sale_price_history_products = sorted_products
        # ---------------
        self.sale_price_history_ids = sale_history_ids

    def _get_purchase_price_history(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        purchase_history_obj = self.env['sr.purchase.price.history'].sudo()
        purchase_history_ids = []
        domain = [('product_id', 'in', self.product_variant_ids.ids)]
        purchase_order_line_record_limit = int(ICPSudo.get_param('purchase_order_line_record_limit'))
        purchase_order_status = ICPSudo.get_param('purchase_order_status')
        if not purchase_order_line_record_limit:
            purchase_order_line_record_limit = 30
        if not purchase_order_status:
            purchase_order_status = 'purchase'
        if purchase_order_status == 'purchase':
            domain += [('state', '=', 'purchase')]
        elif purchase_order_status == 'done':
            domain += [('state', '=', 'done')]
        else:
            domain += [('state', '=', ('purchase', 'done'))]

        purchase_order_line_ids = self.env['purchase.order.line'].sudo().search(domain,
                                                                                limit=purchase_order_line_record_limit,
                                                                                order='create_date desc')
        for line in purchase_order_line_ids:
            purchase_price_history_id = purchase_history_obj.create({
                'name': line.id,
                'partner_id': line.partner_id.id,
                'user_id': line.order_id.user_id.id,
                'product_tmpl_id': line.product_id.product_tmpl_id.id,
                'variant_id': line.product_id.id,
                'purchase_order_id': line.order_id.id,
                'purchase_order_date': line.order_id.date_order,
                'product_uom_qty': line.product_qty,
                'unit_price': line.price_unit,
                'currency_id': line.currency_id.id,
                'total_price': line.price_total
            })
            purchase_history_ids.append(purchase_price_history_id.id)
        self.purchase_price_history_ids = purchase_history_ids

    sale_price_history_prices = fields.Many2many("sr.sale.price.history", string="Sale Price History",
                                                 compute="_get_sale_price_history")
    sale_price_history_dates = fields.Many2many("sr.sale.price.history", string="Sale Price History",
                                                compute="_get_sale_price_history")
    sale_price_history_products = fields.Many2many("sr.sale.price.history", string="Sale Price History",
                                                   compute="_get_sale_price_history")
    sale_price_history_ids = fields.Many2many("sr.sale.price.history", string="Sale Price History",
                                              compute="_get_sale_price_history")
    purchase_price_history_ids = fields.Many2many("sr.purchase.price.history", string="Purchase Price History",
                                                  compute="_get_purchase_price_history")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_sale_price_history(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        sale_history_obj = self.env['sr.sale.price.history'].sudo()
        sale_history_ids = []
        sale_history_prices = []
        sale_history_dates = []
        sale_history_products = []
        currency_converter = request.env['res.currency']._convert
        current_website = self.env['website'].get_current_website()
        pricelist = current_website.get_current_pricelist()
        domain = [('product_id', 'in', self.ids)]
        sale_order_line_record_limit = int(ICPSudo.get_param('sale_order_line_record_limit'))
        sale_order_status = ICPSudo.get_param('sale_order_status')
        if not sale_order_line_record_limit:
            sale_order_line_record_limit = 30
        if not sale_order_status:
            sale_order_status = 'sale'
        if sale_order_status == 'sale':
            domain += [('state', '=', 'sale')]
        elif sale_order_status == 'done':
            domain += [('state', '=', 'done')]
        else:
            domain += [('state', '=', ('sale', 'done'))]

        sale_order_line_ids = self.env['sale.order.line'].sudo().search(domain, limit=sale_order_line_record_limit,
                                                                        order='create_date desc')
        for line in sale_order_line_ids:
            sale_price_history_id = sale_history_obj.create({
                'name': line.id,
                'partner_id': line.order_partner_id.id,
                'user_id': line.salesman_id.id,
                'product_tmpl_id': line.product_id.product_tmpl_id.id,
                'variant_id': line.product_id.id,
                'sale_order_id': line.order_id.id,
                'sale_order_date': line.order_id.date_order,
                'product_uom_qty': line.product_uom_qty,
                'unit_price': currency_converter(
                    line.price_unit, pricelist.currency_id, current_website.company_id, fields.Date.today(), False

                    # line.price_unit, line.currency_id,
                    # request.env['res.currency'].browse(line.currency_id.id),
                    # fields.Date.today(), False
                ),
                'currency_id': line.currency_id.id,
                'total_price': line.price_subtotal,
            })
            sale_history_prices.append(line.price_unit)
            sale_history_dates.append(line.order_id.date_order)
            sale_history_products.append(sale_price_history_id)
            sale_history_ids.append(sale_price_history_id.id)
        self.sale_price_history_prices = sale_history_prices
        self.sale_price_history_dates = sale_history_dates
        self.sale_price_history_products = sale_history_products

        self.sale_price_history_ids = sale_history_ids

    def _get_purchase_price_history(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        purchase_history_obj = self.env['sr.purchase.price.history'].sudo()
        purchase_history_ids = []
        domain = [('product_id', 'in', self.product_variant_ids.ids)]
        purchase_order_line_record_limit = int(ICPSudo.get_param('purchase_order_line_record_limit'))
        purchase_order_status = ICPSudo.get_param('purchase_order_status')
        if not purchase_order_line_record_limit:
            purchase_order_line_record_limit = 30
        if not purchase_order_status:
            purchase_order_status = 'purchase'
        if purchase_order_status == 'purchase':
            domain += [('state', '=', 'purchase')]
        elif purchase_order_status == 'done':
            domain += [('state', '=', 'done')]
        else:
            domain += [('state', '=', ('purchase', 'done'))]

        purchase_order_line_ids = self.env['purchase.order.line'].sudo().search(domain,
                                                                                limit=purchase_order_line_record_limit,
                                                                                order='create_date desc')
        for line in purchase_order_line_ids:
            purchase_price_history_id = purchase_history_obj.create({
                'name': line.id,
                'partner_id': line.partner_id.id,
                'user_id': line.order_id.user_id.id,
                'product_tmpl_id': line.product_id.product_tmpl_id.id,
                'variant_id': line.product_id.id,
                'purchase_order_id': line.order_id.id,
                'purchase_order_date': line.order_id.date_order,
                'product_uom_qty': line.product_qty,
                'unit_price': line.price_unit,
                'currency_id': line.currency_id.id,
                'total_price': line.price_total
            })
            purchase_history_ids.append(purchase_price_history_id.id)
        self.purchase_price_history_ids = purchase_history_ids

    sale_price_history_prices = fields.Many2many("sr.sale.price.history", string="Sale Price History",
                                                 compute="_get_sale_price_history")
    sale_price_history_dates = fields.Many2many("sr.sale.price.history", string="Sale Price History",
                                                compute="_get_sale_price_history")
    sale_price_history_products = fields.Many2many("sr.sale.price.history", string="Sale Price History",
                                                   compute="_get_sale_price_history")
    sale_price_history_ids = fields.Many2many("sr.sale.price.history", string="Sale Price History",
                                              compute="_get_sale_price_history")
    purchase_price_history_ids = fields.Many2many("sr.purchase.price.history", string="Purchase Price History",
                                                  compute="_get_purchase_price_history")
