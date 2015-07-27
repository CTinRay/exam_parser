
# Requirement

* python 3.4.3
* beautifulsoup: html parser
* lxml: A library for pulling data out of HTML and XML files. 

Using command to install:

````
sudo pip install beautifulsoup
sudo pip install lxml
````

# 功能限制（到目前為止）
* 支援提型與別稱（使用其他的題型可能會造成程式崩潰）
 * 是非題（圈圈叉叉）
 * 選擇題（單選題）
 * 填充題（填空題）
* 多選題
 * 只能使用字母或是數字作為選項（(A), (B), (C), ... 或 (1), (2), (3), ... ）
 * 所有題目必須使用統一的選項形式，即統一使用數字或字母。
 * 若是使用數字形式，則目前最多指支援9個選項（(1)~(9)）；若是使用字母，則最多可以支援到26個選項（(A)~(Z)）
 * 不支援「編碼的」選項，像是使用(AB)作為第六個選項。這常見於電腦閱卷的考試，因為一般的答案卡只有五個選項（(A)~(E)）。
 * 目前每個選項不能超出一行
 * 在選項中，底線、斜體、粗體，等樣式可能會在轉換過程中消失
 * 這個程式可能會崩潰，如果使用了預期外的格式。

# docx格式

* 每一大題都要有標題，格式如「一、XXX」或「壹、XXX」
* 大題的標題裡必須包含題型的關鍵字（見支援題型與別稱），如「好棒棒選擇題」、「是或不是（是非題）」等都包含題型的關鍵字。
* 每一題都必須以阿拉伯數字標號。


# 使用方式

* 轉換後的json會輸出在標準輸出(stdout)
* 轉換訊息（錯誤、警告、紀錄）會輸出在標準錯誤(stderr)
* 命令列的第一個參數是要轉換的htm檔路徑
* 使用方式如下：
 * python parser.py ./path/of/the/html/file.htm > ./output.json

# 輸出的JSON格式

* 包含兩部份：exam 與 img_belongings.
 * img_belongings: 的結構大致與exam 相同，每一個題目對應到一個陣列，陣列裡包含那一題使用的圖片。
 * exam: 至少會包含一個陣列（question_parts）貯存這份試卷的每一大題。
  * question_parts: 這是一個陣列，裡面的每一個物件都代表著一大題。
   * 陣列裡的物件： 每個大題都有一些屬性：
    * title: 這一大題的標題，像是「一、多選題（每題5分）」。
    * type: 這一大題的題型。可能會是 true_false（是非題）, multi_option（選擇題）, fill_in_blank（填充題）
    * questions: 一個包含這一大題所有題目的陣列。
     * 陣列裡的物件： 如果是是非題或填充題，則每個物件就直接是題目敘述了（字串）。若是選擇題，則每個物件都包含了：
      * description: 題目的敘述
      * answers: 選項
* 可以參考文末結構圖


# Limitation ( until now )

* For multiple options question, there is only two type of option available. One is alphebatic, eg. (A), (B), (C), .... The other is numeric, eg. (1), (2), (3), ... 
* All the multiple question in one exam file should only use one unified option type ( (A), (B), (C), ... or (1), (2), (3), ...). 
* Avoid using either (1), (2), (3), ... or (A), (B), (C), ... in places other than in options. Otherwise, that may cause wrong option type analyze or wrong question/options detect.
* The program only support up to 9 ( (1) ~ (9) ) options for numeric option type, and 26 ( (A) ~ (Z) ) options for alphabetic type.
* The program does not support "encoded option type", such as using "(AB)" as the sixth option. That is common in computer scoring system, because the answer sheet only has five field ( (A) ~ (E) ) each question.
* Each option can not have more than one line.
* The underline, italic, bold style in option part of multiple choise question will disappear. ( This may be improve latter )
* The program may crash if the format of the exam is out of expectation ....

# Usage

* The first argument of the program is the path of the html file which is to be parsed.
* The program will output the parsed json file in standard output. And some information (error/log/warn) about the parsing process will output in standard error. 
* example
 * python parser.py ./path/of/the/html/file.htm > ./output.json

# Output json format.

The basic structure of the output json contains two part:
* img_belongings: Indicating the images each question contains.
* exam: The questions in the exam.

The struct of "img_belongings" correspoding to the struct of "exam".

One exam contains parts of question, so the basic structure of "exam" includes an array "question_parts".

Each entry in array "question_parts" represent one part of questions in the exam.

Each entries in "question_parts" is an array, which contains questions in the part.

Until now, there are three type of questions:
* multiple option question
* true-false question
* fill in the blank question
The structure of ture-flase question and fill in the blank question are identical. The question itself is the description of the question, and that's all.
The structure of multiple question contains two part, descriptions and answers.
The answers part is an array of options.

So the example struct of an exam json file is like that:
````
Parsed exam 
│
├─img_belongings
│        │
│        │        .... the sruct is like the exam part
│        └
│
└─exam        
        │
        ├─title: "Phycs final exam"
        └──question_parts:
                ├─┬─title: "一、單選題（占60分）"
                │ └─questions
                │        ├─┬─description: "1. 下列的現象或應用，何者的主因是波的繞射性質造成的？"
                │        │ └─answers:
                │        │        ├"(A) 琴弦振動產生駐波"        
                │        │        ├"(B) 波浪進入淺水區波速變慢"        
                │        │        ├"(C) 以X射線拍攝胸腔照片"        
                │        │        ├"(D) 以X射線觀察晶體結構 "        
                │        │        └"(E) 陰極射線實驗中螢幕的亮點位置會隨外加磁場改變"        
                │        ├─┬─description: "繩上質點P恰在x軸上，則質點P在這一瞬間的運動方向最接近下列何者？"
                │        │ └─answers:
                │        │        ├"(A) 向上"        
                │        │        ├"(B) 向下"        
                │        │        ├"(C) 向左"        
                │        │        ├"(D) 向右"        
                │        │        └"(E) 沒有確定的方向，因其速度為零"        
                │        ├─┬─description: "3. 若其基音頻率為390 Hz，則其對應的空氣柱長度約為幾公分？"
                │        │ └─answers:
                │        │        ├"(A) 44cm"        
                │        │        ├"(B) 88cm"        
                │        │        ├"(C) 100cm"        
                │        │        ├"(D) 100km "        
                │        │        └"(E) 2nm"        
                │        ├─┬─description: " ...... "
                │        │ └─answers:
                │        │        ├"(A) .... "        
                │        └        ├"(B) .... "                
                │
                │
                │                
                ├─┬─title: "二、是非題（占60分）"
                │ └─questions
                │        ├──"1.( ) 如果你是一位著作人，你所創作的書、歌曲、圖畫、攝影等，都受著作權法的保護，別人不能任意盜印、盜版、抄襲。"
                │        ├──"2.( ) 明知為電腦程式的盜版品，仍在夜市予以販賣，是侵害著作權的行為。"
                │        ├──"3.( ) 電腦程式是著作權法保護的著作。"
                │        ├──"4.( ) 原則上，著作權的侵害屬於「告訴乃論」罪，所以發生侵害時，著作權人可以自己決定到底要不要對侵權之人進行刑事告訴。"
                │        ├──"5.( ) ..."
                │        └──"..."
                │
                │
                │                
                ├─┬─title: "三、填充題"
                │ └─questions
                │        ├──"1.如果你是一位▁▁▁▁，你所創作的書、歌曲、圖畫、攝影等，都受著作權法的保護，別人不能任意盜印、盜版、抄襲。"
                │        ├──"2.明知為電腦程式的▁▁▁▁，仍在夜市予以販賣，是侵害著作權的行為。"
                │        ├──"3.▁▁▁▁是著作權法保護的著作。"
                │        ├──"4.原則上，著作權的侵害屬於「▁▁▁▁」罪，所以發生侵害時，著作權人可以自己決定到底要不要對侵權之人進行刑事告訴。"
                │        ├──"5...."
                │        └──"..."

````


