from flask import Flask, request
from flask_apscheduler import APScheduler
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
import yagmail
import time
import datetime

class Config(object):
    JOBS = [{
        'id': 'createschuler_job',
        'func': '__main__:timedClockIn',
        'trigger': 'interval',
        'seconds': 30
    }]
class person:
    def __init__(self):
        self.grade = ''
        self.classNum = ''
        self.studentID = ''
        self.exerciseTime = '' 
        self.email = '' 
        
app = Flask(__name__)
CORS(app)
execArr = []
app.config.from_object(Config()) 
scheduler = APScheduler()

@app.route('/')
def index():
    return 'It Works!'

@app.route('/clockin', methods=['POST'])
def regClockIn():
    global execArr
    student = person()
    student.grade = request.form.get('grade')
    student.classNum = request.form.get('class')
    student.studentID = request.form.get('id')
    student.exerciseTime = request.form.get('exerciseTime')
    student.email = request.form.get('email')
    execArr.append(student)
    print(len(execArr), " Student(s) in execArr")
    return "Registration Successful!"

@app.route('/clockin', methods=['GET'])
def getExecArr():
    studentIDs = ''
    for item in execArr:
        temp = [" ", str(item.studentID), ", "]
        studentIDs.join(temp)
    return studentIDs

def sendEmail(email, imgUrl):
    #链接邮箱服务器
    yag = yagmail.SMTP( user="3416637635@qq.com", password="BLANK", host='smtp.qq.com')
    # 邮箱正文
    contents = ['你好，Hello!',
                'The attatched picture is your clock in status today. ']
    # 发送邮件
    yag.send(email, 'Auto Clock In Status', contents, [imgUrl])
        
    
def ClockIn(student):
    print(student)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    start_url = "https://jinshuju.net/f/YuSF9m"
    driver.get(start_url)
    selector = Select(driver.find_element_by_id('entry_field_3_level_1'))  
    selector.select_by_visible_text(student.grade)
    selector = Select(driver.find_element_by_id('entry_field_3_level_2'))
    selector.select_by_visible_text(student.classNum)
    inputter = driver.find_element_by_id('entry_field_31')
    inputter.send_keys(student.studentID)
    selector = Select(driver.find_element_by_id('entry_field_20'))
    selector.select_by_visible_text("Yes")
    selector = Select(driver.find_element_by_id('entry_field_32'))
    selector.select_by_visible_text("Yes")
    selector = Select(driver.find_element_by_id('entry_field_33'))
    selector.select_by_visible_text("Yes")
    selector = Select(driver.find_element_by_id('entry_field_34'))
    selector.select_by_visible_text("Yes")
    selector = Select(driver.find_element_by_id('entry_field_35'))
    selector.select_by_visible_text("Yes")
    selector = Select(driver.find_element_by_id('entry_field_36'))
    selector.select_by_visible_text("Yes")
    inputter = driver.find_element_by_id('entry_field_37')
    inputter.send_keys(student.exerciseTime)
    button = driver.find_element_by_name('commit')
    button.click()
    path = 'C:\\Users\\calen\\Desktop\\'+ str(student.studentID) + '.png'
    driver.save_screenshot(path)
    sendEmail(str(student.email),path)
    driver.quit()
    return 

def timedClockIn():
    print('TimeNow:%s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    if(len(execArr) == 0):
        print("no items yet")
        return
    for student in execArr:
        ClockIn(student)
    print("Clocked in ", len(execArr), " student(s)")
    return
if __name__ == '__main__':
    scheduler=APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=False)

