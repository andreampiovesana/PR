## 20.0.1.0.0 (2026-09-19)

- \[MIG\] Migration to Odoo 20.0
- \[IMP\] Replace `security/ir.model.access.csv` with `security/ir.access.csv`
  (`ir.model.access` was replaced by `ir.access`)
- \[FIX\] `products_count`: the old `read_group` signature no longer exists, the
  count is now computed with `_read_group`
- \[FIX\] `sale.report` and `account.invoice.report` were rewritten in 20.0 as
  `subselect` queries: the brand column is added through `_select_dict` /
  `_groupby_list` and `_select_list` instead of the removed `_select_additional_fields`,
  `_group_by_sale`, `_select` and `_group_by` hooks
- \[FIX\] The brand menu now hangs under `sale.product_menu_catalog`, since
  `sale.prod_config_main` no longer exists
- \[FIX\] Kanban view: `t-esc` is a forbidden OWL directive in view arch, replaced by `t-out`
- \[FIX\] Tests: `BaseCommon` runs as a plain internal user, which may not write on
  products; the test user is granted `product.group_product_manager`
