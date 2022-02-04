import os
import csv
import re
from operator import itemgetter


# Data format:        3 ERROR: BLECommunicator: Received active status for service: bluetooth. Service running: true
#                     13 WARN : BLECommunicator: Received active status for service: bluetooth. Service running: true
#                      ^ how many times has the same error/warning occurred
from os.path import splitext
from shlex import join


def clear_lines(line):  # Used for cutting out unimportant data
    result = line

    if "GemaltoCinterion_ELS61: Gemalto Hard Reset ()" in line:
        regex = r"odemComm-[0-9].*-[A-Z].*:[0-9]\): "
        subst = " <aggregated>"
        result = re.sub(regex, subst, line, 0, re.MULTILINE)
    elif "SMONI  communication standard not implemented." in line:
        line = line.split(".", 1)
        result = line[0] + "." + " {line data replaced}"
    elif "SMONI line doesnt contain communication standard." in line:
        line = line.split(".", 1)
        result = line[0] + "." + " {line data replaced}"
    elif "MachFullSystem: Shutdown scheduled for" in line:
        regex = r"[A-Z].[a-z].[0-9].*,"
        subst = "{date + time},"
        result = re.sub(regex, subst, line, 0, re.MULTILINE)
    elif "ModemComm: Error (AT '^SMONI' (URC" in line:
        line = line.split("Error (AT '^SMONI'")
        result = line[0] + "URC line: ^SMONI <aggregated>"
    elif "ModemComm: Error (Err instantiating AT '+CMGR' (URC" in line:
        line = line.split("Error (Err instantiating AT '+CMGR'")
        result = line[0] + "URC line: +CMGR <aggregated>"
    elif "ModemComm: Error (Err instantiating AT '+CREG' (URC" in line:
        line = line.split("Error (Err instantiating AT '+CREG'")
        result = line[0] + "URC line: +CREG <aggregated>"
    elif "ModemComm: Error (Err instantiating AT '+CSQ' (URC" in line:
        line = line.split("Error (Err instantiating AT '+CSQ'")
        result = line[0] + "URC line: +CSQ <aggregated>"
    elif "Message came in QueueCommunicator when not expected. Payload:" in line:
        line = line.split("Payload:")
        result = line[0] + "<payload>"
    elif "Error while insertion into database! Statement: INSERT OR REPLACE INTO state" in line:
        line = line.split('VALUES("')
        result = line[0] + " <aggregated>"
    elif "Not understandable AT+CMGR command:" in line:
        line = line.split('command:')
        result = line[0] + "<command>"
    elif "QueueCommunicator: We received error Exception while parsing MUX message. Error code" in line:
        regex = r"ID.[0-9]*[^- ]"
        subst = "<ID>"
        result = re.sub(regex, subst, line, 0, re.MULTILINE)
    elif "QueueCommunicator: We received error Extracted DLP message contains device error." in line:
        regex = r"ID.[0-9]*[^- ]"
        subst = "<ID>"
        result = re.sub(regex, subst, line, 0, re.MULTILINE)
    elif "HttpMachHandler: onError() handling http request:Request[" in line:
        regex = r"@[0-9a-z].*,"
        subst = " <id>,"
        result = re.sub(regex, subst, line, 0, re.MULTILINE)
    elif "ModemComm: Error parsing URC line: ^SMONI:" in line:
        regex = r": [2-5]G,.*"
        subst = ": <error data>"
        result = re.sub(regex, subst, line, 0, re.MULTILINE)
    elif "ModemComm: Exception while parsing line:'^SMONI:" in line:
        regex = r": [2-5]G,.*"
        subst = ": <error data>"
        result = re.sub(regex, subst, line, 0, re.MULTILINE)
    elif "ModemComm: Exception while parsing line:'+CMGR:" in line:
        regex = r": 0,,[0-9].*"
        subst = ": <error data>"
        result = re.sub(regex, subst, line, 0, re.MULTILINE)
    elif "ModemComm: Exception while parsing line:'+CREG:" in line:
        regex = r" [0-9],\".*"
        subst = ": <error data>"
        result = re.sub(regex, subst, line, 0, re.MULTILINE)
    elif "AT_CPIN: Got AT+CPIN? response that module doesn't support! Treating as PinMode.READY." in line:
        regex = r":\+CREG:.*"
        subst = ": +CREG: <error data>"
        result = re.sub(regex, subst, line, 0, re.MULTILINE)
    elif "Detected the restart trigger, reason:" in line:
        regex = r"[A-Z][a-z]{2} .[0-9].[0-9]{2}:[0-9]{2}:[0-9]{2}"
        subst = "<date>"
        result = re.sub(regex, subst, line, 0, re.MULTILINE)
    elif "GemaltoCinterion_ELS61: WWAN connected, but no internet. WWAN_NET_FAIL count:" in line:
        regex = r" count:.*"
        subst = ": <count>"
        result = re.sub(regex, subst, line, 0, re.MULTILINE)
    elif "HttpParser" in line:
        regex = r"@[0-9a-z]*[a-z0-9]"
        subst = " <id>,"
        result = re.sub(regex, subst, line, 0, re.MULTILINE)
    return result


def get_count(line):  # Returns the first integer in every line (error count)
    return int(line.split(" ")[0])


def is_error(line):
    return "ERROR" in line


def save_in_dict(dictionary, line):
    x = line.split(": ", 1)
    if len(x) > 1:  # for exceptions like: 12 Error:    <- name is empty
        dictionary[x[1]] = get_count(line)
    return dictionary


def one_mach(machID):  # Checks every line in current mach file
    path_file = os.path.join("errors_n_warnings", machID)

    error_dict = {}  # dictionary for errors in current file that is later added to the all_dict_err dictionary
    warn_dict = {}  # -||-           warnings                                           all_dict_warn

    with open(path_file, "r", encoding='utf-8') as file:
        lines = file.readlines()
        newlines = []
        for line in lines:
            line = clear_lines(line)
            if re.search("^ .*[0-9].*", line):  # for exceptions when "\n" apears in the middle of the line
                # checks if a row really starts with an integer
                newlines.append(line)
            else:
                newlines[-1] += " " + line

        for line in newlines:
            line = line.strip()  # this is how we get rid of "\n" and spaces in every line
            if is_error(line):
                save_in_dict(error_dict, line)
            else:
                save_in_dict(warn_dict, line)
    return error_dict, warn_dict


def add_to_all_dict(all_dict, dict, file_name):
    file_name = file_name.split(".")
    for key in dict:
        if key in all_dict.keys():
            all_dict[key][0] += dict[key]
        else:
            all_dict[key] = [dict[key]]
        all_dict[key].append(file_name[0])
    return all_dict


def delete_txt(file_name):  # mach: 8737D323D.txt -> 8737D323D
    x = splitext(file_name)
    return x[0]


def print_mach_ids(dict, error_or_warn):
    name_of_file = "machs_" + error_or_warn + ".txt"
    with open(name_of_file, 'w', encoding='utf-8') as f:
        table = []
        for key in dict:
            one_err = []
            key_splitted = key.split(": ", 1)
            one_err.append(key_splitted[0])
            one_err.append(key_splitted[1])
            one_err.append(dict[key][0])
            one_err.append(len(dict[key]) - 1)
            for i in range(1, len(dict[key])):
                one_err.append(dict[key][i])
            table.append(one_err)
        table = sorted(table, key=itemgetter(2), reverse=True)
        for i in range(0, len(table)):
            f.write("Index: " + str(i + 1) + "\n")
            f.write("Class: " + table[i][0] + "\n")
            f.write("Description: " + table[i][1] + "\n")
            f.write("Frequency: " + str(table[i][2]) + "\n")
            f.write("MACH count: " + str(table[i][3]) + "\n")
            f.write("MACH IDs: ")
            for k in range(4, len(table[i])):
                f.write(table[i][k])
                f.write(", ")
            f.write("\n")
            f.write("\n")


def print_csv_format(dict_errors_and_warns, error_or_warn):
    name_of_file = "all_mach_" + error_or_warn + "s" + ".csv"
    with open(name_of_file, 'w', newline='', encoding='utf-8') as f:
        table = []
        for key in dict_errors_and_warns:
            row = []
            key_splitted = key.split(": ", 1)
            row.append(key_splitted[0])
            row.append(key_splitted[1].strip())
            row.append(len(dict_errors_and_warns[key]) - 1)
            row.append(dict_errors_and_warns[key][0])
            table.append(row)
        table = sorted(table, key=itemgetter(3), reverse=True)

        if error_or_warn == "err":
            header_list = ['Java Class', 'Type of Error', 'Mach count', 'Error count']
        else:
            header_list = ['Java Class', 'Type of Warning', 'Mach count', 'Warnings count']
        csvwriter = csv.writer(f)
        csvwriter.writerow(header_list)
        for row in table:
            csvwriter.writerow(row)

if __name__ == "__main__":
    pass

    all_dict_err = {}
    all_dict_war = {}

    all_files = os.listdir("errors_n_warnings")
    all_mach_count = len(all_files)
    for file in all_files:
        error_dict, warn_dict = one_mach(file)
        all_dict_err = add_to_all_dict(all_dict_err, error_dict, file)
        all_dict_war = add_to_all_dict(all_dict_war, warn_dict, file)


    print_csv_format(all_dict_err, "err")
    print_csv_format(all_dict_war, "warn")

    print_mach_ids(all_dict_err, "err")
    print_mach_ids(all_dict_war, "warn")
