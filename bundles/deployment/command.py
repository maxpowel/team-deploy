import inject
import tornado.ioloop
import tornado.web
import datetime
from threading import Thread, Condition
from bundles.orm.entity_manager import EntityManager
from bundles.user.entity import User, Request
from bundles.command.app import app
from bundles.config import Config
from bundles.deployment.task import tasks
import json


class LongTaskExecutor(Thread):
    @inject.param('entity_manager', EntityManager)
    def __init__(self, output, entity_manager):
        Thread.__init__(self)
        self.entity_manager = entity_manager
        self.cv = Condition()
        self.busy = False
        self._finish = False
        self.output = output
        self.request_id = None

    def finish(self):
        self.output.writeln("Sutthing down...")
        if self.busy:
            self.output.writeln("Please wait until last job finish..")

        self._finish = True
        self.cv.acquire()
        self.cv.notify()
        self.cv.release()

    def add_task(self, task_name, user):
        request = Request()
        request.date = datetime.datetime.today()
        request.user = user
        request.finished = False
        request.task = task_name
        self.entity_manager.session.add(request)
        self.entity_manager.session.commit()
        self.request_id = request.id
        self.cv.acquire()
        self.cv.notify()
        self.cv.release()
        return request

    def run(self):
        # La session no se puede compartir entre diferentes hilos
        local_session = self.entity_manager.make_session()
        while not self._finish:
            self.cv.acquire()
            self.cv.wait()
            self.cv.release()
            # Ensure that when waiting the finish signal was not called
            if not self._finish:
                self.busy = True
                request = local_session.query(Request).filter(Request.id == self.request_id).first()
                if request.task in tasks:
                    request.output = tasks[request.task]()

                else:
                    request.output = "Invalid task"

                request.finished = True
                local_session.commit()
                self.busy = False
        local_session.close()
        self.output.writeln("All tasks finished")



class MainHandler(tornado.web.RequestHandler):
    @inject.param('entity_manager', EntityManager)
    def get(self, entity_manager):
        self.write("<html><head>")

        self.write('<link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">')
        self.write("</head></body>")
        self.write("<table class='table'><thead><tr>")
        self.write("<th width='2%'>Id</th>")
        self.write("<th width='10%'>Date</th>")
        self.write("<th width='7%'>User</th>")
        self.write("<th width='7%'>Task</th>")
        self.write("<th>Output</th>")
        self.write("<th width='5%'>Status</th>")
        self.write("</tr></thead><tbody>")
        for request in entity_manager.session.query(Request).order_by(Request.id.desc()).limit(10).all():
            self.write("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td</tr>" %
                       (str(request.id), request.date.strftime("%Y-%m-%d %H:%M:%S"), request.user.name,
                        request.task, "Empty" if request.output is None else request.output.replace("\n", "<br>"),
                        str("finished" if request.finished else "running")))
        self.write("</tbody><table>")

        self.write("</body></html>")


class TaskHandler(tornado.web.RequestHandler):
    def initialize(self, t):
        self.t = t

    @inject.param('entity_manager', EntityManager)
    def get(self, task_name, entity_manager):
        token = self.get_argument('token')
        user = entity_manager.session.query(User).filter(User.token == token).first()
        if not user:
            self.write(json.dumps({"message": "Invalid token"}))
            self.set_status(400)
        else:
            if self.t.busy:
                self.write(json.dumps({"message": "Already working. Please try again later"}))
                self.set_status(400)
            else:
                request = self.t.add_task(task_name, user)
                self.set_status(200)
                self.write(json.dumps({"id": request.id}))


@app.command('server:start', description='Start the server')
@inject.param('config', Config)
def server_start(i, o, config):

    t = LongTaskExecutor(o)
    t.start()

    application = tornado.web.Application([
        (r"/task/([0-9a-zA-Z_]+)", TaskHandler, dict(t=t)),
        (r"/", MainHandler),
    ])
    o.writeln("Server started at port %d" % config['port'])
    application.listen(config['port'])
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        pass

    t.finish()
    o.writeln("No more requests will be processed")
