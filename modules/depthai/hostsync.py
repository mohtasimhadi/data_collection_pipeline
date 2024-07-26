from datetime import timedelta
MS_THRESHOLD = 5

class HostSync:
    def __init__(self):
        self.arrays = {}

    def add_msg(self, name, msg):
        if not name in self.arrays:
            self.arrays[name] = []

        self.arrays[name].append({"msg": msg, "seq": msg.getSequenceNum()})

        synced = {}
        for name, arr in self.arrays.items():
            for i, obj in enumerate(arr):
                if msg.getSequenceNum() == obj["seq"]:
                    synced[name] = obj["msg"]
                    break

        if len(synced) == 4:
            for name, arr in self.arrays.items():
                for i, obj in enumerate(arr):
                    if obj["seq"] < msg.getSequenceNum():
                        arr.remove(obj)
                    else:
                        break
            return synced
        return False

    def add_msg_t(self, name, msg, ts = None):
        if ts is None:
            ts = msg.getTimestampDevice()

        if not name in self.arrays:
            self.arrays[name] = []

        self.arrays[name].append((ts, msg))

        synced = {}
        for name, arr in self.arrays.items():
            diffs = []
            for i, (msg_ts, msg) in enumerate(arr):
                diffs.append(abs(msg_ts - ts))
            if len(diffs) == 0: break
            diffsSorted = diffs.copy()
            diffsSorted.sort()
            dif = diffsSorted[0]

            if dif < timedelta(milliseconds=MS_THRESHOLD):
                synced[name] = diffs.index(dif)


        if len(synced) == 4:
            for name, i in synced.items():
                self.arrays[name] = self.arrays[name][i:]
            ret = {}
            for name, arr in self.arrays.items():
                ret[name] = arr.pop(0)[1]
            return ret
        return False