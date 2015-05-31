import os
import sys

if sys.version_info[0] == 2:
    import futures
    import Queue as queue
else:
    import queue
    import concurrent.futures as futures


class MeanThreadPoolExecutor(futures.ThreadPoolExecutor):
    """This is an evil ThreadPoolExecutor which will
    throw away all items in the workqueue, when shutdown.
    """

    def __init__(self, max_workers):
        """Initialize a new pool with the max number of workers

        :raises: None
        """
        super(MeanThreadPoolExecutor, self).__init__(max_workers)

    def shutdown(self, wait=True):
        """Works like :meth:`futures.ThreadPoolExecutor` with the exception
        that the current queue is emptied. All items in the queue are not
        processed."""
        with self._shutdown_lock:
            self._shutdown = True
            try:
                while True:
                    self._work_queue.get(block=False)
            except queue.Empty:
                self._work_queue.put(None)
        if wait:
            for t in self._threads:
                t.join()
