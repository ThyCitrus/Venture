'use strict';
Object.defineProperty(exports, "__esModule", { value: true });
exports.TabStopper = void 0;
const vscode_1 = require("vscode");
/**
 * Class used to modify the Tab Stop tipically used with Batch files.
 *
 * Originally extracted from https://github.com/spgennard/vscode_cobol/blob/ae519156bf569742b4cd0e81e5ed252369c89ecd/src/tabstopper.ts
 */
class TabStopper {
    /**
     * Processes the Tab or Reverse-tab with the specified stops
     *
     * @param inserting true if needs to insert tab
     */
    processTabKey(inserting) {
        const editor = vscode_1.window.activeTextEditor;
        if (editor) {
            const doc = editor.document;
            const sel = editor.selections;
            this.executeTab(editor, doc, sel, inserting);
        }
    }
    /**
     * Return the first two tab stops according to the configuration and default values
     *
     * @return {number[]}
     */
    getTabs() {
        return [0, this.getInitialTabAlignment()];
    }
    /**
     * Executes the tab insertion or removal
     *
     * @param editor text editor
     * @param doc current document
     * @param sel selection
     * @param inserting boolean indicating whether the editor is inserting or removing a tab
     */
    executeTab(editor, doc, sel, inserting) {
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        editor.edit(edit => {
            for (var x = 0; x < sel.length; x++) {
                if (sel[x].start.line === sel[x].end.line) {
                    const position = sel[x].start;
                    if (inserting) {
                        this.singleSelectionTab(edit, position);
                    }
                    else {
                        this.singleSelectionUnTab(edit, doc, position);
                    }
                }
                else {
                    if (inserting) {
                        this.multipleSelectionTab(edit, sel[x]);
                    }
                    else {
                        this.multipleSelectionUnTab(edit, doc, sel[x]);
                    }
                }
            }
        });
    }
    /**
     * Inserts a single selection tab
     *
     * @param edit text editor
     * @param pos position to insert the tab
     */
    singleSelectionTab(edit, pos) {
        const size = this.tabSize(pos.character);
        edit.insert(pos, ' '.repeat(size));
    }
    /**
     * Get the value of the active text editor's tab size
     *
     * @return {number} Tab size
     */
    getEditorTabValue() {
        var _a;
        const codeTabSizeConfiguration = (_a = vscode_1.window.activeTextEditor) === null || _a === void 0 ? void 0 : _a.options.tabSize;
        var codeTabSize;
        if (codeTabSizeConfiguration == undefined) {
            codeTabSize = 3;
        }
        else {
            codeTabSize = Number(codeTabSizeConfiguration);
        }
        return codeTabSize;
    }
    /**
     * Removes a single selecton tab
     *
     * @param edit text editor
     * @param doc current document
     * @param pos position to insert the tab
     */
    singleSelectionUnTab(edit, doc, pos) {
        const size = this.unTabSize(pos.character);
        const range = new vscode_1.Range(pos.line, pos.character - size, pos.line, pos.character);
        const txt = doc.getText(range);
        if (txt === ' '.repeat(size)) {
            edit.delete(range);
        }
    }
    /**
     * Performs multiple tab selecton
     *
     * @param edit editor
     * @param sel selection
     */
    multipleSelectionTab(edit, sel) {
        for (let line = sel.start.line; line <= sel.end.line; line++) {
            const pos = new vscode_1.Position(line, sel.start.character);
            this.singleSelectionTab(edit, pos);
        }
    }
    /**
     * Performs ubtab with multiple selecions
     *
     * @param edit current text editor
     * @param doc text document
     * @param selection selection
     */
    multipleSelectionUnTab(edit, doc, selection) {
        for (let line = selection.start.line; line <= selection.end.line; line++) {
            var charpos = selection.start.character;
            if (charpos === 0) {
                const pttrn = /^\s*/;
                const selline = doc.getText(selection);
                if (selline !== null) {
                    const match = selline.match(pttrn);
                    if (match !== null) {
                        charpos = match[0].length;
                    }
                }
            }
            const pos = new vscode_1.Position(line, charpos);
            this.singleSelectionUnTab(edit, doc, pos);
        }
    }
    /**
     * Returns the tab size
     *
     * @param pos current position
     * @return {number}
     */
    tabSize(pos) {
        const tabs = this.getTabs();
        var tab = 0;
        for (var index = 0; index < tabs.length; index++) {
            tab = tabs[index];
            if (tab > pos) {
                return tab - pos;
            }
        }
        // outside range?
        const tabValue = this.getEditorTabValue();
        return tabValue - ((pos - tabs[tabs.length - 1]) % tabValue);
    }
    /**
     * Get the value of the initial tab alignment according to the configuration or the active editor tab value
     *
     * @return {number} Initial tab alignment
     */
    getInitialTabAlignment() {
        const tabConfigString = this.settingsGroup().get("initialTabAlignment", "4");
        if (tabConfigString == "off") {
            return this.getEditorTabValue();
        }
        return Number(tabConfigString);
    }
    /**
     * Returns the untab size
     *
     * @param pos current position
     * @return {number}
     */
    unTabSize(pos) {
        const tabs = this.getTabs();
        if (pos > tabs[tabs.length - 1]) {
            const tabSize = this.getEditorTabValue();
            if ((pos - tabs[tabs.length - 1]) % tabSize === 0) {
                return tabSize;
            }
            return (pos - tabs[tabs.length - 1]) % tabSize;
        }
        for (var index = tabs.length - 1; index > -1; index--) {
            const tab = tabs[index];
            if (tab < pos) {
                return pos - tab;
            }
        }
        return 0;
    }
    /**
     * Return the settings group of Rech Batch extension
     *
     * @return {WorkspaceConfiguration}
     */
    settingsGroup() {
        return vscode_1.workspace.getConfiguration("rech.batch");
    }
}
exports.TabStopper = TabStopper;
//# sourceMappingURL=TabStopper.js.map