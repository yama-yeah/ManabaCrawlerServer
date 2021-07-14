from collections import UserList, defaultdict
import configparser
from re import sub
from types import MethodType
from dataclasses import dataclass, field
import bs4
import requests as rq
from bs4 import BeautifulSoup, element
from typing import List

BASE_URL='https://manaba.fun.ac.jp/ct/'

@dataclass
class Task:
    id: int
    description: str
    title: str
    state: str
    start: str
    end: str



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
            # 科目名が含まれているとき
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

