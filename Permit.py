
class Permit:

    current_id = 1

    def __init__(self, name, field, size, start_dt, end_dt):
        self.permit_id = Permit.current_id
        Permit.current_id += 1

        self.name = name
        self.field = field
        self.size = size
        self.start_dt = start_dt
        self.end_dt = end_dt

        if self.size == 'L':
            self._slots_remaining = 1
        elif self.size == 'XL':
            self._slots_remaining = 2
        else:
            self._slots_remaining = 0

    def __repr__(self):
        return f"#{self.permit_id} {self.name}/{self.field}/{self.size} [{self.start_dt} - {self.end_dt}]"

    def is_available(self):
        return self._slots_remaining > 0

    def get_slots_remaining(self):
        return self._slots_remaining

    def use_slot(self):
        if self.is_available():
            self._slots_remaining -= 1
            return True

        raise ValueError("Permit has already been fully used.")

    def get_availability_interval(self):
        return self.start_dt, self.end_dt

