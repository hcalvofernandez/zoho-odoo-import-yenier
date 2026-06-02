# -*- coding: utf-8 -*-
"""
DoorAndDoor - Estado de Entrega en Picking
Modelo: stock.move
"""

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    # -------------------------------------------------------------------------
    # CAMPOS
    # -------------------------------------------------------------------------

    qty_ordered = fields.Float(
        string='Cantidad Pedida',
        compute='_compute_qty_ordered',
        store=False,
        readonly=True,
        help='Cantidad original pedida en la venta (desde sale.order.line)',
        digits='Product Unit of Measure',
    )

    qty_delivered_this = fields.Float(
        string='Entregado',
        compute='_compute_qty_delivered_this',
        inverse='_inverse_qty_delivered_this',
        store=True,
        help='Cantidad entregada en ESTE picking específico',
        digits='Product Unit of Measure',
    )

    qty_pending = fields.Float(
        string='Pendiente',
        compute='_compute_qty_pending',
        store=False,
        readonly=True,
        help='Cantidad pendiente por entregar = Pedida - Entregado (este picking)',
        digits='Product Unit of Measure',
    )

    has_sale_order = fields.Boolean(
        string='Tiene Venta',
        compute='_compute_has_sale_order',
        store=False,
        help='Indica si este movimiento está vinculado a una venta',
    )

    # -------------------------------------------------------------------------
    # MÉTODOS COMPUTE
    # -------------------------------------------------------------------------

    @api.depends('sale_line_id', 'sale_line_id.product_uom_qty')
    def _compute_qty_ordered(self):
        """
        Calcula la cantidad pedida original desde la línea de venta.
        Si no hay venta relacionada, muestra 0.
        """
        for move in self:
            if move.sale_line_id:
                move.qty_ordered = move.sale_line_id.product_uom_qty
            else:
                move.qty_ordered = 0.0

    @api.depends('quantity_done', 'product_uom_qty')
    def _compute_qty_delivered_this(self):
        """
        Calcula la cantidad entregada en ESTE picking.
        Usa quantity_done (cantidad realizada en el picking actual).
        """
        for move in self:
            # quantity_done es el campo nativo de Odoo para cantidad hecha
            move.qty_delivered_this = move.quantity_done or 0.0

    def _inverse_qty_delivered_this(self):
        """
        Permite editar qty_delivered_this y reflejarlo en quantity_done.
        Esto mantiene sincronización bidireccional.
        """
        for move in self:
            move.quantity_done = move.qty_delivered_this

    @api.depends('qty_ordered', 'qty_delivered_this')
    def _compute_qty_pending(self):
        """
        Calcula la cantidad pendiente: Pedida - Entregado (este picking).
        Si no hay venta, muestra 0.
        """
        for move in self:
            if move.sale_line_id:
                move.qty_pending = move.qty_ordered - move.qty_delivered_this
            else:
                move.qty_pending = 0.0

    @api.depends('picking_id.sale_id')
    def _compute_has_sale_order(self):
        """
        Indica si el movimiento está vinculado a una venta.
        """
        for move in self:
            move.has_sale_order = bool(move.picking_id.sale_id)

    # -------------------------------------------------------------------------
    # MÉTODOS HEREDADOS
    # -------------------------------------------------------------------------

    def write(self, vals):
        """
        Sobrescribe write para asegurar que qty_delivered_this se mantenga
        sincronizado con quantity_done cuando se edita desde otras vistas.
        """
        res = super(StockMove, self).write(vals)
        if 'quantity_done' in vals and 'qty_delivered_this' not in vals:
            # quantity_done cambió desde otra vista, sincronizar
            for move in self:
                move.qty_delivered_this = move.quantity_done
        return res
