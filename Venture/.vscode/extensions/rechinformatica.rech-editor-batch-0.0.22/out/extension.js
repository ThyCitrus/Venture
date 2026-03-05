'use strict';
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
exports.deactivate = exports.activate = void 0;
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode_1 = require("vscode");
const client_1 = require("./lsp/client");
const TabStopper_1 = require("./bat/TabStopper");
const ConflictingExtensionsChecker_1 = require("./ConflictingExtensionsChecker");
const SnippetsGenerator_1 = require("./SnippetsGenerator");
// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
function activate(_context) {
    new ConflictingExtensionsChecker_1.ConflictingExtensionsChecker().check();
    new SnippetsGenerator_1.SnippetsGenerator().generate();
    const context = _context;
    client_1.Client.startServerAndEstablishCommunication(context);
    //
    // The command has been defined in the package.json file
    // Now provide the implementation of the command with  registerCommand
    // The commandId parameter must match the command field in package.json
    //
    context.subscriptions.push(vscode_1.commands.registerCommand('rech.editor.batch.batchInsertCommentLine', () => __awaiter(this, void 0, void 0, function* () {
        yield vscode_1.commands.executeCommand('editor.action.insertLineBefore');
        yield vscode_1.commands.executeCommand('editor.action.trimTrailingWhitespace');
        yield vscode_1.commands.executeCommand('editor.action.commentLine');
    })));
    context.subscriptions.push(vscode_1.commands.registerCommand('rech.editor.batch.tab', () => {
        new TabStopper_1.TabStopper().processTabKey(true);
    }));
    context.subscriptions.push(vscode_1.commands.registerCommand('rech.editor.batch.revtab', () => {
        new TabStopper_1.TabStopper().processTabKey(false);
    }));
}
exports.activate = activate;
// this method is called when your extension is deactivated
function deactivate() {
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map