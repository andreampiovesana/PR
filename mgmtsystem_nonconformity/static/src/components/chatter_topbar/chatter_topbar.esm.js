import {Chatter} from "@mail/chatter/web_portal_project/chatter";
import {patch} from "@web/core/utils/patch";

patch(Chatter.prototype, {
    async onClickShowNonConformities() {
        if (!this.state.thread.id) {
            const saved = await this.webChatterProps.saveRecord?.();
            if (!saved) {
                return;
            }
        }
        this.env.services.action.doAction(
            "mgmtsystem_nonconformity.open_mgmtsystem_nonconformity_thread_list",
            {
                additionalContext: {
                    id: this.threadId(),
                    mgmtsystem_nonconformity: this.threadModel(),
                },
            }
        );
    },
});
