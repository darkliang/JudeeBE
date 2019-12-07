import socket
import json
import _judger
import time
import socket
import logging
import threading
import os
import filecmp
import json
from Judee.judee_errors import *
'''
Judging Flow:
    1. Get the Submission ID from Judge Server
    2. Get the Corresponding TestCases(zip) and code
    3. Compile if necessary
    4. Running for each testcase and recording the result
    5. Update database

Dictionary:
    ProblemData/?/[#.in, #.out] -- ? is the problem id, # is the testcase id
    UserData/?/[#.output, #.error]  -- ? is the User id, # is corresponding to the testcase id

'''
class Running_Status:
    status = True
    JudgerName = 'Judee'

class Global_Parameters:
    db_keys = ['db_ip', 'db_pwd', 'db_user', 'db_port']
    server_keys = ['server_ip', 'server_port', 'key']
    path_keys = ['python3','java','c','cpp']
    server_config = {key : None for key in server_keys}
    db_config = {key : None for key in db_keys}
    path_list = {key : None for key in path_keys}
    @staticmethod
    def init_path(pathname,systempath):
        try:
            path_list[pathname] = systempath
        except:
            pass
    @staticmethod
    def init_db_info():
        try:
            with open('./conf.d/database.json', 'r') as f:
                db_json = json.loads(f.read())
            for key in db_keys:
                db_config[key] = db_json[key]
        except json.decoder.JSONDecodeError:
            print('DB Json file is not legal')
            exit(-1)
        except KeyError:
            print('DB Json file not satisify format')
            exit(-1)
        except FileNotFoundError:
            print('DB config file not exist')
            exit(-1)
    @staticmethod
    def init_server_info():
        try:
            with open('./conf.d/judge_server.json', 'r') as f:
                logging.debug('Reading the Judger Server Configuration')
                server_json = json.loads(f.read())
            for key in server_keys:
                server_config[key] = server_json[key]
        except (json.decoder.JSONDecodeError, KeyError):
            logging.info('Server Configuration Json File isn\'t legal')
            exit(-1)
        except FileNotFoundError:
            logging.info('Server Configuration File isn\'t exist')
            exit(-1)
class Connection_Manager:
    db_connection = None
    judgeserver_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    @staticmethod
    def connect_judge_server(server_config):
        # TODO Exception Handle
        try:
            judgeserver_connection.connect((server_config['server_ip'],server_config['server_port']))
        except socket.timeout :
            raise socket.timeout
    @staticmethod
    def connect_db_server():
        pass
def judgePython3(timelimit, memorylimit, inputpath, outputpath, errorpath, id, judgername):
    return _judger.run(max_cpu_time=timelimit,
                        max_real_time=timelimit*10,
                        max_memory=memorylimit * 1024 * 1024,
                        max_process_number=200,
                        max_output_size=32 * 1024 * 1024,
                        max_stack=32 * 1024 * 1024,
                        # five args above can be _judger.UNLIMITED
                        exe_path=Global_Parameters.path_list['python3'],
                        input_path=inputpath,
                        output_path=outputpath,
                        error_path=errorpath,
                        args=[judgername+".py"],
                        # can be empty list
                        env=[],
                        log_path=judgername+"judger.log",
                        # can be None
                        seccomp_rule_name="general",
                        uid=0,
                        gid=0
                        )

def judgeC(timelimit, memorylimit, inputpath, outputpath, errorpath, id, judgername):
    return _judger.run(max_cpu_time=timelimit,
                        max_real_time=timelimit*10,
                        max_memory=memorylimit * 1024 * 1024,
                        max_process_number=200,
                        max_output_size=32 * 1024 * 1024,
                        max_stack=32 * 1024 * 1024,
                        # five args above can be _judger.UNLIMITED
                        exe_path=judgername+".out",
                        input_path=inputpath,
                        output_path=outputpath,
                        error_path=errorpath,
                        args=[],
                        # can be empty list
                        env=[],
                        log_path=judgername+"judger.log",
                        # can be None
                        seccomp_rule_name="c_cpp",
                        uid=0,
                        gid=0
                        )

def judgeCPP(timelimit, memorylimit, inputpath, outputpath, errorpath, id, judgername):
    return _judger.run(max_cpu_time=timelimit,
                        max_real_time=timelimit*10,
                        max_memory=memorylimit * 1024 * 1024,
                        max_process_number=200,
                        max_output_size=32 * 1024 * 1024,
                        max_stack=32 * 1024 * 1024,
                        # five args above can be _judger.UNLIMITED
                        exe_path=judgername+".out",
                        input_path=inputpath,
                        output_path=outputpath,
                        error_path=errorpath,
                        args=[],
                        # can be empty list
                        env=[],
                        log_path=judgername+"judger.log",
                        # can be None
                        seccomp_rule_name="c_cpp",
                        uid=0,
                        gid=0
                        )


def compileC(id,code,problem):
    # transfer code into file named with judgername
    tmp_name = 'tmp_'+str(problem)
    with open('%s.c' % tmp_name, 'w',encoding='utf-8') as f:
        f.write(code)
    
    result = os.system('timeout 10 gcc %s.c -fmax-errors=3 -o %s.out -O2 -std=c11 2>%sce.txt' % (tmp_name, tmp_name, tmp_name))

    if result != 0:
        try:
            with open('%sce.txt' % tmp_name, 'r') as f:
                msg = str(f.read())
            if msg == '':
                msg = 'Compile timeout! Maybe you define too big arrays!'
                raise CompilerError(msg)
        except FileNotFoundError:
            msg = str('Fatal Compile error!')
            raise CompilerError(msg)

def compileCPP(id,code,judgername,problem):
    file = open("%s.cpp" % judgername, "w",encoding='utf-8')
    file.write(code)
    file.close()
    result = os.system("timeout 10 g++ %s.cpp -fmax-errors=3 -o %s.out -O2 -std=c++14 2>%sce.txt" %(judgername, judgername, judgername))
    if result:
        try:
            filece = open("%sce.txt" % judgername, "r")
            msg = str(filece.read())
            if msg == "": msg = "Compile timeout! Maybe you define too big arrays!"
            filece.close()
            # Controller.compileError(id,problem,msg)
            GlobalVar.statue = True
        except:
            msg = str("Fatal Compile error!")
            # Controller.compileError(id,problem,msg)
            # GlobalVar.statue = True
        return False
    return True
def compilePython3(id,code,judgername,problem):
    tmp_name = 'tmp_' + str(problem)
    with open('')
    with open()
    file = open("%s.py" % judgername, "w",encoding='utf-8')
    # file.write("import sys\nblacklist = ['importlib','traceback','os']\nfor mod in blacklist:\n    i = __import__(mod)\n    sys.modules[mod] = None\ndel __builtins__.__dict__['eval']\ndel __builtins__.__dict__['exec']\ndel __builtins__.__dict__['locals']\ndel __builtins__.__dict__['open']\n" +code)
    file.write(code)
    file.close()
    return True

#  utils
def PackupTestcases(problem):
    testcases = os.listdir('./ProblemData/%s/' % problem)
    in_list = [i for i in testcases if i.split('.')[1] == 'in']
    out_list = [i for i in testcases if i.split('.')[1] == 'out']
    in_list = sorted(in_list)
    out_list = sorted(out_list)
    tests = zip(in_list,out_list)
    return tests

def judge(id, code, lang, problem, contest, username):
    '''
        id: submission id
        code: submission code
        lang: submission language
        problem: problem id
        contest: 属于哪个比赛的提交，为0时，不属于任何比赛的提交
        username: user id
    '''
    timelimit = 0
    memorylimit = 0
    try:
        tests = PackupTestcases(problem)
        if lang == 'C':
            compileC(id,code,problem)
        if lang == 'python3':
            pass
        result_list = []
        for incase,outcase in tests:
            logging.debug('Judging %s %s' % (incase, outcase))
            incasePath = './ProblemData/%s/%s' % (problem, incase)
            outcasePath = './ProblemData/%s/%s' % (problem, outcase)
            outputPath = './UserData/%s/%s/%s' % (username, problem, outcase)
            errorPath = './UserData/%s/%s/%s' % (username, problem, caseid)
            caseid = incase.split('.')[0]
            if lang == 'C':
                result = judgeC(timelimit, memorylimit, incasePath, outputPath, errorPath, id, Running_Status.JudgerName)
            
            result['result'] = -2 if not filecmp.cmp(outcasePath, outputPath) else result['result']
            result_list.append(json.dumps(result))
    except NotADirectoryError:
        logging.debug('./ProblemData/%s/ not exist' % problem)
        # Update the Database

    except CompilerError as e:
        msg,_ = e.args
        logging.info('Compile Error %s' % msg) 
        
    except Exception as e:
        raise e
    else:
        
    finally:
        Running_Status = True
        return


        
        

            





def run():
    while True:
        time.sleep(1)
        try:
            data = cm.judgeserver_connection.recv(2048)
            assert data == None
            data = data.decode('utf-8')
            if data == 'status':
                cm.judgeserver_connection.send('1'.encode('utf-8') if Running_Status.status else '0'.encode('utf-8'))
            elif data == 'timeout':
                logging.debug('Long Time No Result')
                # Update DataBase with Timeout
                break
            elif data.find('judge') != -1:
                Running_Status.status = False
                submission_id = data.split('|')[1]
                # get  serial info
                try:
                    # Search the submit entry
                    pass
                except:
                    # No entry
                    pass
                t = threading.Thread(target=judge, args=(
                    data[0], data[13], data[8], data[3], data[11], data[1], data[9], data[12], data[2],data[15],isoi))
                t.setDaemon(True)
                t.start()
        except:
            pass

    # pass


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG',format='%(name)s - %(levelname)s - %(message)s')
    g_pars = Global_Parameters()
    g_pars.init_db_info()
    g_pars.init_server_info()
    cm = Connection_Manager()
    # connect to servers
    run()
    print('test')

