./manage.py runworker --only-channels='websocket.*' --threads 10
daphne -u /home/ubuntu/apps/sparktw/conf/daphne.sock sparktw.asgi:channel_layer

#Every Page
menu:
    ranking list(?)
    login/logout
    user profile
    *quiz list
    tutorial list(playground)
    about?

#Quiz Page
quiz discription:
    title
    details: p(markdown?)
    testcase
    examples/demos

code submit form:
    language selector
    editor
    submit button

result message:
    p
