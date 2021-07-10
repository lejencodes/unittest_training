"""
This module has the purpose of assist in the most diverse operations, such as validations, prearing
the OS for bot execution, and so on.
"""

import getpass
import json
import os
import sys
from sys import platform

# if platform in ["linux", "linux2"]:
#     # linux
#     print('Linux')
# elif platform == "darwin":
#     # OS X
#     print('OS X')
# elif platform == "win32":
if platform=="win32":
    # Windows...
    # print('Win')
    import pywinauto
    import win32clipboard
    import pytesseract
    from pdf2image import convert_from_path
    import pygetwindow as gw
    import winreg

import array
import calendar
import getpass
import pathlib
import re
import shutil
import smtplib
import subprocess
import tempfile
import threading
import time
from datetime import date as datetime_date
from datetime import datetime, timedelta
from distutils.dir_util import copy_tree
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import holidays
import psutil
from PIL import Image
from tika import parser

# from gfa import BusinessException


# pylint: disable=too-many-locals,too-many-arguments,broad-except
# global variable that'll be available for email css styling

EMAIL_CSS = """
    <style>
        body{
            color: #000066;
            font-family:"Calibri";
            font-size: 15px;
        }
        table {
            color: #00004d;
            font-family: "Calibri", sans-serif;
            font-size: 15px;
            border-collapse: collapse;
            width: 100%;
        }
        td,th {
            border: 1px solid #999999;
            text-align: left;
            padding: 3px;
        }
        img{
            width:100%;
            max-width:800px;
        }
    </style>
"""


def system_exception(exception, file_name):

    """
    Performs a pretty print of the System Exception generated, specifying the line, file and
    thread number where the exception was raised

    Parameters:

        exception (Exception): Exception that was raised
        file_name (str): Name of the file who called the method

    Returns:

        str: "SYSTEM EXCEPTION"
    """

    thread = threading.current_thread().name
    line = sys.exc_info()[-1].tb_lineno
    message = 'Error on line {} of {} inside thread: {}\n'
    print(message.format(line, file_name, thread), type(exception).__name__, exception)
    return 'SYSTEM EXCEPTION'


def set_internet_user_authentication(default=True, print_output=False):

    """
    Set the Internet Settings Zones in order to make the Windows prompt for user/pwd or not.
    The default will be True, meaning that once this function is called, it will asked for the
    bot's credentials

    Parameters:

        default (bool): Flag to define reg value, case True, the credentials will be asked,
                        otherwise, it will use the Windows credentials.
        print_output (bool): Flag to define if output is to be printed in the terminal or not

    """

    value = 0
    if default:
        value = 65536

    for i in range(1, 5):
        path = r'Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\' + str(i)
        reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(reg, "1A00", None, winreg.REG_DWORD, value)
        output = winreg.QueryValueEx(reg, "DisplayName"), "SET TO", winreg.QueryValueEx(reg, "1A00")
        if print_output:
            print(output)


def kill_all_apps(download_folder):

    """
    Kill all Chrome, IExplorer, Excel, EBS Oracle Forms executables and also clean trash files
    from last executions. (e.g. Selenium remainings)
    Function also deletes all *.crdownload files within the download_folder param

    Parameters:

        download_folder (str): Main Download folder

    Returns:

        bool: False case the login has failed, otherwise it will return True
    """

    try:

        # delete all crdownloads
        for item in os.listdir(download_folder):
            if item.endswith(".crdownload"):
                os.remove(os.path.join(download_folder, item))

        # kill all opened apps
        apps_to_be_killed = ['chrome.exe', 'iexplore.exe', 'excel.exe', 'jp2launcher.exe']
        for i in [
            i
            for i in psutil.process_iter()
            if (str.lower(i.name()) in apps_to_be_killed and str.lower(getpass.getuser()) in str.lower(i.username()))
        ]:
            try:
                os.kill(i.ppid(), 0)
            except Exception:
                pass

        # join all files from current temp folder and parent temp folder
        parent_folder = os.listdir(os.path.abspath(os.path.join(tempfile.gettempdir(), '..')))
        temp_lst = parent_folder + os.listdir(tempfile.gettempdir())

        # clean selenium trash from current temp folder
        for folder in temp_lst:
            if folder.startswith('scoped_dir'):
                try:
                    # verify if current or parent
                    temp_folder = tempfile.gettempdir()
                    if folder in parent_folder:
                        temp_folder = os.path.join(tempfile.gettempdir(), '..')

                    # remove folder tree
                    shutil.rmtree(os.path.join(temp_folder, folder))
                except Exception:
                    pass

        return 'True'

    except Exception as exception:
        return system_exception(exception, os.path.basename(__file__))


def is_process_alive(process_name):

    """
    Check if the process is running/file is open

    Parameters:

        process_name (str):
            Name of the process we want to check (ex: 'jp2launcher.exe')

    Returns:

        str:
            PPID of current process
        False:
            In case the process is not running
    """

    lst_process = []

    for i in psutil.process_iter():

        try:

            process = [i.ppid(), i.name()]
            if str.lower(getpass.getuser()) in str.lower(i.username()) and process not in lst_process:
                lst_process.append(process)
        except:
            pass

    return [i[0] for i in lst_process if process_name in i[1]]


def is_window_active(window_name):

    """
    Check if a window is active and maximized on screen.
    It's not necessary to input the full name of the window, but this may return a wrong
    answer, because 2 windows could have similar names.

    Parameters:

        window_name (str):
            Name of the window we want to check (ex: 'Oracle Applications')

    Returns:

        True:
            In case the window is currently active
        False:
            In case the window is not currently active
    """

    try:
        window = gw.getWindowsWithTitle(window_name)[0]
        if window_name in gw.getActiveWindow().title and window.isMaximized:
            return True
    # This exception may occur in the transition between current and previous active window
    except AttributeError:
        is_window_active(window_name)
    except IndexError:
        raise Exception('WINDOW NOT OPEN')

    return False


def activate_window(window_name):

    """

    This function will activate and maximize a window based on its name.
    Maximizing the windows is a workaround for a problem where despite being active,
    the window won't show on the screen.

    Parameters:

    window_name (str):
        Name of the window we want to check (ex: 'Oracle Applications')

    Returns:

    True:
        In case the window is currently active
    False:
        In case the window is not currently active

    """

    for _ in range(30):
        try:
            window = gw.getWindowsWithTitle(window_name)[0]
            window.activate()
            window.maximize()
            return
        except Exception as exception:
            system_exception(exception, os.path.basename(__file__))
            pywinauto.application.Application().connect(handle=window._hWnd).top_window().set_focus()
            print('Try again...')
            pass
        time.sleep(1)


def minimize_window(window_name):

    """

    This function will minimize a window based on its name.

    Parameters:

    window_name (str):
        Name of the window we want to check (ex: 'Oracle Applications')

    Returns:

    True:
        In case the window is currently active
    False:
        In case the window is not currently active

    """
    try:
        window = gw.getWindowsWithTitle(window_name)[0]
    except IndexError:
        raise Exception('WINDOW NOT OPEN')

    window.minimize()


def wait_for_window(window_name, timeout=60):

    for _ in range(timeout):
        try:
            window = gw.getWindowsWithTitle(window_name)[0]
            return
        except IndexError:
            pass
        time.sleep(1)
    raise BusinessException('WAIT FOR WINDOW TIMEOUT')


def window_numbers(transactions, n_max=6):

    """
    Based on the amount of transactions it needs to perform, the function will return the
    best number of window that the process should support. The maximum is 6 by default.

    Parameters:

        transactions (list or int): List containing transactions or the amount of it
        n_max (int): Number max of window the function will return (optional)

    Returns:

        str: "SYSTEM EXCEPTION"
    """

    n_trans = len(transactions) - 1 if isinstance(transactions, list) else transactions
    return min([1, 2, 3, 4, 6, 8, 9], key=lambda x: abs(x - n_trans)) if n_trans < n_max else n_max


def get_working_days_by_month(country, month, state=None, year=datetime.now().year):

    """
    Retrieve a list containing all working days of desired month
    For more details: https://pypi.org/project/holidays/

    Parameters:

        country (str): Country from which holidays will be gathered (e.g. BR, UK)
        month (int): Desired month, it should be a integer (i.e. for April it should be 4)
        state (str): Country state if applied (e.g. SP for Brazil)
        year (int): Desired year to search

    Returns:

        list: list containing all days in the form of datetime
    """
    # get all holidays
    holidays_year = holidays.CountryHoliday(country, year, state=state)

    # get how much days we have today
    days_len = calendar.monthrange(year, month)[1] + 1

    # get all days of current month
    current_month = [datetime_date(year, month, i) for i in range(1, days_len)]

    # return list containing all working days of current month
    return [i for i in current_month if i not in holidays_year and i.weekday() < 5]


def get_last_working_day(country, today=datetime_date.today()):

    """
    This function get the last working day considering start of the month and january

    Parameters:

        today (date)

    Returns:

        last_working_day (date)
    """

    working_days = get_working_days_by_month(country, today.month)
    last_working_day = None
    for index, day in enumerate(working_days):
        if day == today:
            if index == 0:
                if today.month == 1:
                    last_month = 12
                    search_year = datetime.today() - timedelta(days=365)
                    search_year = search_year.year
                else:
                    last_month = today.month - 1
                    search_year = datetime.today().year
                last_working_day = get_working_days_by_month(country, last_month, year=search_year)[-1]
                break
            else:
                last_working_day = working_days[index - 1]
                break

    return last_working_day


def is_file_older_than_x_days(file_path, days=1):

    """
    Verify if file is older than x days

    Parameters:

        file_path (str): Path containing the file or folder

    Returns:

        bool: True if it is older, False otherwise
    """

    file_time = os.path.getmtime(file_path)

    # Check against 24 hours
    return (time.time() - file_time) / 3600 > 24 * days


def backup(target_path, dest_path='', delete_original=True, delete_after_x_days=90):

    """
    Performs the backup of a file or folder, saving it in a folder (dest_path) with
    the same name case defined, or in the same folder it is located.

    The backup will have the same name appending the current date by the end of the file.
    This method will also delete any backup older than 90 by default. This value can be
    changed on the parameter delete_after_x_days.

    Parameters:

        target_path (str): Path containing the file or folder which will be backed up
        dest_path (str): path where the file will be backed up (optional)
        delete_after_x_days (int): maximum age (days) for files inside backup folder (optional)
        delete_original (bool): flag to define if original file should be deleted after backup
                             by default it will be True (optional)

    Returns:

        bool: True if backup is performed, otherwise False
    """

    try:

        # check if target_path exists
        if not os.path.exists(target_path):
            print('No ' + target_path + ' to be backuped..')
            return False

        # string date for backup, always unique
        date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        target = target_path.split(os.path.sep)[-1]

        # check if target_path is a directory
        if os.path.isdir(target_path):

            # define backup folder
            backup_folder = os.path.join(dest_path, target + '_BACKUPS', '%s_%s' % (target, date))

            # create directory if empty
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)

            # perform backup of whole directory
            print('Backing up the folder: ' + target_path)
            copy_tree(target_path, backup_folder)

            # remove folder if desired
            if delete_original:
                shutil.rmtree(target_path)

        # check if target_path is a file
        elif os.path.isfile(target_path):

            # define backup folder
            backup_folder = os.path.join(dest_path, re.sub(r'.*\\|\..*$', '', target))

            # create directory if empty
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)

            # perform backup of fiile
            print('Backing up the file: ' + target)
            backup_file = re.sub(r'\.', '_' + date + '.', target)
            shutil.copyfile(target_path, os.path.join(backup_folder, backup_file))

            # remove file if desired
            if delete_original:
                os.remove(target_path)

        # delete everything older than x days
        # pylint: disable=expression-not-assigned
        for i in os.listdir(backup_folder):
            old_backup = os.path.join(backup_folder, i)
            if is_file_older_than_x_days(old_backup, delete_after_x_days):
                os.remove(old_backup) if os.path.isfile(old_backup) else shutil.rmtree(old_backup)

        return True

    except Exception as exception:
        return system_exception(exception, os.path.basename(__file__))


def wait_download(f_path=None, timeout=300):

    """
    Wait for the abscence of *.crdownload type files inside the download_path within a
    limited time window (300 seconds by default, setted by the timeout parameter)
    If the usage of X Engine is not being made, the download_path is a mandatory parameter.

    Parameters:

        f_path (str): Full path where the file should be once the download is finished
        timeout (str): folder_path where the file is located (mandatory case the X Engine
                            is not being used)

    Returns:

        bool: True if backup is performed, otherwise False
    """

    # wait for download
    for _ in range(timeout):

        # check if file exists
        if os.path.exists(f_path):
            break

        time.sleep(1)

    else:
        raise BusinessException('DOWNLOAD TIMEOUT')

    return True


def download_from_url(url, file_name):

    """
    Download a file directly from URL without screen interation.

    Parameters:

        url (str): Url where the file is located
        file_name (str): name that will be put upon the file

    Returns:

        bool: True if download succeeds, otherwise False
    """

    # vbs script that downloads a file directly from its URL
    vbs_code = """
        dim xHttp: Set xHttp = createobject("Microsoft.XMLHTTP")
        dim bStrm: Set bStrm = createobject("Adodb.Stream")
        xHttp.Open "GET", WScript.Arguments.Item(0), False
        xHttp.Send

        with bStrm
            .type = 1 '//binary
            .open
            .write xHttp.responseBody
            .savetofile WScript.Arguments.Item(1), 2 '//overwrite
        end with
    """

    # create temp file with vbs code
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.vbs')
    temp_file.write(bytes(vbs_code, encoding='utf-8'))
    temp_file.close()

    # run the vbs script and remove the temp file
    subprocess.call('cscript %s %s %s' % (temp_file.name, url, file_name))
    os.remove(temp_file.name)

    return os.path.exists(file_name)


def download_file(driver, url, file_name):

    """
    Download a file inside the webdriver with given name by using XML HTTP request
    It is very useful in order to skip the 'usual' download path

    Parameters:

        driver (webdriver): WebDriver where the download should be performed
        url (str): Url of the file to be downloaded
        file_name (str): name that will be put upon the file

    Returns:

        bool: True if download succeeds, otherwise False
    """

    # pylint: disable=anomalous-backslash-in-string
    data = driver.execute_script(
        '''
        var byteArray = [];
        var req = new XMLHttpRequest();
        req.open( "GET", "'''
        + url
        + '''", false );
        req.overrideMimeType('text\/plain; charset=x-user-defined');
        req.send(null);   
        for (var i = 0; i < req.responseText.length; ++i) {
            byteArray.push(req.responseText.charCodeAt(i) & 0xff)
        }
        return byteArray;
    '''
    )

    data = array.array('B', data).tobytes()
    with open(file_name, 'wb') as file:
        file.write(data)

    return os.path.exists(file_name)


def send_email(html, subject, sender, destination, bcc="", files=None, save_msg=None, server=None):

    """
    Send an html customized email to the desired email address.
    It is possible to save a copy of the sent message using the save_msg parameter.

    Parameters:

        html (str): HTML that will be used for the email's body
        subject (str): Email's Subject
        sender (str): Email address of the sender
        destination (str or list<str>): Email address or list of that will receive the email
        bcc (str or list<str>): Email (or list) who will receive the email in bcc (optional)
        files (str or list<str>): List of files that will be attached in the email (optional)
        save_msg (str): File name that will be given to a copy of the email (optional)
        server (smtplib.SMTP): Server SMTP that will be use to send the emails (optional)
    """

    try:

        # opening SMTP server case needed
        default = server
        if not default:
            server = smtplib.SMTP('smtpout.uk.experian.local', 25)

        # create msg
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ", ".join(destination) if isinstance(destination, list) else destination
        bcc = ", ".join(bcc) if isinstance(bcc, list) else bcc
        bcc = ", " + bcc if bcc != "" else bcc

        # add the recipients
        recipients = msg['To'] + bcc
        recipients = recipients.split(', ')
        msg.attach(MIMEText(html, 'html'))

        # add attachments case needed
        if files:
            for i in files:
                part = MIMEApplication(open(i, "rb").read(), Name=os.path.basename(i))
                part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(i)
                msg.attach(part)

        # save a copy of the message case needed
        if save_msg:
            open(save_msg, 'wb').write(bytes(msg))
            print('Email saved as ' + save_msg + '.')

        # send email and close server
        server.sendmail(msg['From'], recipients, msg.as_string())
        print('Email to ' + str(destination) + ' was sent.')

        if not default:
            server.quit()

    except Exception as exception:
        system_exception(exception, os.path.basename(__file__))


def send_communication_email(communication, bot_name, subject, sender, destination, bcc=""):

    """
    Send an html customized email to the desired email address with desired communication.

    Parameters:

        communication (str): Plain string containing the desired communication
        bot_name (str): Robot's friendly name
        subject (str): Email's Subject
        sender (str): Email address of the sender
        destination (str or list<str>): Email address or list of that will receive the email
        bcc (str or list<str>): Email (or list) who will receive the email in bcc (optional)
    """

    try:

        # prepare email html
        html = """
        <!DOCTYPE html>
        <html>
            <head>
                EMAIL_CSS
            </head>
            <body>
                </br>@communication
                <br></br><b>Robot @bot_name</b> - Global Finance Automation<br>
            </body>
        </html>""".replace(
            'EMAIL_CSS', EMAIL_CSS
        )

        # set communication and bot name
        html = html.replace('@communication', communication).replace('@bot_name', bot_name)

        # send email
        send_email(html, subject, sender, destination, bcc)

    except Exception as exception:
        system_exception(exception, os.path.basename(__file__))


def first_working_day_month(month, country='BR', state='SP'):

    # pylint: disable=eval-used

    """
    Return the first working day of the month

    Parameters:

        month (str): Month which will be retrieve the first working day
        country (str): Month which will be retrieve the first working day
        state (str): Month which will be retrieve the first working day

    Returns:

        str: date in format '%m/%d/%Y'
    """

    # get holidays list based on desired region
    year = str(datetime.now().year)
    state_holidays = eval('holidays.%s(years=%s, state="%s")' % (country, year, state))

    # loop thru days within month
    for i in range(1, 30):

        # specify search date
        search_date = datetime.strptime('%s/%s/%s' % (month, i, year), '%m/%d/%Y')
        today = search_date.strftime('%A')

        # case not weekend and not holiday, return the first working day
        if today not in ['Sunday', 'Saturday'] and not state_holidays.get(search_date):
            return search_date

    # should never came here, but return None just in case all days are holidays
    return None


def get_clipboard():

    """
    Get the content inside clipboard
    """

    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        return data

    finally:
        win32clipboard.CloseClipboard()


def set_clipboard(content):

    """
    Set the content inside clipboard

    Parameters:

        content (str): Content that you wish to place inside the clipboard

    Returns:

        str: date in format '%m/%d/%Y'
    """

    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(content)

    finally:
        win32clipboard.CloseClipboard()


def get_pdf_text(file_path):
    """
    This function will process PDF files to string. If the PDF
    is images, the function use OCR by tesseract.

    Parameters:

        file_path (str): path to PDF file

    Returns:

        raw_txt (str): text got in PDF.
    """
    try:
        pdf_file = file_path

        raw = parser.from_file(pdf_file)

        try:
            raw = parser.from_file(pdf_file)
        except:
            raw = {'content': None}
        # if pdf has text
        if len(raw['content']) > 100:
            text = raw['content']

        else:

            if os.path.exists(r"c:\\Tesseract_files\\Tesseract-OCR\\tesseract.exe"):
                # Path of pytesseract
                pytesseract.pytesseract.tesseract_cmd = r"c:\\Tesseract_files\\Tesseract-OCR\\tesseract.exe"
            else:
                raise BusinessException('Tesseract path does not exists')

            if os.path.exists(r'c:\\Tesseract_files\\poppler-0.68.0\\bin'):
                # Store all the pages of the PDF in a variable
                pages = convert_from_path(pdf_file, 500, poppler_path=r'c:\\Tesseract_files\\poppler-0.68.0\\bin')
            else:
                raise BusinessException('Poppler path does not exists')
            image_counter = 1

            # Iterate through all the pages stored above
            for page in pages:

                # filename for each page of PDF as JPG
                filename = "page_" + str(image_counter) + ".jpg"

                # Save the image of the page in system
                page.save(filename, 'JPEG')
                image_counter += 1

            filelimit = image_counter - 1
            text = ''
            for i in range(1, filelimit + 1):

                filename = "page_" + str(i) + ".jpg"

                # Recognize the text as string in image using pytesserct
                read_text = str(((pytesseract.image_to_string(Image.open(filename)))))
                read_text = read_text.replace('-\n', '')
                text += read_text

        return text
    except Exception as exception:
        system_exception(exception, os.path.basename(__file__))


def read_test_result_json(file_path, dic_key):
    import json

    with open(file_path) as f:
        data = json.load(f)
    # type(data)
    # print(data[dic_key])
    return data[dic_key]


def write_test_result_json(file_path, dic):

    # Serializing json
    json_object = json.dumps(dic, indent=4)

    # write to file
    with open(file_path, "w") as outfile:
        outfile.write(json_object)
