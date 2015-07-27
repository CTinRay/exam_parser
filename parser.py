from bs4 import BeautifulSoup
import re
import string
import json
import sys
import chardet
from chardet.universaldetector import UniversalDetector

def strip_all_tags( tag_str ):
    '''Make all tags in the str disappear, only text reamin'''
    pattern = re.compile( '<[^>]*>' )
    return pattern.sub( '', tag_str )


def extract_GSAP_subsection_title1( tag_list, start_index ):
    '''Skip the title of subsection level 1 in General Scholastic Ability Test.
    Ex: 第壹部分：選擇題
    '''
    return { 'parsed_str':tag_list[start_index].text,
             'next_index':start_index + 1}


def extract_GSAP_subsection_title2( tag_list, start_index):
    '''Skip the title of subsection level 2 in General Scholastic Ability Test.
    Ex: 一、單選題（占20分）
    '''
    return { 'parsed_str':tag_list[start_index].text,
             'next_index':start_index + 1}

def check_blank_line( tag_list, start_index ):
    pattern = re.compile( '^[ \xa0]*$' )    
    return pattern.match( tag_list[start_index].text )
    
def check_GSAP_subsection_title( tag_list, start_index ):
    '''Check if encounter a subsection title
       If encounter title of level 1 (Ex: 第壹部分：選擇題 ) return 1
       If encounter title of level 2 (Ex: 一、單選題（占20分）) return 2
       If not encounter title of any kind, return 0
    '''
    tag_str = tag_list[start_index]
    text = tag_str.text

    pattern1 = re.compile( '[ ]*第[壹貳參肆伍陸柒捌玖拾]部分：.*' )
    pattern2 = re.compile( '[ ]*[一二三四五六七八九十]、.*' )
    if( re.match( pattern1, text ) ):
        return 1
    else:
        if( re.match( pattern2, text ) ):
            return 2
        
        else:
            return 0

def skip_GSAP_head( tag_list, start_index ):
    '''Skip the dummy cover of General Scholastic Ability Test.
    --> go through until encounter subsection title
    '''
    parsed_str = "" 
    while check_GSAP_subsection_title( tag_list, start_index ) == 0:
        parsed_str += str( tag_list[start_index] )
        start_index += 1
    return { 'parsed_str':parsed_str, 'next_index':start_index}


def extract_exam_head( tag_list, start_index ):
    '''Extract the head of general exam.
    --> go through until encounter subsection title
    '''
    parsed_str = "" 
    while check_GSAP_subsection_title( tag_list, start_index ) == 0:
        parsed_str += str( tag_list[start_index] )
        start_index += 1
    return { 'parsed_str':parsed_str, 'next_index':start_index}



def get_multi_opt_description( tag_list, start_index, opt_type ):
    '''
    Get the question part of a mulitiple choise problem.
    Parameter opt_type specify the type of option. 
    Available type are numeric, alphebatic.
    Eg. numeric: (1) (2) (3) (4) (5)
        alphebatic: (A) (B) (C) (D) (E)
    '''
    parsed_str = ""
    next_index = start_index
    first_opt_str = { 'numeric':'(1)', 'alphebatic': '(A)' }[opt_type]
    tag = tag_list[next_index]
    while tag.text[:3] != first_opt_str:
        parsed_str += str(tag)
        start_index += 1
        tag = tag_list[start_index]    
        
    return { 'parsed_str':parsed_str, 'next_index':start_index}



def get_multi_opt_answers( tag_list, start_index, opt_type ):
    '''
    Get the answer part of a mulitiple choise problem.
    Return parsed_str -> html that contain the answer part.
    Parameter opt_type specify the type of option. 
    Available type are numeric, alphebatic.
    Eg. numeric: (1) (2) (3) (4) (5)
        alphebatic: (A) (B) (C) (D) (E)
    '''
    parsed_str = ""
    next_index = start_index
    tag = tag_list[next_index]
    expression = { 'numeric':'^[ ]*\([0-9]\).*', 'alphebatic':'^[ ]*\([A-Z]\).*' }[opt_type]
    pattern = re.compile( expression ) 

    while pattern.search( tag.text ):
        parsed_str += str(tag)
        next_index += 1
        tag = tag_list[next_index]

    return { 'parsed_str':parsed_str, 'next_index':next_index}


def split_multi_opt_answer( str_answers_part, opt_type ):
    '''
    Split the string of the answer part into a list of options 
    (eg. ['(A) blah~', '(B) blah~~', '(C) afga', ... ])
    ''' 
    #Strip all html tags except <img> tag.
    #Because this function split the string according the options (A), (B), (C) as keyword,
    #And some tags may split option. (ex. <p><span>(A</span>)</p>)
    pattern = re.compile('<[ ]*(?!img|/[ ]*img)[^>]*>')
    stripped_answer = re.sub( pattern, '', str_answers_part )

    #Prepare the keywords for splitting the string
    option_list = { 'alphebatic':
                    ['A', 'B', 'C', 'D', 'E', 'F', 'G',
                     'H', 'I', 'J', 'L', 'L', 'M', 'N',
                     'O', 'P', 'Q', 'R', 'S', 'T', 'N',
                     'V', 'W', 'X', 'Y', 'Z'],
                    'numeric':
                    ['1', '2', '3', '4', 
                     '5', '6', '7', '8', '9' ] }[opt_type]

    #Find the start position of all options
    start_pos = 0
    start_pos_list = []
    for option in option_list:
        index = stripped_answer.find( '(' + option + ')' )        
        if index != -1 :
            start_pos_list.append( index )
        else:
            break

    #Add the ending position
    start_pos_list.append( len(stripped_answer) )
                
    #Split the string based on the position list
    option_str_dict = {}
    n_pos = len( start_pos_list)
    for i in range( 0, n_pos - 1 ):
        start = start_pos_list[i]
        end = start_pos_list[i+1]
        opt = option_list[i]
        option_str_dict[i] = stripped_answer[start:end]

    return option_str_dict


def parse_multi_opt_question( tag_list, start_index, opt_type ):
    '''Return a dictionary of a multiple option question'''

    
    result = get_multi_opt_description( tag_list, start_index, opt_type )
    start_index = result['next_index']
    str_question = result['parsed_str']

    result = get_multi_opt_answers( tag_list, start_index, opt_type )
    start_index = result['next_index']
    str_answers_part = result['parsed_str']
    
    option_list = split_multi_opt_answer( str_answers_part, opt_type )

    return { 'question':
             {'description': str_question , 'answers': option_list},
             'next_index':start_index }
    

def parse_multi_opt_question_part( tag_list, start_index, opt_type ):
    '''Return list of questions of a part.'''

    n_tags = len( tag_list )
    
    questions = []
    
    # Parse questions until encounter title of any level
    while start_index < n_tags and check_GSAP_subsection_title( tag_list, start_index ) == 0 :
        if check_blank_line( tag_list, start_index ):
            start_index += 1
            continue        
        result = parse_multi_opt_question( tag_list, start_index, opt_type )
        start_index = result['next_index']
        questions.append( result['question'] )

    return {'questions':questions, 'next_index':start_index }

def parse_true_false_question_part( tag_list, start_index ):

    n_tags = len( tag_list )

    questions = []
    while start_index < n_tags and check_GSAP_subsection_title( tag_list, start_index ) == 0:
        questions.append( str( tag_list[start_index] ) )
        start_index += 1
        pattern = re.compile( '^[ ]*[0-9]*[ ]*\.' )

        while( start_index < n_tags
               and not pattern.match( tag_list[start_index].text )
               and check_GSAP_subsection_title( tag_list, start_index ) == 0 ):
        
            questions.append( str( tag_list[start_index] ) )
            start_index += 1

    return { 'questions': questions, 'next_index': start_index }

def parse_fill_in_the_blank_question_part( tag_list, start_index ):

    n_tags = len( tag_list )
    
    questions = []

    question_number_pattern = re.compile( '^[ ]*[0-9]*[ ]*\.' )
    
    while start_index < n_tags and check_GSAP_subsection_title( tag_list, start_index ) == 0:
        questions.append( str( tag_list[start_index] ) )
        start_index += 1
        while( start_index < n_tags
               and not question_number_pattern.match( tag_list[start_index].text )
               and not check_GSAP_subsection_title( tag_list, start_index ) ):
            questions.append( str( tag_list[start_index] ) )
            start_index += 1

    return { 'questions': questions, 'next_index': start_index }



def find_img_belong_to( exam ):
    '''
    For all the images in the exam, 
    find out which questions they belong to respectively
    '''
    #Each element of the array is a list (img_list),
    #which contains all the images the question have
    img_in_exam = []

    #For all part in the exam
    for part in exam['question_parts']:

        img_in_part = []

        #For all questions in the part
        for question in part['questions']:
            img_in_question = set()

            if part['type'] == 'multi_option':
                #Find all the images in the description
                img_tags = BeautifulSoup( question['description'], 'lxml' ).find_all('img')
                for img_tag in img_tags:
                    img_in_question.add( img_tag.attrs['src'] )

                #For all the options in the question
                for key, opt in question['answers'].items():

                    #Find all the images in the option
                    img_tags = BeautifulSoup( opt, 'lxml' ).find_all('img')
                    for img_tag in img_tags:
                        img_in_question.add( img_tag.attrs['src'] )
                        
            else:
                img_tags = BeautifulSoup( question, 'lxml' ).find_all('img')
                for img_tag in img_tags:
                    img_in_question.add( img_tag.attrs['src'] )

                
            img_in_part.append( list( img_in_question ) )
            
        img_in_exam.append( img_in_part )
        
    return img_in_exam

def analyze_following_question_type( tag_list, start_index ):
    '''
    Analyze the type of following questions form the title.
    ( if the title comtains specific keyword, 
    then assert that the following questions is of the type )
    '''

    # Each type has its keywords in the title.
    type_keywords = { 'true_false' : [ '是非題', '圈圈叉叉' ],
                      'fill_in_blank': [ '填充題', '填空題' ],
                      'multi_option': ['選擇題', '單選題']
                      }
    title_text = tag_list[start_index].text
    for question_type, keywords in type_keywords.items():
        for keyword in keywords:
            if title_text.find( keyword ) != -1:
                return question_type 
    return 'unknown'
    
def parse_GSAP( tag_list, opt_type ):
    '''Parse the whole contain of GSAP exam'''    
    start_index = 0
    result = skip_GSAP_head( tag_list, start_index )
    start_index = result['next_index']

    result = extract_GSAP_subsection_title1( tag_list, start_index )
    start_index = result['next_index']
    title1 = result['parsed_str']
    
    result = extract_GSAP_subsection_title2( tag_list, start_index )
    start_index = result['next_index']
    title2 = result['parsed_str']

    result = parse_multi_opt_question_part( tag_list, start_index, opt_type )
    start_index = result['next_index']
    multi_opt_questions = result['questions']


    return  { 'title': title1,
               'question_parts':
              [
                  { 'title': title2,
                    'questions': multi_opt_questions
                  }              
              ]
              }

def parse_general_exam( tag_list, opt_type ):
    '''Parse the whole contain of general exam'''    
    parsed_exam = {}

    n_tags = len(tag_list)
    
    start_index = 0
    result = extract_exam_head( tag_list, start_index )
    start_index = result['next_index']
    parsed_exam['exam_head'] = result['parsed_str']

    #For every part of question in the exam
    parsed_exam['question_parts'] = []
    while start_index < n_tags:
        question_part = {}

        question_type = analyze_following_question_type( tag_list, start_index )
        print( "LOG: detect question type:", question_type, file=sys.stderr )
        question_part['type'] = question_type
        
        result = extract_GSAP_subsection_title1( tag_list, start_index )
        start_index = result['next_index']
        question_part['title'] = result['parsed_str']
        
        # Base on the question type, call different function
        if question_type == 'multi_option':
            result = parse_multi_opt_question_part( tag_list, start_index, opt_type )
        elif question_type == 'true_false':
            result = parse_true_false_question_part( tag_list, start_index )
        elif question_type == 'fill_in_blank':
            result = parse_fill_in_the_blank_question_part( tag_list, start_index )
        else:
            print( "Error: in parse_general_exam, unknown question type: ",
                   question_type, file=sys.stderr )
            return

        start_index = result['next_index']

        question_part['questions'] = result['questions']        
        parsed_exam['question_parts'].append( question_part )
                
    return parsed_exam
    
    
def make_soup( html_bytes, encoding ):
    print( "LOG: Encoding html to Python string...", file=sys.stderr )
    raw_html = html_bytes.decode( encoding, 'ignore' )

    print( "LOG: Start parsing HTML", file=sys.stderr )
    soup = BeautifulSoup( raw_html , "lxml"  ) 

    return soup

def analyze_option_type( soup ):
    '''Analize the type of options in the exam
       ( eg. (A), (B), (C), ... or (1), (2), (3), ... ) 
       based on the frequency of the first option of each type.
       ( ex. the first one of alphebatic options is (A) )
    '''
    
    plain_text = soup.text

    opt_pattern_list = { 'alphebatic': "\n[ ]*\([ ]*A[ ]*\)",
                         'numeric': "\n[ ]*\([ ]*1[ ]*\)" }

    #Find the pattern type which has the most match
    greatest_type = ""
    greatest_match = 0
    for opt_type, opt_pattern in opt_pattern_list.items():
        pattern = re.compile(opt_pattern)
        n_match = len( pattern.findall( plain_text ) )
        if n_match > greatest_match:
            greatest_match = n_match
            greatest_type = opt_type
            
    return greatest_type


def get_html_encodeing(soup):
    encode = soup.meta.get('charset')
    if encode == None:
        encode = soup.meta.get('content-type')
        if encode == None:
            content = soup.meta.get('content')
            match = re.search('charset=(.*)', content)
            if match:
                encode = match.group(1)
            else:
                raise ValueError('unable to find encodeing')
    return encode



#Start of main function
print( "LOG: Opening file...", file=sys.stderr )
html_bytes = open( sys.argv[1], 'rb' ).read()

#set big5 as default encoding and use it
default_encoding = "big5"
encoding = default_encoding

soup = make_soup( html_bytes, encoding )

print( "LOG: Rechecking encoding according to html meta charset", file=sys.stderr )
encoding = get_html_encodeing( soup )

if encoding != default_encoding:
    print( "WARN: The encoding of the file is not default encoding(",
           default_encoding,
           ")" )
    print( "LOG: Try to decode html file with detected encode: ", encoding )
    soup = make_soup( html_bytes, encoding )


#All tags meaningful is under html -> body -> div -> { paragraphs, div, span, blah ~ }
#Therefore, the tag list contains those {paragraphs, div, span, blah~ }
tag_list = soup.html.body.div.find_all(True, recursive=False)


opt_type = analyze_option_type( soup )
print( "LOG: Analyzed option type = ", opt_type, file=sys.stderr )

#exam = parse_GSAP(tag_list, opt_type)
exam = parse_general_exam( tag_list, opt_type )
img_belongings = find_img_belong_to( exam )

output = { 'exam': exam,
           'img_belongings': img_belongings
           }

print( json.JSONEncoder().encode( output ) )
