from datetime import datetime, timedelta, timezone
from re import sub
from dataclasses import dataclass
import requests as rq
from bs4 import BeautifulSoup
from typing import List
import aiohttp
import asyncio
import re
import pprint
BASE_URL = 'https://manaba.fun.ac.jp/ct/'


@dataclass
class Task:
    task_id: int
    task_title: str
    task_url: str
    task_type: str
    course_id: int
    course_name: str
    state: str
    start: str
    end: str
    remain: str
    #description: str

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "task_title": self.task_title,
            "task_url": self.task_url,
            "task_type": self.task_type,
            "course_id": self.course_id,
            "course_name": self.course_name,
            "state": self.state,
            "start": self.start,
            "end": self.end,
            "remain": self.remain,
            # "description": self.description 重くなりそうだから消しておく
        }


@dataclass
class Course:
    course_id: int  # int
    course_name: str  # str
    course_url: str  # str BASE_URL+course_id

    def to_dict(self):
        return {
            "course_id": self.course_id,
            "course_name": self.course_name,
            "course_url": self.course_url
        }


Courses = List[Course]

TimeTable = {'Mon': [], 'Tue': [], 'Wed': [],
             'Thu': [], 'Fri': [], 'Sat': [], 'Other': []}
#ALL: List[Courses_DICT]


class Manaba:
    BASE_URL = 'https://manaba.fun.ac.jp/ct/'
    TASK_TYPE = ['_query', '_survey', '_report']

    def __init__(self, userid, password):
        url = BASE_URL + 'login'
        self.login_data = {
            'userid': userid,
            'password': password
        }
        self.session = rq.Session()
        self.session.get(url)
        login = self.session.post(url, data=self.login_data)
        self.bs = BeautifulSoup(login.text, 'lxml')
        #self.courses: list[element.Tag] = [course for course in self.bs.find_all('td', class_='course')if course.find('a')]
        self.success = self.check_login()
        if self.success:
            # split body to main and others
            main = self.bs.find('table', class_='stdlist')
            others = self.bs.find('table', class_='stdlist courselist')
            main_courses, other_courses = self.split_courses(main, others)
            # get courses data(course_id,course_name)
            main_data, other_data = self.get_courses_data(
                main_courses, other_courses)
            self.main_courses_id, self.main_courses_name = main_data
            self.other_courses_id, self.other_courses_name = other_data
        else:
            print('login failed')

    def check_login(self):
        # print(self.bs)
        return self.bs.find('div', class_='login-body') is None

    def access_course(self):
        # 多分実装しない
        # ニュースを引っ張ってくる
        pass

    def split_courses(self, main, others):
        return (main.find_all('td', class_='course'), others.find_all('span', class_='courselist-title'))

    def get_courses_data(self, main_courses, other_courses):
        main_name_temp = list(map(lambda x: x.find_all('a',href=re.compile('^course_')) if x.find(
            'a') else ["%void%"], main_courses))  # if course is empty, return %void%
        main_name=list(map(lambda x: list(map(lambda y:y.get_text() if type(y)!=type('')else y,x)), main_name_temp))
        #pprint.pprint(main_name)
        other_name = list(map(lambda x: x.find(
            'a').get_text().replace('\u3000', ''), other_courses))
        main_id_temp = list(map(lambda x: x.find_all('a',href=re.compile('^course_')) if x.find(
            'a') else ["%void%"], main_courses))
        main_id=list(map(lambda x: list(map(lambda y:y['href'] if type(y)!=type('') else y,x)) , main_id_temp))
        other_id = list(map(lambda x: x.find('a')['href'], other_courses))
        return ((main_id, main_name), (other_id, other_name))

    def get_courses_timetable_list(self):
        pass

    def split_main_timetable(self, main_courses):
        main_name = list(map(lambda x: x.find('a').get_text().replace('\u3000', '') if x.find(
            'a') else ["%void%"], main_courses))  # if course is empty, return %void%



    def get_tasks(self, except_id=['%void%'], least='%void%',except_type=[],except_state=[]):
        tasks = []
        self.except_type=except_type
        if(self.success):
            raw = self.run_async()
        else:
            return {'tasks': [], 'status': 'failed'}
        # get main_tasks
        i = 0
        # print(len(raw),len(raw[0]))
        for id, name in zip(sum(self.main_courses_id,[])+self.other_courses_id, sum(self.main_courses_name,[])+self.other_courses_name):
            # access each task
            if id == '%void%':
                continue
            course_id = int(id.strip('course_'))
            if course_id in except_id:
                continue
            j = 0
            for t in self.TASK_TYPE:
                if t[1:] in self.except_type:
                    continue
                task_html = BeautifulSoup(
                    raw[i][j], 'lxml',)
                if i == 0:
                    #print(BeautifulSoup(raw[-3][2], 'lxml',).find_all('tr')[1:-1][0].find_all('td',class_='center')[2:])
                    pass
                # salvage task_id,task_title,task_url,state,start,end,remain,description
                # already have datas are task_id task_name task_type course_id course_name
                # split html for tasks
                task_html = task_html.find_all(
                    'tr')[1:-1]  # erase header & footer
                task_html = list(reversed(task_html))

                if not task_html:
                    j += 1
                    continue
                # url=BASE_URL+course_id+t+'_'+task_id
                task_url_list = list(
                    map(lambda x: BASE_URL+x.find('a')['href'], task_html))
                if course_id==95955:
                    print(task_url_list)
                #print(list(filter(lambda x: x=='https://manaba.fun.ac.jp/ct/course_102052_query_102105', task_url_list)))
                task_title_list = list(
                    map(lambda x: x.find('a').get_text().replace('\u3000', ''), task_html))
                task_id_list = list(
                    map(lambda x: x.split('_')[-1], task_url_list))
                task_state_list = list(
                    map(lambda x: self.get_task_state(x), task_html))
                if t == '_query':
                    p = 1
                elif t == '_report':
                    p = 2
                else:
                    p = 1
                task_start_end_list = list(
                    map(lambda x: x.find_all('td', class_='center')[p:], task_html))
                task_start_list = [x[0].get_text() if x[0].get_text() != '' else '0000-01-01 00:00'
                                   for x in task_start_end_list ]
                task_end_list = [x[1].get_text() if x[1].get_text() != '' else '0000-01-01 00:00'
                for x in task_start_end_list]
                remain_list = list(
                    map(lambda x: self.get_remaining_time(x), task_end_list))
                for k in range(len(task_start_list)):
                    if course_id==95955:
                        print(task_state_list[k])
                    if self.check_wrap(task_end_list[k], least,task_state_list[k],except_state):
                        task = Task(int(task_id_list[k]), task_title_list[k], task_url_list[k], t[1:], course_id, name,
                                    task_state_list[k], task_start_list[k], task_end_list[k], remain_list[k])
                        tasks.append(task.to_dict())
                    else:
                        continue
                j += 1
            i += 1
        return {'tasks': tasks, 'status': 'success'}
    '''
    task_id: int
    task_title: str
    task_url: str
    task_type: str
    course_id: int
    course_name: str
    state: str
    start: str
    end: str'''

    def get_task_state(self, html):
        if html.find('span', class_='expired'):
            return '提出失敗'
        elif html.find('strong'):
            return '提出完了'
        else:
            return '受付中'

    def get_remaining_time(self, end: str) -> str:
        # タイムゾーンの生成
        JST = timezone(timedelta(hours=+9), 'JST')
        end_time = datetime.strptime(end, '%Y-%m-%d %H:%M').replace(tzinfo=JST)
        now_time = datetime.now(JST)
        residual = end_time - now_time
        return str(residual)

    def check_task_time(self, end, least):
        if(end == '%void%' or least == '%void%'):
            return True
        end_time = datetime.strptime(end, '%Y-%m-%d %H:%M')
        least = datetime.strptime(least, '%Y-%m-%d %H:%M')
        if(end_time >= least):
            return True
        else:
            return False
    
    def check_task_state(self,state,except_state):
        if(state in except_state):
            return False
        return True

    def check_wrap(self,end,least,state,except_state):
        if(self.check_task_time(end, least) and self.check_task_state(state,except_state)):
            return True
        return False

    async def get_tasks_html_async(self):
        async def a(id, ss):
            resps=[]
            if(self.TASK_TYPE[0][1:] not in self.except_type):
                async with ss.get(BASE_URL+id+self.TASK_TYPE[0]) as resp:
                    q = await resp.text()
                resps.append(q)
            if(self.TASK_TYPE[1][1:] not in self.except_type):
                async with ss.get(BASE_URL+id+self.TASK_TYPE[1]) as resp:
                    r = await resp.text()
                resps.append(r)
            if(self.TASK_TYPE[2][1:] not in self.except_type):
                async with ss.get(BASE_URL+id+self.TASK_TYPE[2]) as resp:
                    s = await resp.text()
                resps.append(s)
            return resps
        async with aiohttp.ClientSession() as session:
            ss = session
            await ss.get(BASE_URL+'login')
            await ss.post(BASE_URL+'login', data=self.login_data)
            tasks = [a(id, ss) for id in sum(self.main_courses_id,[]) +
                     self.other_courses_id if id != '%void%']
            res = await asyncio.gather(*tasks)
        return res

    def run_async(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.get_tasks_html_async())

    def get_timetable(self):
        if(not self.success):
            return {'timetable': {}, 'status': 'failed'}
        # main
        keys = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        i = 0
        for ids, names in zip(self.main_courses_id, self.main_courses_name):
            courses=[]
            if(i == 6):
                i = 0
            for id,name in zip(ids,names):
                if(id == '%void%'):
                    id = 0
                    url = '%void%'
                else:
                    url = BASE_URL+id
                    id = int(id.strip('course_'))
                course = Course(id, name, url)
                courses.append(course.to_dict())
            TimeTable[keys[i]].append(courses)
            i += 1
        # other
        for id, name in zip(self.other_courses_id, self.other_courses_name):
            if(id == '%void%'):
                id = 0
                url = '%void%'
            else:
                url = BASE_URL+id
                id = int(id.strip('course_'))
            course = Course(id, name, url)
            TimeTable['Other'].append(course.to_dict())
        return {'timetable': TimeTable, 'status': 'success'}


if __name__ == '__main__':
    pass


# print(b)
# print(t2-t1)


"""
Tasks = List[Task]


@dataclass
class Course:
    "コース"
    course_name: str
    # course_id: int
    tasks: Tasks

    def __add__(self, other):
        other: Course
        if self.course_name == other.course_name:
            self.tasks += other.tasks


Courses = List[Course]


@dataclass
class Courses(UserList):
    data: List[Course] = field(default_factory=list)

    def __add__(self, other: Courses):
        for item in other:
            item: Course
            # 科目名が含まれているときget
            if (idx := self.get_index(item.course_name)) != -1:
                self.data[idx] += item
            else:
                self.data.append(item)

    def get_index(self, course_name: str) -> int:
        course_name_list = [cn.course_name for cn in self.data]
        if course_name in course_name_list:
            return self.data.index(course_name)
        return -1


def main():
    config = configparser.ConfigParser()
    config.read('./config.ini')
    USERID = config['USER']['userid']
    PASSWORD = config['USER']['password']

    base_url = 'https://manaba.fun.ac.jp/ct/'
    url = base_url + 'login'
    login_data = {
        'userid': USERID,
        'password': PASSWORD
    }

    session = rq.session()
    session.get(url)

    login = session.post(url, data=login_data)

    couses_have_tasks = Courses()

    bs = BeautifulSoup(login.text, 'lxml')

    courses = [course for course in
               bs.find_all('td', class_='course')
               if course.find('a')]
    # print(courses[0])

    couses_have_tasks += get_tasks(session, base_url, courses, '_report')
    couses_have_tasks += get_tasks(session, base_url, courses, '_query')
    couses_have_tasks += get_tasks(session, base_url, courses, '_survey')
    # for course in couses_have_tasks:
    # print(course)
    # for task in course.tasks:
    #     print('-'*20)
    # print(task)
    print(courses)
    print("----------------")


def get_tasks(session: rq.Session, base_url: str, courses: Courses, query: str) -> Courses:
    couses_have_tasks = Courses()
    for course in courses:
        report_url: str = base_url + course.find('a').get('href') + query
        report = BeautifulSoup(session.get(report_url).text, 'lxml')
        course_name: str = report.find('a', id='coursename').get_text()
        table = report.find_all('table', class_='stdlist')
        #print(table)
        for row in table:
            row: element.Tag
            # 0 は項目、１以降が実際の課題
            reports: List[element.Tag] = row.find_all('tr')[1:]
            # print(reports)

            un_submitted_tasks:Tasks() =[] 
            for item in reports:
                title: element.Tag
                state: element.Tag
                start: element.Tag
                end: element.Tag
                description: element.Tag
                title, state, start, end = item.find_all('td')
                if is_unsubmitted(state, query):

                    id = title.find('a').get('href').split('_')[-1]
                    description = get_description(session, report_url, id)

                    t = Task(
                        id=int(id),
                        description=description,
                        title=title.find('a').get_text(),
                        state=state.find('span', class_='deadline').get_text(),
                        start=start.get_text(),
                        end=end.get_text()
                    )
                    un_submitted_tasks.append(t)

            if (c := Course(course_name=course_name, tasks=un_submitted_tasks)).tasks:
                couses_have_tasks.append(c)
    return couses_have_tasks


def is_unsubmitted(state: element.Tag, query: str) -> bool:
    "受付中かつ未提出"
    acception: str
    submission: str
    if query == '_report':
        if (div := state.find('div')) and (deadline := state.find('span', class_='deadline')):
            acception = div.get_text()
            submission = deadline.get_text()
        else:
            try:
                print(deadline.get_text())
            except:
                pass
            return False
    if query in ['_query', '_survey']:
        if (td := state.get_text()) and (deadline := state.find('span', class_='deadline')):
            # 構造が悪い
            acception, submission = td.strip().split()
        else:
            return False

    if acception == '受付中' and submission == '未提出':
        return True
    return False


def get_description(session: rq.Session, report_url: str, id: str) -> str:
    "課題のページから説明を取得"
    url = report_url + '_' + id
    page = BeautifulSoup(session.get(url).text, 'lxml')
    table: element.Tag = page.find('table')
    if not table:
        return ""
    tr: element.Tag = table.find('tr', class_='row1')
    if not tr:
        return ""
    td: element.Tag = tr.find('td', class_='left')
    return td.text


def sub_dic(couses_have_tasks):
    #convert Course to dic 
    #original data style
    '''
    Course(
        course_name='線形代数学Ⅰ 1-IJKL', 
        tasks=[Task(id=104270, description='', 
        title='演習課題５', state='未提出', 
        start='2021-05-17 18:00', 
        end='2021-05-21 00:00')]
    )'''
    #dic style
    '''
    dic{
        COURSE_NAME{
            TASK_NAME{
                {state},
                {start},
                {end}
            }
        }
    }
    '''
    dic = defaultdict(lambda: dict())
    for course in couses_have_tasks:
        for task in course.tasks:
            task_dic = {}  # task内容を記述
            task_dic['state'] = task.state
            task_dic['start'] = task.start
            task_dic['end'] = task.end
            dic[course.course_name][task.title] = task_dic
    return dic

def t4t5u0_list(couses_have_tasks):
    #convert Course to dic 
    #original data style
    '''
    Course(
        course_name='線形代数学Ⅰ 1-IJKL', 
        tasks=[Task(id=104270, description='', 
        title='演習課題５', state='未提出', 
        start='2021-05-17 18:00', 
        end='2021-05-21 00:00')]
    )'''
    #list style
    '''
    [
        {
            "course_name": "技術者倫理 3",
            "end": "2021-05-25 00:00",
            "start": "2021-05-18 13:40",
            "state": "未提出",
            "task_title": "第6回ミニエッセイ課題",
        }
    ]
    '''
    list = []
    for course in couses_have_tasks:
        for task in course.tasks:
            task_dic={}
            task_dic['state'] = task.state
            task_dic['start'] = task.start
            task_dic['end'] = task.end
            task_dic['course_name'] = course.course_name
            task_dic['task_title'] = task.title
            list.append(task_dic)
    return list

def submode(session,bs):
    couses_have_tasks = Courses()
    courses = [course for course in
               bs.find_all('td', class_='course')
               if course.find('a')]
    couses_have_tasks.data+=get_tasks(session, BASE_URL, courses, '_report').data
    couses_have_tasks.data+=get_tasks(session, BASE_URL, courses, '_query').data
    couses_have_tasks.data+=get_tasks(session, BASE_URL, courses, '_survey').data
    # print(couses_have_tasks)
    #dic = couses_have_tasks
    dic = sub_dic(couses_have_tasks)
    return dic

def timemode(bs):
    course_list= [name.find('a').get_text() if name.find('a') else "%void%" for name in bs.find_all('td', class_='course')]
    dic={
        "月":[],
        "火":[],
        "水":[],
        "木":[],
        "金":[],
        "土":[]
    }
    i=0
    keys=list(dic.keys())
    print(len(course_list))
    for course in course_list:
        if(i==6):
            i=0
        dic[keys[i]].append(course)
        i+=1
    return dic

def t4t5u0(session,bs):
    couses_have_tasks = Courses()
    courses = [course for course in
               bs.find_all('td', class_='course')
               if course.find('a')]
    couses_have_tasks.data+=get_tasks(session, BASE_URL, courses, '_report').data
    couses_have_tasks.data+=get_tasks(session, BASE_URL, courses, '_query').data
    couses_have_tasks.data+=get_tasks(session, BASE_URL, courses, '_survey').data
    # print(couses_have_tasks)
    #dic = couses_have_tasks
    return t4t5u0_list(couses_have_tasks)

def app(userid, password,mode):
    #config = configparser.ConfigParser()
    # config.read('./config.ini')
    USERID = userid
    PASSWORD = password

    url = BASE_URL + 'login'
    login_data = {
        'userid': USERID,
        'password': PASSWORD
    }

    session = rq.session()
    session.get(url)
    login = session.post(url, data=login_data)
    bs = BeautifulSoup(login.text, 'lxml')
    #######
    
    #######
    if(mode=="sub"):
        dic=submode(session,bs)
    elif(mode=="time"):
        dic=timemode(bs)
    elif(mode=="t4t5u0"):
        dic=t4t5u0(session,bs)
    return dic

"""
