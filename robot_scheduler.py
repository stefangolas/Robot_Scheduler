import os
import time
import sys
from pick import pick
import curses
import subprocess
from datetime import timedelta, date, datetime
import json

from google_scheduler import add_block_to_calendar, calendar_interface


this_file_dir = os.path.dirname(os.path.abspath(__file__))
containing_dirname = os.path.basename(this_file_dir)
pyhamilton_methods_dir = os.path.abspath(os.path.join(this_file_dir, '..' ))
prance_script = os.path.abspath(os.path.join(pyhamilton_methods_dir, '210210_PRANCE_w_errorrecovery\\reusable-pace\\robot_method.py'))


banner = """
  _____       _    _                 _ _ _                 _____      _              _       _           
 |  __ \     | |  | |               (_) | |               / ____|    | |            | |     | |          
 | |__) |   _| |__| | __ _ _ __ ___  _| | |_ ___  _ __   | (___   ___| |__   ___  __| |_   _| | ___ _ __ 
 |  ___/ | | |  __  |/ _` | '_ ` _ \| | | __/ _ \| '_ \   \___ \ / __| '_ \ / _ \/ _` | | | | |/ _ \ '__|
 | |   | |_| | |  | | (_| | | | | | | | | || (_) | | | |  ____) | (__| | | |  __/ (_| | |_| | |  __/ |   
 |_|    \__, |_|  |_|\__,_|_| |_| |_|_|_|\__\___/|_| |_| |_____/ \___|_| |_|\___|\__,_|\__,_|_|\___|_|   
         __/ |                                                                                           
        |___/                                                                                            
"""


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def login_existing():
    title = "What's your name?"
    with open('names.txt') as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    name = pick(lines, banner + '\n' + title, indicator='=>', default_index=0)[0]
    return name



def add_new_user():
    text = input("Enter your name: ")
    text = '\n' + text
    with open('names.txt', 'a') as file:
        file.write(text)
    return text

experiment_options = ['PRANCE', 'Turbidostat']

def experiment_selection(user):
    title = 'Welcome ' + user + ', what experiment would you like to run?'
    output = pick(experiment_options, banner + '\n' + title, indicator='=>', default_index=0)
    if output[0] == experiment_options[0]:
        print("Hi!")
        subprocess.run(['py','-3.6',prance_script,'--new'])

def write_blank_schedule():
    lookahead_dict = {(date.today() + timedelta(days=i)).strftime('%Y-%m-%d'):'' for i in range(14)}
    with open('schedule.txt', 'w', encoding ='utf8') as json_file:
        json.dump(lookahead_dict, json_file)

def read_schedule_dict():
    schedule = json.load('schedule.txt')
    return schedule

def add_block_to_schedule(user, start_date, end_date):
    if not os.path.exists('schedule.txt'):
        write_blank_schedule()
    with open('schedule.txt') as f:
        schedule_dict = json.load(f)
    block_dict = {(start_date + timedelta(days=i)).strftime('%Y-%m-%d'):user for i in range((end_date - start_date).days + 1)}
    print(block_dict)
    schedule_dict.update(block_dict)
    print(schedule_dict)
    with open('schedule.txt', 'w') as f:
        json.dump(schedule_dict, f)
    

def view_schedule(user):
    clear()
    with open('schedule.txt') as f:
        schedule_dict = json.load(f)
    print_schedule_dict = [(str(k) + ' ' + str(schedule_dict[k])) for k in schedule_dict if datetime.strptime(k, '%Y-%m-%d') >= datetime.now()]
    print('\n')
    print('14-day Schedule')
    print('\n')
    for day in print_schedule_dict:
        print(day)
    input("Press Enter to continue...")
    return user_dashboard(user)



def user_dashboard(user):
    dashboard_options = ['Run Experiment', 'Reserve Time Slot', 'View Schedule', 'Exit']
    title = 'Welcome ' + user + ', what would you like to do today?'
    output = pick(dashboard_options, banner + '\n' + title, indicator='=>', default_index=0)[0][0]
    print(output)
    print(dashboard_options[1])
    if output == dashboard_options[0]:
        return experiment_selection(user)
    if output == dashboard_options[1]:
        return reserve_dates(user)
    if output == dashboard_options[2]:
        return view_schedule(user)
    if output == dashboard_options[3]:
        sys.exit()


def login_prompt():
    output = pick(user_options, banner, indicator='=>', default_index=0)[0]
    return output

cal_int = calendar_interface()

def reserve_dates(user):
    lookahead = [(date.today() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(14)]
    
    start_date = pick(lookahead, banner + '\n' + 'Select your experiment start date', indicator='=>', default_index=0)[0][0] + ' 00:00:00'
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    
    times_list = [start_date_dt + timedelta(hours = i) for i in range(24)]
    
    start_time_dt = pick(times_list, banner + '\n' + 'Select your experiment start time', indicator='=>', default_index=0)[0][0]
    
    end_dates_str = [(start_date_dt + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0,12)]
    end_date = pick(end_dates_str, banner + '\n' + 'Select your experiment end date', indicator='=>', default_index=0)[0][0] + ' 00:00:00'
    
    end_times_list = [datetime.strptime(end_date,'%Y-%m-%d %H:%M:%S')  + timedelta(hours = i) for i in range(24)]
    
    end_time_dt = pick(end_times_list, banner + '\n' + 'Select your experiment end time', indicator='=>', default_index=0)[0][0]
    
    add_block_to_calendar(cal_int, start_time_dt, end_time_dt, 'stefanmgolas@gmail.com', '00001', 'TEST')
    return user_dashboard(user)

user_options = ['Log-in As Existing User', 'New User']

def start():
    lg = login_prompt()
    print(lg)
    if lg == user_options[0]:
        user = login_existing()[0]
    elif lg == user_options[1]:
        user = add_new_user()[0]
    user_dashboard(user)
    
if __name__ == '__main__':
    start()
