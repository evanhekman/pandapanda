from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import enum
import time
import random
import os

# declare PageType enum
class PageType(enum.Enum):
    MULTIPLE_CHOICE = 1
    CHECKBOX = 2
    TEXT = 3
    EMAIL = 4
    EMPLOYEE = 5

# survey_code = input("enter survey code (with dashes):\n")
survey_code = "2315-6862-2243-0112-0712-7402"
survey_code = survey_code.replace(" ", "")
# survey_code = survey_code.replace("-", "")
print(f"processing survey code {survey_code}")

with open("seed.txt", "r") as f:
    sentences = f.read().split("\n")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
email_address = os.environ.get("STUDENT_EMAIL")
favorite_employee = os.environ.get("FAVORITE_EMPLOYEE")

def determine_page_type() -> PageType:
    options = []
    for opt in ["Opt1", "Opt2", "Opt3", "Opt4", "Opt5"]:
        found = driver.find_elements(By.CLASS_NAME, opt)
        for f in found:
            options.append(f)
    if len(options) > 0:
        return PageType.MULTIPLE_CHOICE
    checkboxes = driver.find_elements(By.CLASS_NAME, "checkboxSimpleInput")
    if len(checkboxes) > 0:
        return PageType.CHECKBOX
    if driver.find_elements(By.TAG_NAME, "textarea"):
        return PageType.TEXT
    text_spots = driver.find_elements(By.CLASS_NAME, "textinputwrapper")
    if len(text_spots) > 1:
        return PageType.EMAIL
    if len(text_spots) > 0:
        return PageType.EMPLOYEE
    return None

def next_page() -> None: 
    nextbutton = driver.find_element("id", "NextButton")
    nextbutton.click()

def complete_multiple_choice() -> None:
    # Opt1, Opt2, Opt3, Opt4, Opt5 (or just Opt1, Opt2)
    no_option_found = True
    for row in driver.find_elements(By.CLASS_NAME, "InputRowEven"):
        options = [] 
        for opt in ["Opt1", "Opt2", "Opt3", "Opt4", "Opt5"]:
            found = row.find_elements(By.CLASS_NAME, opt)
            for f in found:
                options.append(f)
        random.choice(options).click()
        no_option_found = False
    for row in driver.find_elements(By.CLASS_NAME, "InputRowOdd"):
        options = [] 
        for opt in ["Opt1", "Opt2", "Opt3", "Opt4", "Opt5"]:
            found = row.find_elements(By.CLASS_NAME, opt)
            for f in found:
                options.append(f)
        random.choice(options).click()
        no_option_found = False
    if no_option_found:
        opt1s = driver.find_elements(By.CLASS_NAME, "radioButtonHolder")
        random.choice(opt1s).click()

def complete_text() -> None:
    # <textarea>
    textbox = driver.find_element(By.TAG_NAME, "textarea")
    feedback = ""
    for i in range(4):
        feedback += random.choice(sentences)
    textbox.send_keys(feedback)

def complete_checkbox() -> None:
    # <input type="checkbox">
    for checkbox in driver.find_elements(By.CLASS_NAME, "checkboxSimpleInput"):
        if random.random() > 0.6:
            checkbox.click()

def complete_email() -> None:
    # <input type="text">
    instr = driver.find_elements(By.CLASS_NAME, "inputtypeinstr")
    if len(instr) > 0:
        if "email" in instr[0].text.lower():
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for i in inputs:
                if i.get_attribute("type") == "text":
                    i.send_keys(email_address)

def complete_employee() -> None:
    # <input type="text">
    textarea = driver.find_elements(By.TAG_NAME, "input")
    for t in textarea:
        if t.get_attribute("type") == "text":
            t.send_keys(favorite_employee)

driver.get(f"https://www.pandaguestexperience.com/?cn={survey_code}&source=QR")
while True:
    page_type = determine_page_type()
    # print(page_type)
    if page_type == PageType.MULTIPLE_CHOICE:
        print("Multiple Choice")
        complete_multiple_choice()
    elif page_type == PageType.CHECKBOX:
        print("Checkbox")
        complete_checkbox()
    elif page_type == PageType.TEXT:
        print("Text")
        complete_text()
    elif page_type == PageType.EMAIL:
        print("Email")
        complete_email()
        input("press enter to complete survey")
    elif page_type == PageType.EMPLOYEE:
        print("Employee")
        complete_employee()
    else:
        print("Unknown page type")
        
    # input("press enter to proceed")
    next_page()
