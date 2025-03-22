class SerialDecoder:
    def __init__(self):
        self.buffer = bytearray()
        self.frames = []

    def add_data(self, data):
        self.buffer.extend(data)
        self.decode_frames()

    def decode_frames(self):
        while True:
            start_index = self.buffer.find(b'A')
            end_index = self.buffer.find(b'Z', start_index + 1)
            if start_index == -1 or end_index == -1:
                break
            if end_index > start_index:
                frame = self.buffer[start_index+1:end_index]
                if len(frame) == 2:
                    value = int.from_bytes(frame, byteorder='little', signed=False)
                    self.frames.append(value)
                del self.buffer[start_index:end_index+1]
            else:
                break

    def get_frames(self):
        frames = self.frames[:]
        self.frames = []
        return frames
