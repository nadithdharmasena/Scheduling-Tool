
class PermitFactory:
    @staticmethod
    def generate_permits(name, field, size, start_dt, end_dt):
        if size == 'L':
            new_permit = Permit(name, field, size, start_dt, end_dt)
            return [new_permit]
        elif size == 'XL':
            first_new_permit = Permit(name, field, size, start_dt, end_dt)
            second_new_permit = Permit(name, field, size, start_dt, end_dt)
            return [first_new_permit, second_new_permit]

        return []


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

        self._is_available = True

    def __repr__(self):
        return f"#{self.permit_id} {self.name}/{self.field}/{self.size} [{self.start_dt} - {self.end_dt}]"

    def is_available(self):
        return self._is_available

    def reserve(self):
        if self.is_available():
            self._is_available = False
            return

        raise ValueError("Permit has already been fully used.")

    def get_availability_interval(self):
        return self.start_dt, self.end_dt

