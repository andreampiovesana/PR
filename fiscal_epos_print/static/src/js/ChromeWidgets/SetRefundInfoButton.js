import {Component, onMounted, useState} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";
import {registry} from "@web/core/registry";
import {_t} from "@web/core/l10n/translation";
import {ControlButtons} from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import {usePos} from "@point_of_sale/app/store/pos_hook";
import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {RefundInfoPopup} from "../Popups/RefundInfoPopup";
import {patch} from "@web/core/utils/patch";
import {refundUtils} from "../utils/refundUtils";

export class SetRefundInfoButton extends Component {
    static template = "SetRefundInfoButton";
    static components = {
        AlertDialog,
    };
    static props = {};
    setup() {
        super.setup();
        this.pos = usePos();
        this.dialog = useService("dialog");
        this.state = useState({
            buttonColor: "#e2e2e2",
        });

        onMounted(() => {
            this.bind_order_events();
            this.orderline_change();
        });
    }
    is_available() {
        const order = this.pos.get_order();
        return order;
    }
    get buttonColor() {
        return refundUtils.getButtonColor(this.pos.get_order());
    }
    async onClickRefund() {
        await refundUtils.showRefundPopup(this.dialog, this.pos, () =>
            this.update_refund_info_button()
        );
    }
    update_refund_info_button() {
        // Trigger re-render by updating state
        this.state.buttonColor = this.buttonColor;
    }
    bind_order_events() {
        var order = this.pos.get_order();
        if (!order) {
            return;
        }
        if (this.old_order) {
            this.old_order.unbind(null, null, this);
        }
        // TODO: Servono?
        // this.pos.bind("change:selectedOrder", this.orderline_change, this);
        var lines = order.lines;
        // lines.unbind("add", this.orderline_change, this);
        // lines.bind("add", this.orderline_change, this);
        // lines.unbind("remove", this.orderline_change, this);
        // lines.bind("remove", this.orderline_change, this);
        // lines.unbind("change", this.orderline_change, this);
        // lines.bind("change", this.orderline_change, this);
        this.old_order = order;
    }
    orderline_change() {
        var order = this.pos.get_order();
        if (order) {
            var lines = order.lines;
            order.has_refund =
                lines.find(function (line) {
                    return line.qty < 0.0;
                }) !== undefined;
        }
        // Update button color state
        this.state.buttonColor = this.buttonColor;
    }
}

// Register the component
registry.category("components").add("SetRefundInfoButton", SetRefundInfoButton);

// Patch ControlButtons to add the refund button logic
patch(ControlButtons, {
    components: {
        ...ControlButtons.components,
        SetRefundInfoButton,
    },
});

patch(ControlButtons.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
        this.dialog = useService("dialog");
        // Ensure check_order_has_refund is called to update has_refund property
        const order = this.pos.get_order();
        if (order) {
            order.check_order_has_refund();
        }
    },
    async onClickRefund() {
        await refundUtils.showRefundPopup(this.dialog, this.pos);
    },
    refund_get_button_color() {
        return refundUtils.getButtonColor(this.pos.get_order());
    },
});
