import subprocess
import time


def hello_world():
    response = []
    response.append(subprocess.check_output(["echo", "Hello World!"], universal_newlines=True))
    response.append(subprocess.check_output(["echo", "Other thing"], universal_newlines=True))
    return "\n".join(response)


def delay():
    time.sleep(3)

tasks = {
    "hello_world": hello_world,
    "delay": delay
}