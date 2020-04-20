from flask import Flask, request
from flask_apscheduler import APScheduler
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
import json
import yagmail
import time
import datetime

class Config(object):
    JOBS = [{
        'id': 'createschuler_job',
        'func': '__main__:timedClockIn',
        'trigger': 'interval',
        'days': 1,
        'misfire_grace_time': 10000
    }]
        
app = Flask(__name__)
CORS(app)
execArr = []
path = input("data file path: ")
app.config.from_object(Config()) 
scheduler = APScheduler()

@app.route('/')
def index():
    return 'It Works!'

@app.route('/del', methods=['POST'])
def deleteStudent():
    print(request.form.get('id'))
    global execArr
    for i in range(0,len(execArr)):
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
    if addStudent(request.form.get('grade'),request.form.get('class'),request.form.get('id'),request.form.get('exerciseTime'),request.form.get('email')):
        return "Registration Successful!"
    
@app.route('/clockin', methods=['GET'])
def getExecArr():
    return json.dumps(execArr,ensure_ascii=False)

@app.route('/mclockin', methods=['GET'])
def manualClockin():
    if timedClockIn():
        return "Manual Clockin Success"
    
def sendEmail(email, imgUrl):
    if email == "":
        return
    #链接邮箱服务器
    yag = yagmail.SMTP( user="3416637635@qq.com", password="jusjjfwirioocibf", host='smtp.qq.com')
    # 邮箱正文
    contents = ['你好，Hello!',
                'The attatched picture is your clock in status today. ']
    # 发送邮件
    yag.send(email, 'Auto Clock In Status', contents, [imgUrl])

def addStudent(grade,classNum,id,exerciseTime,email):
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
        print(str(student['studentID']) + " " + str(student['grade']) + " " + str(student['classNum']))
    print(len(execArr), " Student(s) in execArr")
    return True

def ClockIn(student):
    print(student)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    start_url = "https://jinshuju.net/f/RrnsWl"
    driver.get(start_url)
    selector = Select(driver.find_element_by_id('entry_field_3_level_1'))  
    selector.select_by_visible_text(student['grade'])
    selector = Select(driver.find_element_by_id('entry_field_3_level_2'))
    selector.select_by_visible_text(student['classNum'])
    inputter = driver.find_element_by_id('entry_field_31')
    inputter.send_keys(student['studentID'])
    selector = Select(driver.find_element_by_id('entry_field_20'))
    selector.select_by_visible_text("Yes")
    selector = Select(driver.find_element_by_id('entry_field_32'))
    selector.select_by_visible_text("Yes")
    selector = Select(driver.find_element_by_id('entry_field_33'))
    selector.select_by_visible_text("Yes")
    selector = Select(driver.find_element_by_id('entry_field_34'))
    selector.select_by_visible_text("Yes")
    inputter = driver.find_element_by_id('entry_field_37')
    inputter.send_keys(student['exerciseTime'])
    button = driver.find_element_by_name('commit')
    button.click()
    filePath = 'C:\\Users\\Administrator\\Desktop\\'+ str(student['studentID']) + '.png'
    driver.save_screenshot(filePath)
    sendEmail(str(student['email']),filePath)
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
    with open(path,"r") as f:
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
    scheduler=APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=False)

