import subprocess
import os


class BackendException(Exception):
    pass


class twBackend:
    def __init__(self, logger) -> None:
        self.log = logger

    def command(self, commands: list):
        env = os.environ.copy()
        mcmd = commands.copy()
        if len(commands) == 0 or commands[0] != "timew":
            mcmd = ["timew"] + commands
        p = subprocess.Popen(
            mcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
        )
        stdout, stderr = [x.decode("utf-8") for x in p.communicate()]
        self.log(f"{p.returncode=}\n{stdout=}\n{stderr=}", 8)
        return (
            stdout.rstrip(),
            stderr.rstrip(),
            p.returncode,
        )
