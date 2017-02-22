#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, getopt, os
import requests


def update_config(config_url, mitm=False, path=''):
    list_to_add = read_list(find_file_path('add_list.txt'))
    list_to_remove = read_list(find_file_path('remove_list.txt'))
    if mitm:
        list_to_remove.append('[MITM]')
    conf_header, isheader = read_header(find_file_path('header.txt'))
    list_raw_conf = get_raw_list(config_url, isheader).splitlines(keepends=False)
    list_new_raw = list_raw_conf
    for line in list_raw_conf[:]:
        for remove in list_to_remove:
            if remove in line:
                list_new_raw.remove(line)
                log_append('Removing: ' + line)
    if mitm:
        new_conf = ''.join(conf_header.splitlines(True)[1:])
    else:
        new_conf = conf_header
    try:
        for line2 in list_to_add:
            list_raw_conf.insert(list_new_raw.index('[Rule]') + 1, line2)
            log_append("Adding: " + line2)
    except ValueError:
        log_append('Not a legal config file for Surge..')
        exit(0)
    log_append('Refining header...')
    new_conf += '\n'.join(list_raw_conf)
    mitm_name = ''
    if mitm:
        log_append('Adding MitM configs...')
        mitm_conf, is_mitm = read_header(find_file_path('mitm.txt'))
        if is_mitm:
            new_conf += mitm_conf
            mitm_name = 'MitM'
        else:
            log_append('MitM loading failed!')
    if not os.path.exists(path) and path != '':
        os.mkdir(path)
    with open(os.path.join(path, 'Surge{}.conf'.format(mitm_name)), 'w', encoding='utf-8') as ff:
        ff.write(new_conf)
    log_append('New config ready: ' + 'Surge{}.conf'.format(mitm_name))

def find_file_path(path):
    file_path = path
    if os.path.exists(file_path):
       return file_path
    file_path = os.path.join(os.path.dirname(__file__), path)
    if os.path.exists(file_path):
        return file_path
    return path

def read_list(path):
    list = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if len(line.strip()) > 0 :
                    list.append(line.strip())
    except FileExistsError:
        log_append('Can\'t find: ' + path)
    return list

def read_header(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            str_header = f.read()
            return str_header, True
    except FileExistsError:
        log_append('Can\'t find: ' + path)
        return '', False



def log_append(str):
    print(str)


def get_raw_list(url,cut_header=True):
    try:
        log_append('Downloading remote config from: ' + url)
        res = requests.get(url)
        res.encoding = 'utf-8'
        raw_conf_with_header = res.text
        if cut_header:
            index1 = raw_conf_with_header.find('[Host]')
            index2 = raw_conf_with_header.find('[Rule]')
            index = min(index1,index2)
        else:
            index = 0
        if res.ok:
            log_append('download remote config complete!')
            return raw_conf_with_header[index:]
        else:
            log_append('Error when downloading...')
            exit()
    except Exception:
        log_append('Error when downloading...')
        exit()



def print_help():
    print('This is a Surge config file updater.')
    print('Options:')
    print('--url <url>        Remote url for a config file, default is from lhie1')
    print('-p, --path <path>  Define a local path to save new config file')
    print('-m, --mitm         Add MitM configs to the file from mitm.txt')
    print('-h, --help         display this')
    print('Make header.txt add_list.txt remove_list.txt in the path of this program')
    print('add_list.txt       Rules will be add to new downloaded file.')
    print('remove_list.txt    Rules will be removed from downloaded file if existed')
    print('header.txt         The header of your config including [General],[Proxy],[Proxy Group]')
    print('See the samples to learn more')
    print('For more information please contact weekendy963@gmail.com')



if __name__ == '__main__':
    url = 'https://raw.githubusercontent.com/lhie1/Surge/master/Surge.conf'
    mitm = False
    path = ''
    if len(sys.argv) == 1:
        update_config(url, False)
        exit(0)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hmp:", ['url=', 'help', 'path=', 'mitm'])
    except getopt.GetoptError:
        print_help()
        exit(0)
    if len(opts) > 0:
        for op, value in opts:
            if op == '--url':
                url = value
            elif op in ['-h', '--help']:
                print_help()
                exit(0)
            elif op in ['-m', '--mitm']:
                mitm = True
            elif op in ['-p', '--path']:
                path = value
            else:
                print_help()
                exit(0)
        update_config(url, mitm, path)
        exit(0)
    else:
        print_help()
        exit(0)











