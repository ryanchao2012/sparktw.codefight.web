import random
import time
import json


class MyDict(dict):

    def __init__(self, **kwargs):

        for k, v in self.__class__.__dict__.items():
            if not k.startswith('__'):
                self.__setattr__(k, kwargs.get(k, v))
        attrs = self.__dict__
        dict.__init__(self, **attrs)

    def __str__(self):
        return json.dumps(self)


class QuizData(MyDict):
    description = ''
    uid = ''
    title = ''
    status = ''
    difficulty = ''
    reward = 0


class SnippetData(MyDict):
    language = 'python3'
    body = ''
    run_count = 0
    contestant_id = -1
    quiz_id = -1
    status = ''
    uid = ''
    is_running = False


class EvaluateBase:
    # For subjects test
    # Success
    # {"response_code":0,"response_message":"pass","metrics":{"total":3,"error":0,"success":3}}

    # Syntax Error
    # {"response_code":1,"response_message":"syntax error","metrics":{"total":127,"error":127,"success":0}}

    # Fail
    # {"response_code":2,"response_message":"fail","metrics":{"total":0,"error":1,"success":0}}

    def eval(self, data):
        raise NotImplementedError


class PseudoEvaluator(EvaluateBase):

    template = {
        "response_code": 0,
        "response_message": "pass",
    }

    message = ['Pass', 'Failed']

    def eval(self, data):
        n_test = random.randint(3, 6)
        for i in range(n_test):
            time.sleep(random.randint(1, 3))
            code = random.choice([0, 1])
            yield {
                'response_code': code,
                'response_message': 'Testcase {}: {}'.format(i + 1, self.message[code]),
                'timestamp': time.time()
            }
