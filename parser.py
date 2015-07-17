from bs4 import BeautifulSoup
import re
import string

def strip_all_tags( tag_str ):
    '''Make all tags in the str disappear, only text reamin'''
    pattern = re.compile( '<[^>]*>' )
    return pattern.sub( '', tag_str )


def skip_GSAP_head( tag_list, start_index ):
    '''Skip the dummy cover of General Scholastic Ability Test.'''
    return { 'parsed_str':"", 'next_index':20}


def extract_GSAP_subsection_title1( tag_list, start_index ):
    '''Skip the title of subsection level 1 in General Scholastic Ability Test.
    Ex: 第壹部分：選擇題
    '''
    return { 'parsed_str':tag_list[start_index].string,
             'next_index':start_index + 1}


def extract_GSAP_subsection_title2( tag_list, start_index):
    '''Skip the title of subsection level 2 in General Scholastic Ability Test.
    Ex: 一、單選題（占20分）
    '''
    return { 'parsed_str':tag_list[start_index].string,
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


def get_multi_opt_description( tag_list, start_index, opt_type ):
    '''
    Get the question part of a mulitiple choise problem.
    Parameter opt_type specify the type of option. 
    Available type are numeric, alphetic.
    Eg. numeric: (1) (2) (3) (4) (5)
        alphetic: (A) (B) (C) (D) (E)
    '''
    parsed_str = ""
    next_index = start_index
    first_opt_str = { 'numeric':'(1)', 'alphetic': '(A)' }[opt_type]
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
    Available type are numeric, alphetic.
    Eg. numeric: (1) (2) (3) (4) (5)
        alphetic: (A) (B) (C) (D) (E)
    '''
    parsed_str = ""
    next_index = start_index
    tag = tag_list[next_index]
    expression = { 'numeric':'^[ ]*\([0-9]\).*', 'alphetic':'^[ ]*\([A-Z]\).*' }[opt_type]
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

    #Split the string based on the position list
    option_str_dict = {}
    n_pos = len( start_pos_list)
    for i in range( 0, n_pos - 1 ):
        start = start_pos_list[i]
        end = start_pos_list[i+1]
        opt = option_list[i]
        option_str_dict[opt] = stripped_answer[start:end]

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
    questions = []
    
    # Parse questions until encounter title of any level
    while check_GSAP_subsection_title( tag_list, start_index ) == 0 :
        if check_blank_line( tag_list, start_index ):
            #debug
            print( "Blank" )
            start_index += 1
            continue
        #debug
        print( "Checking:'",tag_list[start_index].text,"'" ) 
        result = parse_multi_opt_question( tag_list, start_index, opt_type )
        start_index = result['next_index']
        questions.append( result['question'] )

    return {'questions':questions, 'next_index':start_index }
    

def parse_GSAP( tag_list ):
    '''Parse the whole contain of GSAP exam'''
    opt_type = 'numeric'
    
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

    print( multi_opt_questions )
    return  { 'title': title1,
               '0': { 'title': title2,
                 'questions': multi_opt_questions }
               }
             

#Start of main function
soup = BeautifulSoup( open( './docx_to_html/03-104學測數學定稿.htm', encoding='big5' ) , "lxml"  ) 

#All tags meaningful is under html -> body -> div -> { paragraphs, div, span, blah ~ }
#Therefore, the tag list contains those {paragraphs, div, span, blah~ }
tag_list = soup.html.body.div.find_all(True, recursive=False)

print( parse_GSAP(tag_list) )    
