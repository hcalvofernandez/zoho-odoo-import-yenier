from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import SavepointCase


@tagged("post_install", "-at_install")
class TestInvoiceToSaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Cliente Pruebas DoorAndDoor",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Producto Prueba DDSN",
                "type": "consu",
                "list_price": 120.0,
            }
        )
        cls.component_product = cls.env["product.product"].create(
            {
                "name": "Componente DDSN",
                "type": "consu",
                "list_price": 10.0,
            }
        )
        cls.manufactured_product = cls.env["product.product"].create(
            {
                "name": "Producto Fabricado DDSN",
                "type": "product",
                "list_price": 300.0,
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.manufactured_product.product_tmpl_id.id,
                "product_uom_id": cls.manufactured_product.uom_id.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.component_product.id,
                            "product_qty": 1.0,
                            "product_uom_id": cls.component_product.uom_id.id,
                        },
                    )
                ],
            }
        )

    def _create_customer_invoice(self):
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.display_name,
                            "quantity": 2.0,
                            "price_unit": 120.0,
                        },
                    )
                ],
            }
        )
        return move

    def _create_manufacturing_invoice(self):
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.manufactured_product.id,
                            "name": self.manufactured_product.display_name,
                            "quantity": 2.0,
                            "price_unit": 300.0,
                        },
                    )
                ],
            }
        )
        return move

    def test_invoice_post_creates_sale_order_and_fulfillment(self):
        move = self._create_customer_invoice()

        move.action_post()

        self.assertTrue(move.sale_order_id, "La factura debe generar un pedido de venta en borrador.")
        self.assertEqual(move.sale_order_id.state, "draft")
        self.assertEqual(len(move.sale_order_id.order_line), 1)
        self.assertEqual(len(move.fulfillment_line_ids), 1)

        invoice_line = move.invoice_line_ids.filtered(lambda line: line.product_id)
        fulfillment_line = move.fulfillment_line_ids

        self.assertEqual(invoice_line.generated_sale_line_id, move.sale_order_id.order_line)
        self.assertEqual(invoice_line.fulfillment_line_id, fulfillment_line)
        self.assertEqual(fulfillment_line.qty_invoiced, 2.0)
        self.assertEqual(fulfillment_line.qty_pending_payment, 2.0)
        self.assertEqual(fulfillment_line.qty_pending_delivery, 2.0)

    def test_posting_same_invoice_does_not_duplicate_fulfillment_lines(self):
        move = self._create_customer_invoice()

        move.action_post()
        first_sale_order = move.sale_order_id
        first_fulfillment_count = len(move.fulfillment_line_ids)
        move._ddsn_create_sale_orders_and_fulfillment()

        self.assertEqual(move.sale_order_id, first_sale_order)
        self.assertEqual(len(move.fulfillment_line_ids), first_fulfillment_count)

    def test_prorated_release_updates_fulfillment_lines(self):
        move = self._create_customer_invoice()
        move.payment_release_policy = "prorated"
        move.action_post()

        move._ddsn_apply_release_for_amount(move.amount_total / 2)

        fulfillment_line = move.fulfillment_line_ids
        self.assertEqual(fulfillment_line.qty_released, 1.0)
        self.assertEqual(fulfillment_line.qty_pending_payment, 1.0)
        self.assertEqual(move.release_state, "partially_released")

    def test_release_creates_stock_picking(self):
        move = self._create_customer_invoice()
        move.action_post()

        move._ddsn_apply_release_for_amount(move.amount_total)

        fulfillment_line = move.fulfillment_line_ids
        self.assertTrue(fulfillment_line.picking_id, "La liberacion debe crear un picking de salida.")
        self.assertEqual(fulfillment_line.qty_sent_stock, fulfillment_line.qty_released)
        self.assertEqual(fulfillment_line.state, "in_process")
        self.assertEqual(move.picking_count, 1)

    def test_release_creates_mrp_production(self):
        move = self._create_manufacturing_invoice()
        move.fulfillment_route_policy = "force_mrp"
        move.action_post()

        move._ddsn_apply_release_for_amount(move.amount_total)

        fulfillment_line = move.fulfillment_line_ids
        self.assertTrue(fulfillment_line.mrp_production_id, "La liberacion debe crear una orden de fabricacion.")
        self.assertEqual(fulfillment_line.qty_sent_mrp, fulfillment_line.qty_released)
        self.assertEqual(fulfillment_line.state, "in_process")
        self.assertEqual(move.mrp_production_count, 1)

    def test_completed_mrp_creates_outgoing_picking(self):
        move = self._create_manufacturing_invoice()
        move.fulfillment_route_policy = "force_mrp"
        move.action_post()
        move._ddsn_apply_release_for_amount(move.amount_total)

        fulfillment_line = move.fulfillment_line_ids
        picking = move._ddsn_sync_finished_mrp_to_outgoing_picking(fulfillment_line)

        self.assertTrue(picking, "La produccion terminada debe preparar un picking de salida.")
        self.assertEqual(fulfillment_line.picking_id, picking)
        self.assertEqual(fulfillment_line.qty_sent_stock, fulfillment_line.qty_sent_mrp)
