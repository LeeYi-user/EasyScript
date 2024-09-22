# EasyScript

本程式為原創作品，僅有基礎架構參考自以下專案:

1. [堆疊式虛擬機](https://github.com/Horiwix/VM-python/blob/master/vm.py)
2. [編譯器範例](https://github.com/ccc111b/cpu2os/blob/master/02-%E8%BB%9F%E9%AB%94/02-%E7%B7%A8%E8%AD%AF%E5%99%A8/01-diy/03d-compiler4/compiler.c)
3. [物件變數](https://github.com/karpathy/micrograd/blob/master/micrograd/engine.py)

## 基本介紹

這個專案是我根據上課內容做出來的編譯器，該編譯器使用 EBNF 語法將高階語言轉換成中間碼，然後再丟進虛擬機裡執行。而在把高階語言轉換成中間碼之前，我們必須先將其轉換成 `token`，以下是用來對其進行轉換的正規表達式:

```regex
\+|\-|\*|\/|\<|\>|\=\=|\=|\,|\;|\(|\)|\{|\}|\d+\.\d+|\'.+?\'|\".+?\"|\w+
```

轉換完成後，我們還要利用 EBNF 語法將 token 轉換成中間碼，以下便是該編譯器的 EBNF 語法:

```regex
OP = '+' | '-' | '*' | '/' | '<' | '>'
NUMBER = [0-9]+ ('.' [0-9]+)?
NONE = None
BOOL = 'True' | 'False'
STRING = '\'' .* '\'' | '\"' .* '\"'
NAME = [a-zA-Z_][a-zA-Z0-9_]*
```

```regex
C = E (',' C)?
D = NAME (',' D)?
E = F (OP E)*
F = '(' E ')' | NUMBER | NONE | BOOL | STRING | 'input' '(' E ')' | NAME | NAME '(' C? ')'
```

```regex
STMT = ASSIGN | WHILE | IF | BLOCK | PRINT | FUNCTION | RETURN | CALL
ASSIGN = NAME '=' E ';'
WHILE = 'while' '(' E ')' STMT
IF = 'if' '(' E ')' STMT
BLOCK = '{' STMT* '}'
PRINT = 'print' '(' C ')' ';'
FUNCTION = 'function' NAME '(' D? ')' BLOCK
RETURN = 'return' E? ';'
CALL = NAME '(' C? ')' ';'
```

完成上述兩步驟後，在目標文件的路徑下將會出現一個以 `.vm` 結尾的檔案，該檔案包含了用來給虛擬機執行的中間碼。這個中間碼有點類似於組合語言，只需透過簡單的 `PUSH` 、 `STORE` 、 `LOAD` 指令，便能完成變數的存取操作。除此之外還能搭配 `ADD` 、 `SUB` 、 `MUL` ... 來完成基本運算，並利用 `JMP` 、 `JZ` 實作出條件迴圈，以達成一個最小化實現圖靈完備的程式語言。而為了讓其可用度更高，我還製作了 `DEF` 、 `CALL` 等函式類指令，幫忙實現封裝及遞迴。

那除了上述的指令操作外，這裡還有一個關鍵點便是變數的儲存方式。因為我用的是堆疊式虛擬機架構，所以所有的變數都會存在一個堆疊裡。而對於那些有專有名稱的變數，我則是另外開一個字典把它們記錄下來。與此同時也在每次呼叫函式時給字典新開分支，從而把區域變數隔開。

以下便是一開始的堆疊設定及變數載入的部分:
```python
def __init__(self):
    self.code = []
    self.stack = []
    self.variable = [{}]

def load(self, f):
    for i in f:
        lexeme = ["\(.+?\)", "\d+\.\d+", "\'.+?\'", "\".+?\"", "\w+"]
        i = re.findall("|".join(lexeme), i)

        for j in i:
            if len(self.code) > 0 and self.code[-1] == "PUSH":
                j = Value(j, push = True)

            self.code.append(j)

    f.close()
```

其中較值得一提的便是 `Value` 物件。為了實現出類似 `JavaScript` 的弱型別變數，我特意把所有的變數以物件形式儲存，然後再搭配 Python Class 原有的 `Operator Overloading` 功能，將相關的運算操作進行特殊判斷，讓其可以順利計算。以下便是相關的計算結果:

```
1 + "1"       // 11
1 - "1"       // 0
1 * "a"       // None
"a" < "b"     // True
1 == "1.0"    // True
1 > "0"       // True
1 > "hi"      // False
1 == "hi"     // False
1 < "hi"      // False
True / 2      // 0.5
False + 1     // 1
```

如此一來，這個編譯器就算暫時完成了。雖然功能還不是很完整，但已經具備基本的輸入輸出，並且可以根據情境達到基本要求。未來希望能再進一步擴充，從而實現真正的市場價值。

## 使用方式

以執行 `test` 資料夾下的 `fib.ez` 為例，只要在終端機中輸入以下指令即可:
```
python compiler.py test/fib.ez
```

如果想單獨執行編譯器生成出來的中間碼檔案 (fib.vm)，則輸入以下指令:
```
python vm.py test/fib.vm
```

## 授權聲明

[LICENSE](https://github.com/LeeYi-user/EasyScript/blob/main/LICENSE)
