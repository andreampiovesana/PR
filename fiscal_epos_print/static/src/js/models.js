import {PosOrder} from "@point_of_sale/app/models/pos_order";
import {PosOrderline} from "@point_of_sale/app/models/pos_order_line";
import {PosPayment} from "@point_of_sale/app/models/pos_payment";
import {patch} from "@web/core/utils/patch";
import {_t} from "@web/core/l10n/translation";
import {roundPrecision as round_pr} from "@web/core/utils/numbers";
import {PosStore} from "@point_of_sale/app/store/pos_store";

// TODO serve?
patch(PosStore.prototype, {
    set_refund_data(
        refund_date,
        refund_report,
        refund_doc_num,
        refund_cash_fiscal_serial,
        refund_full_refund
    ) {
        const selectedOrder = this.get_order();
        selectedOrder.refund_date = refund_date;
        selectedOrder.refund_report = refund_report;
        selectedOrder.refund_doc_num = refund_doc_num;
        selectedOrder.refund_cash_fiscal_serial = refund_cash_fiscal_serial;
        selectedOrder.refund_full_refund = refund_full_refund;
    },
});

patch(PosOrder.prototype, {
    check_order_has_refund() {
        const lines = this.lines;
        this.has_refund = lines.some((line) => line.qty < 0);
    },

    getPrinterOptions() {
        const config = this.config;
        if (!config) return {url: null};
        var protocol = config.use_https ? "https://" : "http://";
        var printer_url = protocol + config.printer_ip + "/cgi-bin/fpmate.cgi";
        return {url: printer_url};
    },
});

patch(PosOrderline.prototype, {
    set_fp_data() {
        if (this.tax_ids.length !== 1) {
            console.error(
                "Fiscal Print Error: Product must have exactly one tax",
                this.product.display_name
            );
            return;
        }
        this.tax_department = this.tax_ids[0];
        if (this.tax_department.price_include === true) {
            this.price_unit_incl = this.price_unit;
        } else {
            // This strategy was used because JavaScript's Math.round rounds to the nearest integer
            const rounding = this.currency.rounding;
            this.price_unit_incl = round_pr(
                this.price_unit * (1 + this.tax_department.amount / 100),
                rounding
            );
        }
    },
});
