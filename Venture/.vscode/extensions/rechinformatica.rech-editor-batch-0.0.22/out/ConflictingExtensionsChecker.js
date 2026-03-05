"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ConflictingExtensionsChecker = void 0;
const vscode_1 = require("vscode");
const EXTENSION_SETTINGS_GROUP = 'rech.batch';
const ALERT_CONFLICTING_EXTENSIONS = 'alertConflictingExtensions';
/**
 * Class to check for extensions which are installed and conflict with Rech Bath extension
 */
class ConflictingExtensionsChecker {
    check() {
        if (this.shouldAlert()) {
            const extensionName = `'Windows Bat Language Basics'`;
            const extensionId = 'vscode.bat';
            const vscodeBatExtension = vscode_1.extensions.getExtension(extensionId);
            if (vscodeBatExtension) {
                const yesButton = 'Yes';
                const dontAskAnymoreButton = `Don't ask anymore`;
                // eslint-disable-next-line @typescript-eslint/no-floating-promises
                vscode_1.window.showInformationMessage(`The built-in extension ${extensionName} is enabled along with Rech Batch, which may lead to misbehavior while inserting 'rem' comments in lowercase. Would you like to manually disable the built-in extension ${extensionName}?`, yesButton, 'Not now', dontAskAnymoreButton)
                    .then(selected => {
                    switch (selected) {
                        case yesButton:
                            // eslint-disable-next-line @typescript-eslint/no-floating-promises
                            vscode_1.commands.executeCommand('workbench.extensions.action.showExtensionsWithIds', [extensionId]);
                            // eslint-disable-next-line @typescript-eslint/no-floating-promises
                            vscode_1.window.showInformationMessage(`Please click on the gear icon and manually disable ${extensionName} extension.`);
                            break;
                        case dontAskAnymoreButton:
                            this.disableAlertSetting();
                            break;
                    }
                });
            }
        }
    }
    ;
    shouldAlert() {
        const shouldAlert = settingsGroup().get(ALERT_CONFLICTING_EXTENSIONS, true);
        return shouldAlert;
    }
    disableAlertSetting() {
        const newValue = false;
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        settingsGroup().update(ALERT_CONFLICTING_EXTENSIONS, newValue, vscode_1.ConfigurationTarget.Global);
    }
}
exports.ConflictingExtensionsChecker = ConflictingExtensionsChecker;
function settingsGroup() {
    return vscode_1.workspace.getConfiguration(EXTENSION_SETTINGS_GROUP);
}
//# sourceMappingURL=ConflictingExtensionsChecker.js.map