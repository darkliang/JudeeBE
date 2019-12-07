# coding=utf-8
import _judger
import json
python3path = "/home/wang/Workspace/OJ/env/bin/python"
def judgePython3(timelimit, memorylimit, inputpath, outputpath, errorpath, id, judgername):
    return _judger.run(max_cpu_time=timelimit,
                        max_real_time=timelimit*10,
                        max_memory=memorylimit * 1024 * 1024,
                        max_process_number=200,
                        max_output_size=32 * 1024 * 1024,
                        max_stack=32 * 1024 * 1024,
                        # five args above can be _judger.UNLIMITED
                        exe_path=python3path,
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
if __name__ == '__main__':
      a = judgePython3(1000,100,'/home/wang/Workspace/OJ/Judee/in.txt','/home/wang/Workspace/OJ/Judee/out.txt','/home/wang/Workspace/OJ/Judee/err.txt',0,'/home/wang/Workspace/OJ/Judee/a_b')
      a['result'] = a['result']
      f = json.dumps(a)
      print(f)
      