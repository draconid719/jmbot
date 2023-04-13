import threading


class ObservableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(ObservableThread, self).__init__(*args, **kwargs)

        self.stop_event = threading.Event()

    def start_thread(self):
        self.start()
        self.stop_event.set()

    def restart_thread(self):
        self.stop_event.set()

    def stop_thread(self):
        self.stop_event.clear()

    def is_running(self):
        return self.stop_event.is_set()
