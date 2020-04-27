from flask import Flask, request
from flask_apscheduler import APScheduler
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from openpyxl import Workbook
import pandas as pd
import json
import yagmail
import time
import datetime

class person:
    def __init__(self):
        self.classNum = ''
        self.studentID = ''
        self.isExercised = False
        self.exerciseTime = ''
        self.feedback = ''


class Config(object):
    JOBS = [{
        'id': 'createschuler_job',
        'func': '__main__:timedClockIn',
        'trigger': 'interval',
        'days': 1,
        'misfire_grace_time': 10000
    }]

grades = ['G9', 'G10', 'G11', 'G12']
gradeList = {
    'G9': [],
    'G10': [],
    'G11': [],
    'G12': []
}

app = Flask(__name__)
CORS(app)
execArr = []
path = input("data file path: ")
app.config.from_object(Config())
scheduler = APScheduler()

email = 'calen0909@hotmail.com'
username = '13681984578'
password = 'BLANK'
url = 'https://jinshuju.net/forms/xnyI52/entries'

@app.route('/')
def index():
    return 'It Works!'

@app.route('/manager', methods=['POST'])
def regManager():
    global email, username, password, url
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    url = request.form.get('url')
    return "Registration Successful!"

@app.route('/fetch', methods = ['GET'])
def manualFetch():
    timedfetchTable()
    return "manual fetching complete！"

def timedfetchTable():
    print('TimeNow:%s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    if email == '':
        print("User not registered yet!")
    else:
        fetchTable()
        return "success!"
    return "failed"


def appendRow(row):
    student = person()
    student.classNum = row[2].text.split('-')[1]
    student.studentID = row[3].text
    isExercised = True
    for j in range(4, 9):
        if row[j].text == 'NO':
            isExercised = False
        student.isExercised = isExercised
        student.exerciseTime = row[10].text
        student.feedback = row[11].text
    return student


def sendEmailExcel(excelPath):
    # 链接邮箱服务器
    yag = yagmail.SMTP(user="3416637635@qq.com",
                       password="BLANK", host='smtp.qq.com')
    # 邮箱正文
    contents = ['你好，Hello!',
                'The attatched picture is the PE status of SHSID today. ']
    # 发送邮件
    yag.send(email, 'PE Clock In Status', contents, [excelPath])
    print("Email sent successful!")


def generateData():
    formatDate = str(datetime.datetime.now(
    ).year) + str(datetime.datetime.now().month) + str(datetime.datetime.now().day)
    path = 'C:\\Users\\calen\\Desktop\\Daily PE Report ' + formatDate + '.xlsx'
    writer = pd.ExcelWriter(
        r'C:\\Users\\calen\\Desktop\\Daily PE Report ' + formatDate + '.xlsx')
    for grade in grades:
        renderGradeList = []
        for i in range(0, len(gradeList[grade])):
            student = gradeList[grade][i]
            renderRow = {'Grade': grade, "Class": student.classNum, "StudentID": student.studentID,
                         "isExercised": student.isExercised, "exerciseTime": student.exerciseTime, "feedback": student.feedback}
            renderGradeList.append(renderRow)
        # print(renderGradeList)
        df = pd.DataFrame(renderGradeList)
        print(df)
        df.to_excel(writer, sheet_name=grade)
    writer.close()
    sendEmailExcel(path)


def fetchTable():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    start_url = "https://jinshuju.net/login"
    driver.get(start_url)
    path = 'C:\\Users\\calen\\Desktop\\LoginPage.png'
    driver.save_screenshot(path)
    inputter = driver.find_element_by_id('auth_key')
    inputter.send_keys(username)
    button = driver.find_element_by_name('button')
    button.click()
    inputter = driver.find_element_by_id('password')
    inputter.send_keys(password)
    button = driver.find_element_by_name('button')
    button.click()
    formURL = url
    driver.get(formURL)
    table = driver.find_element_by_id(
        'grid_entries_grid_records').find_element_by_tag_name('table')
    table_rows = table.find_elements_by_tag_name('tr')
    checkList = []
    for row in table_rows:
        table_cols = row.find_elements_by_tag_name('td')
        for i in range(2, len(table_cols)):
            col = table_cols[i]
            grade = col.text.split('-')[0]
            if grade in grades:
                studentID = table_cols[3].text
                if studentID in checkList:
                    break
                else:
                    checkList.append(studentID)
                    isAdded = False
                    for i in range(0,len(gradeList[grade])):
                        if table_cols[2].text.split('-')[1] == gradeList[grade][i].classNum:
                            print("found!")
                            gradeList[grade].insert(i,appendRow(table_cols))
                            isAdded = True
                            break
                    if isAdded == False:
                        gradeList[grade].append(appendRow(table_cols))
                    break
    #path = 'C:\\Users\\calen\\Desktop\\LoginResult.png'
    # driver.save_screenshot(path)
    driver.quit()
    generateData()
    return "fetch success!"

@app.route('/del', methods=['POST'])
def deleteStudent():
    print(request.form.get('id'))
    global execArr
    for i in range(0, len(execArr)):
        if str(request.form.get('id')) == execArr[i]['studentID']:
            print("found")
            del execArr[i]
            print("deleted")
            print(execArr)
            return "Delete Successful!"
    print("Nothing found", request.form.get('id'))
    return

@app.route('/clockin', methods=['POST'])
def regClockIn():
    if addStudent(request.form.get('grade'), request.form.get('class'), request.form.get('id'), request.form.get('exerciseTime'), request.form.get('email')):
        return "Registration Successful!"

@app.route('/clockin', methods=['GET'])
def getExecArr():
    return json.dumps(execArr, ensure_ascii=False)

@app.route('/mclockin', methods=['GET'])
def manualClockin():
    if timedClockIn():
        timedfetchTable()
        return "Manual Clockin Success"

def sendEmail(email, imgUrl):
    if email == "":
        return
    # 链接邮箱服务器
    yag = yagmail.SMTP(user="3416637635@qq.com",
                       password="jusjjfwirioocibf", host='smtp.qq.com')
    # 邮箱正文
    contents = ['你好，Hello!',
                'The attatched picture is your clock in status today. ']
    # 发送邮件
    yag.send(email, 'Auto Clock In Status', contents, [imgUrl])

def addStudent(grade, classNum, id, exerciseTime, email):
    global execArr
    student = {
        "grade": grade,
        "classNum": classNum,
        "studentID": id,
        "exerciseTime": exerciseTime,
        "email": email
    }
    execArr.append(student)
    saveData()
    for student in execArr:
        print(str(student['studentID']) + " " +
              str(student['grade']) + " " + str(student['classNum']))
    print(len(execArr), " Student(s) in execArr")
    return True

def ClockIn(student):
    print(student)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    start_url = "https://jinshuju.net/f/xnyI52"
    driver.get(start_url)
    selects = driver.find_elements_by_css_selector("div.pretty-select")
    selects[0].click()
    driver.find_element_by_id("react-select-2-option-0").click()
    selects[1].click()
    grades  = driver.find_elements_by_css_selector("div.pretty-select__option")
    for grade in grades:
        if grade.text == student['classNum']:
            optionID = grade.get_attribute('id')
    driver.find_element_by_id(optionID).click()
    driver.find_element_by_css_selector("input.ant-input").send_keys(student['studentID'])
    for i in range(2,len(selects)):
        selects[i].click()
        driver.find_element_by_css_selector("div.pretty-select__option").click()
    driver.find_element_by_css_selector("textarea.ant-input").send_keys(student['exerciseTime'])
    driver.find_element_by_css_selector("button.ant-btn").click()
    filePath = 'C:\\Users\\calen\\Desktop\\' + \
    str(student['studentID']) + '.png'
    time.sleep(2)
    driver.save_screenshot(filePath)
    sendEmail(str(student['email']), filePath)
    driver.quit()
    return

def timedClockIn():
    print('TimeNow:%s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    if(len(execArr) == 0):
        print("no items yet")
        return False
    for student in execArr:
        ClockIn(student)
    print("Clocked in ", len(execArr), " student(s)")
    return True

def fetchData():
    global execArr
    with open(path, "r") as f:
        f.seek(0)
        text = f.read()
        if text != '':
            execArr = json.loads(text)
            print(execArr)
        else:
            print("Emtpy file")
        return

def saveData():
    f = open(path, 'w')
    f.write(json.dumps(execArr))
    f.close()

if __name__ == '__main__':
    fetchData()
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=False)
