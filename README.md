
# Python package needed

python > 3.0
beautifulsoup: html parser
lxml: A library for pulling data out of HTML and XML files. 
chardet: detect file encoding


# Limitation ( until now )

* For multiple options question, there is only two type of option available. One is alphebatic, eg. (A), (B), (C), .... The other is numeric, eg. (1), (2), (3), ... 
* All the multiple question in one exam file should only use unified option type ( (A), (B), (C), ... or (1), (2), (3), ...). 
* Avoid using either (1), (2), (3), ... or (A), (B), (C), ... in places other than in options. Otherwise, that may cause wrong option type analyze or wrong question/options detect.
* The program only support up to 9 ( (0) ~ (9) ) options for numeric option type, and 26 ( (A) ~ (Z) ) options for alphabetic type.
* The program does not support "encoded option type", such as using "(AB)" as the sixth option. That is common in computer scoring system, because the answer sheet only has five field ( (A) ~ (E) ) each question.
* Each option can not have more than one line.
* The underline, italic, bold style in option part of multiple choise question will disappear. ( This may be improve latter )
* The program may crash if the format of the exam is out of expectation ....

# Usage

* The first argument of the program is the path of the html file which is to be parsed.
* The program will output the parsed json file in standard output. And some information (error/log/warn) about the parsing process will output in standard error. 
* example
** python parser.py ./path/of/the/html/file.htm > ./output.json

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

Parsed exam 
│
├─img_belongings
│	│
│	│	.... the sruct is like the exam part
│	└
│
└─exam	
	│
	├─title: "Phycs final exam"
	└──question_parts:
		├─┬─title: "一、單選題（占60分）"
		│ └─questions
		│	├─┬─description: "1. 下列的現象或應用，何者的主因是波的繞射性質造成的？"
		│	│ └─answers:
		│	│	├"(A) 琴弦振動產生駐波"	
		│	│	├"(B) 波浪進入淺水區波速變慢"	
		│	│	├"(C) 以X射線拍攝胸腔照片"	
		│	│	├"(D) 以X射線觀察晶體結構 "	
		│	│	└"(E) 陰極射線實驗中螢幕的亮點位置會隨外加磁場改變"	
		│	├─┬─description: "繩上質點P恰在x軸上，則質點P在這一瞬間的運動方向最接近下列何者？"
		│	│ └─answers:
		│	│	├"(A) 向上"	
		│	│	├"(B) 向下"	
		│	│	├"(C) 向左"	
		│	│	├"(D) 向右"	
		│	│	└"(E) 沒有確定的方向，因其速度為零"	
		│	├─┬─description: "3. 若其基音頻率為390 Hz，則其對應的空氣柱長度約為幾公分？"
		│	│ └─answers:
		│	│	├"(A) 44cm"	
		│	│	├"(B) 88cm"	
		│	│	├"(C) 100cm"	
		│	│	├"(D) 100km "	
		│	│	└"(E) 2nm"	
		│	├─┬─description: " ...... "
		│	│ └─answers:
		│	│	├"(A) .... "	
		│	└	├"(B) .... "		
		│
		│
		│		
		├──title: "二、是非題（占60分）"
		│	├──"1.( ) 如果你是一位著作人，你所創作的書、歌曲、圖畫、攝影等，都受著作權法的保護，別人不能任意盜印、盜版、抄襲。"
		│	├──"2.( ) 明知為電腦程式的盜版品，仍在夜市予以販賣，是侵害著作權的行為。"
		│	├──"3.( ) 電腦程式是著作權法保護的著作。"
		│	├──"4.( ) 原則上，著作權的侵害屬於「告訴乃論」罪，所以發生侵害時，著作權人可以自己決定到底要不要對侵權之人進行刑事告訴。"
		│	├──"5.( ) ..."
		│	└──"..."
		│
		│
		│		
		├──title: "三、填充題"
		│	├──"1.如果你是一位▁▁▁▁，你所創作的書、歌曲、圖畫、攝影等，都受著作權法的保護，別人不能任意盜印、盜版、抄襲。"
		│	├──"2.明知為電腦程式的▁▁▁▁，仍在夜市予以販賣，是侵害著作權的行為。"
		│	├──"3.▁▁▁▁是著作權法保護的著作。"
		│	├──"4.原則上，著作權的侵害屬於「▁▁▁▁」罪，所以發生侵害時，著作權人可以自己決定到底要不要對侵權之人進行刑事告訴。"
		│	├──"5...."
		│	└──"..."




