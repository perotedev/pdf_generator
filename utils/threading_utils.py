import threading
from typing import Callable, Any

class WorkerThread(threading.Thread):
    """
    A simple worker thread to run tasks in the background without blocking the GUI.
    Since this project uses CustomTkinter (Tkinter), we use Python's threading module.
    """
    def __init__(self, target: Callable, args: tuple = (), kwargs: dict = None, 
                 on_finish: Callable = None, on_error: Callable = None):
        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}
        self.on_finish = on_finish
        self.on_error = on_error
        self.daemon = True

    def run(self):
        try:
            result = self.target(*self.args, **self.kwargs)
            if self.on_finish:
                self.on_finish(result)
        except Exception as e:
            if self.on_error:
                self.on_error(e)
            else:
                print(f"Error in WorkerThread: {e}")
