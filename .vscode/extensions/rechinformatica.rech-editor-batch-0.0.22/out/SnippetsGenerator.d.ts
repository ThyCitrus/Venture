/**
 * Class to generate snippets
 */
export declare class SnippetsGenerator {
    /**
     * Generate all the snippets completion items and provide them
     */
    generate(): void;
    /**
     * Get the json from a json file according to the snippetsType configuration
     *
     * @returns {Object} Snippets json
     */
    private getSnippetsJson;
    /**
     * Returns the value of the snippetsType configuration
     *
     * @returns {string}
     */
    private getSnippetsType;
    /**
     *  Returns rech.batch settings group
     *
     * @returns {WorkspaceCofiguration}
     */
    private settingsGroup;
    /**
     * Convert snippet text to markdown code block
     *
     * @param snippetText Text to convert
     * @returns {MarkdownString} Markdown with the code block inside
     */
    private snippetTextToMarkdown;
}
