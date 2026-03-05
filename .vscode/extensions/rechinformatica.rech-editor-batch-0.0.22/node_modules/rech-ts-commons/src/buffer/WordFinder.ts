/**
 * Class used to words on the current line with the specified regular expression
 */
export class WordFinder {

     /**
      * Finds the word using the specified regular expression
      *
      * @param lineText current line text
      * @param column column where part the word is located
      * @param regex regular expression to find the cobol Word
      */
     public static findWordWithRegex(lineText: string, column: number, cobolWordRegex: RegExp) {
         var result: any;
         while ((result = cobolWordRegex.exec(lineText)) !== null) {
             const start = result.index;
             const end = start + result[0].length;
             if (start <= column && column <= end) {
                 return result[0];
             }
         }
         return "";
     }

     /**
      * Returns the next Cobol word in the current line starting from the specified column
      *
      * @param lineText current line
      * @param column initial column
      */
     public static getNextWordColumn(lineText: string, column: number, regex: RegExp): number {
         let result: any;
         while ((result = regex.exec(lineText)) !== null) {
             const start = result.index;
             if (start > column) {
                 return start;
             }
         }
         return column;
     }

 }
