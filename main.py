from urllib.request import Request, urlopen
import urllib.parse
import json
import re
 
 
DEBUG_MODE = False
 
 
def get_data(code):
    headers = {
        'authority': 'api.classtime.com',
        'accept': 'application/json',
        'sec-fetch-dest': 'empty',
        'accept-language': 'uk',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'content-type': 'application/json',
        'origin': 'https://www.classtime.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'referer': 'https://www.classtime.com/code/{}/'.format(code),
    }
    req = Request('https://api.classtime.com/students-api/v2/login/', data=json.dumps({'name': 'Ivan Basov', 'code': code}).encode())
    for k, v in headers.items():
        req.add_header(k, v)
    content = urlopen(req).read()
    content = json.loads(content)
    if DEBUG_MODE:
        print(content)
 
    headers['authorization'] = 'JWT '+content['token']
    req = Request('https://api.classtime.com/students-api/v2/sessions/{}/join/'.format(code), data=json.dumps({'name': 'Ivan Basov', 'code': code}).encode())
    for k, v in headers.items():
        req.add_header(k, v)
    content = urlopen(req).read()
    if DEBUG_MODE:
        print(content)
 
    req = Request('https://api.classtime.com/students-api/v2/sessions/{}/'.format(code))
    for k, v in headers.items():
        req.add_header(k, v)
    content = urlopen(req).read()
    if DEBUG_MODE:
        print(content)
    content = json.loads(content)
 
    return content
 
 
def get_text_from_category(x):
    choise_text = ''
    if isinstance(x.get('content'), dict):
        try:
            choise_text += ' '.join([x['text'] for x in x['content']['blocks']])
        except:
            print('Не могу получить ответ из: {}'.format(x))
 
        if 'entityMap' in x['content'] and x['content']['entityMap']:
            choise_text += ' '.join([v['data']['teX'] for k, v in x['content']['entityMap'].items()])
    if x.get('image'):
        choise_text += ' id: {}, ссылка: {}'.format(x['image'], 'https://res.cloudinary.com/gopollock/image/upload/{}'.format(x['image']))
    choise_text = choise_text.strip()
    return choise_text
 
 
def render_data(data):
    return_text = ''
    return_text += 'Код: {}'.format(data['code']) + '\n'
    for question in data['questions']:
        return_text += '\n{}'.format(question['title']) + '\n'
        if question['kind'] in ('categorizer', 'multiple_categorizer'):
            for item in question['items']:
                answer = 'нет ответа'
                for category in item['categories']:
                    needed_categories = [x for x in question['categories'] if x['id'] == category]
                    if not needed_categories:
                        continue
                    answer = ', '.join([get_text_from_category(x) for x in needed_categories])
                return_text += '   {} - {}'.format(get_text_from_category(item), answer) + '\n'
        elif question['kind'] in ('choice', 'multiple'):
            for choise in question['choices']:
                is_correct = choise['isCorrect']
                choise_text = get_text_from_category(choise)
               
                return_text += ' {} {}'.format('+' if is_correct else '-', choise_text) + '\n'
        elif question['kind'] == 'bool':
            return_text += ' {} {}'.format('+' if question['isTrueCorrect'] else '-', 'True') + '\n'
            return_text += ' {} {}'.format('-' if question['isTrueCorrect'] else '+', 'False') + '\n'
        elif question['kind'] == 'text':
            return_text += 'Невозможно решить этот вопрос, т.к. он требует ответа в формате своевольного текста\n'
        else:
            return_text += 'Не могу решить вопрос типа: {}'.format(question['kind']) + '\nОтправьте Ваш код сессии разработчику' +'\n'
 
    return return_text
 
 
def main():
    try:
        if not DEBUG_MODE:
            user_input = input('Введите код сессии: ').strip()
        else:
            print('DEBUG MODE!!!')
            user_input = 'NDJQ5Q'
        if not re.match('^[A-Z0-9]{6}$', user_input):
            print('Не правильный код')
            return
 
        text = render_data(get_data(user_input))
        file_path = '{}.txt'.format(user_input)
        print(text)
 
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print('Результат записан по пути: {}'.format(file_path))
 
    except Exception as e:
        raise
    input('Нажмите любую кнопку для выхода...')
 
 
if __name__ == '__main__':
    main()