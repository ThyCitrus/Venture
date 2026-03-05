/**
 * Class used to modify the Tab Stop tipically used with Batch files.
 *
 * Originally extracted from https://github.com/spgennard/vscode_cobol/blob/ae519156bf569742b4cd0e81e5ed252369c89ecd/src/tabstopper.ts
 */
export declare class TabStopper {
    /**
     * Processes the Tab or Reverse-tab with the specified stops
     *
     * @param inserting true if needs to insert tab
     */
    processTabKey(inserting: boolean): void;
    /**
     * Return the first two tab stops according to the configuration and default values
     *
     * @return {number[]}
     */
    private getTabs;
    /**
     * Executes the tab insertion or removal
     *
     * @param editor text editor
     * @param doc current document
     * @param sel selection
     * @param inserting boolean indicating whether the editor is inserting or removing a tab
     */
    private executeTab;
    /**
     * Inserts a single selection tab
     *
     * @param edit text editor
     * @param pos position to insert the tab
     */
    private singleSelectionTab;
    /**
     * Get the value of the active text editor's tab size
     *
     * @return {number} Tab size
     */
    private getEditorTabValue;
    /**
     * Removes a single selecton tab
     *
     * @param edit text editor
     * @param doc current document
     * @param pos position to insert the tab
     */
    private singleSelectionUnTab;
    /**
     * Performs multiple tab selecton
     *
     * @param edit editor
     * @param sel selection
     */
    private multipleSelectionTab;
    /**
     * Performs ubtab with multiple selecions
     *
     * @param edit current text editor
     * @param doc text document
     * @param selection selection
     */
    private multipleSelectionUnTab;
    /**
     * Returns the tab size
     *
     * @param pos current position
     * @return {number}
     */
    private tabSize;
    /**
     * Get the value of the initial tab alignment according to the configuration or the active editor tab value
     *
     * @return {number} Initial tab alignment
     */
    private getInitialTabAlignment;
    /**
     * Returns the untab size
     *
     * @param pos current position
     * @return {number}
     */
    private unTabSize;
    /**
     * Return the settings group of Rech Batch extension
     *
     * @return {WorkspaceConfiguration}
     */
    private settingsGroup;
}
