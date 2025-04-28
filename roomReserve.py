from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
import time as wait_time


driver = webdriver.Chrome()


def find_full_room(time_obj, formatted_date, total_hours):
    time_format = "%I:%M%p"
    
    for room in "MABCEFGHJKL":
        full_block_available = True
        
        for i in range(total_hours * 2):  # check every 30 min slot
            block_time = (time_obj + timedelta(minutes=30*i)).strftime(time_format).lstrip('0')
            xpath = f'//a[contains(@title, "{block_time} {formatted_date} - Room 2100{room}")]'
            
            try:
                element = driver.find_element(By.XPATH, xpath)
                if "unavailable" in element.get_attribute("title").lower():
                    full_block_available = False
                    break
            except Exception:
                full_block_available = False
                break

        if full_block_available:
            return room  # return the first fully open room
    
    return None



def two_hour_block(time_obj, fname, lname, uid, email, room):

    time_format = "%I:%M%p"
    time = time_obj.strftime(time_format)
    if time[0] == '0':
        time = time[1:]
    xpath_expression = f'//a[contains(@title, "{time} {formatted_date} - Room 2100{room}")]'

    try:
        element = driver.find_element(By.XPATH, xpath_expression)
    except:
        print("error, no something there")
        return

    element_title = element.get_attribute("title")
    if "unavailable" in element_title.lower(): 
        print("error, unavailable")
        return
    else:
        flag = 1
        for i in range(hours * 2): # check if every 30 minute slot is available
            new_time_obj = time_obj + timedelta(minutes=30*i)
            new_time = new_time_obj.strftime(time_format)
            if new_time[0] == '0':
                new_time = new_time[1:]

            xpath_expression = f'//a[contains(@title, "{new_time} {formatted_date} - Room 2100{room}")]'
            try:
                element = driver.find_element(By.XPATH, xpath_expression)
            except:
                break
            if "unavailable" in element_title.lower():
                flag = 0
                break
        if flag:
            xpath_expression = f'//a[contains(@title, "{time} {formatted_date} - Room 2100{room}")]'
            try:
                element = driver.find_element(By.XPATH, xpath_expression)
            except:
                print("error, unavailable")
                return
            element.click()

            submit_button = driver.find_element(By.ID, "submit_times")
            submit_button.click()
            driver.implicitly_wait(0.5)

            continue_button = driver.find_element(By.ID, "terms_accept")
            continue_button.click()
            driver.implicitly_wait(0.5)

            #first name
            first_name_field = driver.find_element(By.ID, "fname")
            first_name_field.send_keys(fname)

            #last name
            last_name_field = driver.find_element(By.ID, "lname")
            last_name_field.send_keys(lname)

            #email
            email_field = driver.find_element(By.ID, "email")
            email_field.send_keys(email)
            #uid
            uid_field = driver.find_element(By.ID, "q16114")
            uid_field.send_keys(uid)
            
            #submit (commented out for now )
            submit_button = driver.find_element(By.ID, "btn-form-submit")
            submit_button.click()
            driver.implicitly_wait(0.5)
            
            #continue (commented out for now )
            continue_button = driver.find_element(By.XPATH, '//a[@href="https://umd.libcal.com/reserve/mckeldin/group-study"]')
            continue_button.click()
            driver.implicitly_wait(0.5)

            # reset and print success
            print("reservation at: " + time + " " + formatted_date + " success. User: " + fname + " Room " + room)
            driver.get("https://umd.libcal.com/reserve/mckeldin/group-study")
            driver.implicitly_wait(0.5)
                
def get_to_day(day):
    while True:
        try:
            # Check for the popup
            popup = WebDriverWait(driver, 0.5).until(
                EC.visibility_of_element_located((By.ID, "s-lc-window-limit-warning"))
            )

            break  # Exit the loop if the popup appears

        except TimeoutException:
            # Popup not found, check the date
            current_day_and_date_text = driver.find_element(By.CLASS_NAME, "fc-toolbar-title").text  # Replace with actual locator
            
            if day == current_day_and_date_text:

                break  # Exit the loop if the date matches

            # Otherwise, click the "Next" button
            next_day_button = driver.find_element(By.CLASS_NAME, "fc-next-button")
            next_day_button.click()


def remove_leading_zero(date_str):
    parts = date_str.split(' ')
    if parts[2].startswith('0'):
        parts[2] = parts[2][1:]
    return ' '.join(parts)
# MAIN

input_date = input("Enter a date (MM/DD/YYYY): ")
time = input("Enter a time (XX:00AM/PM  Ex: 4:00PM): ")
hours = int(input("Enter hours of Reservation (Even number): "))

date_object = datetime.strptime(input_date, "%m/%d/%Y")
formatted_date = date_object.strftime("%A, %B %d, %Y")

#Time String in 12-hour format

time_format = "%I:%M%p"
# time object to add time increments
time_obj = datetime.strptime(time, time_format)

driver.get("https://umd.libcal.com/reserve/mckeldin/group-study")
driver.implicitly_wait(0.5)

#get current day and date
day_and_date = driver.find_element(By.CLASS_NAME, "fc-toolbar-title")
day_and_date_text = day_and_date.text


formatted_date = remove_leading_zero(formatted_date)
# Find a room that works
get_to_day(formatted_date)
chosen_room = find_full_room(time_obj, formatted_date, hours)
if not chosen_room:
    print("No room available for full duration!")
    driver.quit()
    exit()
else:
    print("ROOM " + chosen_room + " AVAILABLE!!!")

with open("userdata.txt", "r") as file:
    lines = file.readlines()

for i in range(hours // 2):
    if i+1 >= len(lines):
        print("Not enough user entries!")
        break

    get_to_day(formatted_date)
    fname, lname, uid, email = lines[i+1].strip().split(",")
    two_hour_block(time_obj, fname, lname, uid, email, chosen_room)

    time_obj = time_obj + timedelta(minutes=120)
    time = time_obj.strftime(time_format)
    

driver.quit()


