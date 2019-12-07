import os
class Error(Exception):
    pass

class CompilerError(Error):
    def __init__ (self,message):
        self.message = message


if __name__ == '__main__':
    try:
        # raise CompilerError('test')
        pass
    except CompilerError as alpha:
        x, = alpha.args
        print(x)
    finally:
        print('fafdasf')
    # testcases = os.listdir('./ProblemData/%s/' % '1')
    # in_list = [i for i in testcases if i.split('.')[1] == 'in']
    # out_list = [i for i in testcases if i.split('.')[1] == 'out']
    # in_list = sorted(in_list)
    # out_list = sorted(out_list)
    # tests = zip(in_list,out_list)
    # for i,j in tests:
    #     print(i,j)