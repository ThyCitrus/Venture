"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SnippetsGenerator = void 0;
const vscode_1 = require("vscode");
/**
 * Class to generate snippets
 */
class SnippetsGenerator {
    /**
     * Generate all the snippets completion items and provide them
     */
    generate() {
        vscode_1.languages.registerCompletionItemProvider({ scheme: "file", language: "bat" }, {
            provideCompletionItems: () => __awaiter(this, void 0, void 0, function* () {
                const snippets = [];
                const json = this.getSnippetsJson();
                Object.entries(json).forEach(([_key, value]) => {
                    const completionItem = new vscode_1.CompletionItem(value.prefix, vscode_1.CompletionItemKind.Snippet);
                    completionItem.documentation = this.snippetTextToMarkdown(value.body);
                    completionItem.detail = value.description;
                    completionItem.insertText = new vscode_1.SnippetString(value.body);
                    snippets.push(completionItem);
                });
                return snippets;
            })
        });
    }
    ;
    /**
     * Get the json from a json file according to the snippetsType configuration
     *
     * @returns {Object} Snippets json
     */
    getSnippetsJson() {
        var filename = "../snippets/bat.json";
        if (this.getSnippetsType() == "Community") {
            filename = "../snippets/bat-community.json";
        }
        return require(filename);
    }
    /**
     * Returns the value of the snippetsType configuration
     *
     * @returns {string}
     */
    getSnippetsType() {
        return this.settingsGroup().get("snippetsType", "Rech Internal");
    }
    /**
     *  Returns rech.batch settings group
     *
     * @returns {WorkspaceCofiguration}
     */
    settingsGroup() {
        return vscode_1.workspace.getConfiguration("rech.batch");
    }
    /**
     * Convert snippet text to markdown code block
     *
     * @param snippetText Text to convert
     * @returns {MarkdownString} Markdown with the code block inside
     */
    snippetTextToMarkdown(snippetText) {
        const markdownText = snippetText.replace(/\$[0-9]+|\${|}/g, "");
        const markdown = new vscode_1.MarkdownString();
        markdown.appendCodeblock(markdownText);
        return markdown;
    }
}
exports.SnippetsGenerator = SnippetsGenerator;
//# sourceMappingURL=SnippetsGenerator.js.map