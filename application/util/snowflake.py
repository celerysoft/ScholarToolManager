import threading
import time

import configs


class SnowFlakeToolkit:
    # 2^7 = 128
    WORKER_BITS = 7
    MAX_WORKER_ID = -1 ^ (-1 << WORKER_BITS)
    # 2^3 = 8
    DATA_CENTER_BITS = 3
    MAX_DATA_CENTER_ID = -1 ^ (-1 << DATA_CENTER_BITS)
    SEQUENCE_BITS = 12
    MAX_SEQUENCE = -1 ^ (-1 << SEQUENCE_BITS)
    WORKER_SHIFT = SEQUENCE_BITS
    DATA_CENTER_SHIFT = WORKER_SHIFT + WORKER_BITS
    TIME_SHIFT = DATA_CENTER_SHIFT + DATA_CENTER_BITS

    start_time = configs.SNOWFLAKE_START_TIME
    default_worker = None
    value_lock = threading.Lock()

    class Worker:
        def __init__(self, data_center_id: int, worker_id: int):
            if data_center_id < 0 or data_center_id > SnowFlakeToolkit.MAX_WORKER_ID:
                raise RuntimeError('invalid data_center_id: ' + str(data_center_id))

            if worker_id < 0 or worker_id > SnowFlakeToolkit.MAX_WORKER_ID:
                raise RuntimeError('invalid worker_id: ' + str(data_center_id))

            self.timestamp = 0
            self.data_center_id = data_center_id
            self.worker_id = worker_id
            self.sequence = 0

    @staticmethod
    def get_current_timestamp():
        return int(time.time() * 1000)

    def get_id(self, worker: Worker):
        with self.value_lock:
            now = self.get_current_timestamp()

            if now < worker.timestamp:
                while now <= worker.timestamp:
                    pass

            if worker.timestamp == now:
                worker.sequence += 1
                if worker.sequence > self.MAX_SEQUENCE:
                    while now <= worker.timestamp:
                        now = self.get_current_timestamp()
                    worker.sequence = 0
                    worker.timestamp = now
            else:
                worker.sequence = 0
                worker.timestamp = now

            time_diff = worker.timestamp - self.start_time
            snowflake_id = time_diff << self.TIME_SHIFT | (
                    worker.data_center_id << self.DATA_CENTER_SHIFT) | (
                    worker.worker_id << self.WORKER_SHIFT) | worker.sequence
            return snowflake_id

    def get_id_from_default_worker(self):
        worker = self.get_default_worker()
        return self.get_id(worker)

    def new_worker(self, data_center_id: int, worker_id: int):
        return self.Worker(
            data_center_id=data_center_id,
            worker_id=worker_id,
        )

    def get_default_worker(self):
        if self.default_worker is None:
            self.default_worker = self.Worker(
                data_center_id=configs.SNOWFLAKE_DATACENTER_ID,
                worker_id=configs.SNOWFLAKE_WORKER_ID,
            )
        return self.default_worker


toolkit = SnowFlakeToolkit()
snowflake_toolkit = toolkit

if __name__ == '__main__':
    for x in range(100):
        print(toolkit.get_id_from_default_worker())
