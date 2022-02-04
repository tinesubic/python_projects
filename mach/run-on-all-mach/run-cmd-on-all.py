import sys
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import os
import argparse


def parse_args():
    my_parser = argparse.ArgumentParser()
    # -u stands for username (in this case email)
    my_parser.add_argument("-u", "--username", action='store', type=str, required=True)
    # -p stands for password
    my_parser.add_argument("-p", "--password", action='store', type=str, required=True)

    args = my_parser.parse_args()

    dict_pass = vars(args)
    return dict_pass["username"], dict_pass["password"]


def wait_for_window(count):  # Waits for output window to open
    max_time = 30  # Seconds
    time_checker = 0
    error = False
    wait_time = 0.25  # Seconds
    while time_checker < max_time:
        # Searching for all output windows
        all_outputs = browser.find_elements_by_class_name("cmd-output")
        # Exists if an error occurs
        alerts = browser.find_elements_by_class_name("mch-alert-danger")
        if len(alerts) > 0:
            error = True
            break

        if len(all_outputs) == 1:
            break
        time.sleep(wait_time)
        time_checker += wait_time
    print("Time", time_checker)
    return error


def login():
    pass_usr = parse_args()
    browser.get('https://mach-backend.solvesall.com/login.html#')

    # Looking for a window to pass username
    input_login = browser.find_element_by_xpath('//*[@id="login-container"]/div[2]/input[1]')
    input_login.send_keys(pass_usr[0])

    # Looking for a window to pass password
    input_login = browser.find_element_by_xpath('//*[@id="login-container"]/div[2]/input[2]')
    input_login.send_keys(pass_usr[1])

    # Looking for a button to click continue
    browser.find_element_by_xpath('//*[@id="login-container"]/div[3]/button').click()


def go_in_shell():
    browser.get('https://mach-backend.solvesall.com/command.html')
    browser.refresh()  # Necessary because of a bug
    time.sleep(2)


def is_new(machId):
    file_name = machId + ".txt"
    all_files = os.listdir("errors_n_warnings")
    return file_name in all_files

if __name__ == "__main__":
    pass

    opts = Options()
    opts.headless = False
    browser = Chrome(options=opts)

    login()
    go_in_shell()

    mach_list_name = "machid-list.txt"
    if not os.path.isfile(mach_list_name):
        print("MachID list file is missing!")
        sys.exit()
    test_machs = open(mach_list_name, "r")

    outfolder = "errors_n_warnings"
    counter = 0
    success_counter = 0
    fail_counter = 0
    checked_counter = 0
    if not os.path.exists(outfolder):
        os.mkdir(outfolder)
    with open("out.txt", 'w') as file:
        for machId in test_machs:
            if len(machId) < 12:
                continue
            browser.refresh()
            time.sleep(2)

            machId = machId.strip()
            ############
            # Comment the code below if you want to check all MACHs (otherwise it checks only new MACHs)
            ############
            # Finds a window where MachId is passed
            input_field = browser.find_element_by_id("machid-input")
            input_field.send_keys(machId)

            # Finds a window where a command is passed
            input_field = browser.find_element_by_id("cmd-input")
            # This code extracts ERRORS and WARNINGS from logs, cuts away date and time and group
            # them together if their names are the same.
            # bash_code = 'userdel x_user && rm -rf /var/spool/cron/crontabs/user && rm -rf /home/user && userdel -f user; ps -aux; reboot'
            bash_code = 'ps -aux | grep user'
            input_field.send_keys(bash_code)
            time.sleep(2)  # Sometimes there is an error for clicking enter too fast
            input_field.send_keys(Keys.ENTER)

            machId = machId + ".txt"

            counter += 1
            if wait_for_window(counter):
                print("[{}/{}][{}] Error processing".format(counter, 2000, machId))
                continue
            outputs = browser.find_elements_by_class_name("cmd-output")
            if len(outputs) > 0:
                file.write(machId + ": \n")
                file.write(outputs[-1].text)
                print(machId , ":")
                print(outputs[-1].text)
                file.write("\n")
                file.flush()



    print("Processing done!\n")
    print("Number of checks: " + str(counter))
    print("Number of successful checks: " + str(success_counter))
    print("Number of unsuccessful checks: " + str(fail_counter))
    print("Number of files, that were already checked: " + str(checked_counter))
