class GradeBuffer:
    def __init__(self, students):
        self.__items = students
        self.__curr = 0

    def size(self):
        return len(self.__items)

    def remaining(self):
        return len(self.__items) - self.__curr

    def next(self):
        if self.remaining() <= 0:
            return None
        to_grade = self.__items[self.__curr]
        self.__curr += 1
        return to_grade

    def rewind(self, num):
        rewound = min(self.__curr, num)
        self.__curr = max(0, self.__curr - num)
        return rewound

    def peek(self, index = None):
        if not index:
            index = self.__curr
        return self.__items[index]

    def is_empty(self):
        return self.remaining() <= 0

    def append_list(self, values):
        assert type(values) == list
        self.__items += values

    def set_values(self, values):
        assert type(values) == list
        self.__items = values
        self.__curr = 0

    def get_graded(self):
        return self.__items[:self.__curr]

    def get_to_grade(self):
        return self.__items[self.__curr:]

    def encode(self):
        return (self.__curr, self.__items)

    def decode(self, encoded):
        self.__curr = encoded[0]
        self.__items = encoded[1]
