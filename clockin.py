from flask import Flask, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return 'It Works!'

@app.route('/clockin', methods=['POST']) 
def ClockIn():
    grade = request.form.get('grade')
    classNum = request.form.get('class')
    studentID = request.form.get('id')
    exerciseTime = request.form.get('exerciseTime')
    print(grade,classNum,studentID,exerciseTime)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    start_url = "https://jinshuju.net/f/YuSF9m"
    driver.get(start_url)
    selector = Select(driver.find_element_by_id('entry_field_3_level_1'))  
    selector.select_by_visible_text(grade)
    selector = Select(driver.find_element_by_id('entry_field_3_level_2'))
    selector.select_by_visible_text(classNum)
    inputter = driver.find_element_by_id('entry_field_31')
    inputter.send_keys(studentID)
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
    inputter.send_keys(exerciseTime)
    button = driver.find_element_by_name('commit')
    button.click()
    driver.save_screenshot('C:\\Users\\calen\\Desktop\\5.png')
    driver.quit()
    return 'driver.get_screenshot_as_file'
if __name__ == '__main__':
    app.run()
    
    
#ClockIn()

