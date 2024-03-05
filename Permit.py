class Permit:
    current_id = 1

    def __init__(self, name, field, size, start_dt, end_dt, permit_number, borough, map_location, assignment=None):
        self.permit_id = Permit.current_id
        Permit.current_id += 1

        self.name = name
        self.field = field
        self.size = size
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.permit_number = permit_number
        self.borough = borough
        self.map_location = map_location

        if assignment:
            self._is_available = False
        else:
            self._is_available = True

        self._assignment = assignment

    def __repr__(self):
        return f"#{self.permit_number} -- {self.name}/{self.field}/{self.size} [{self.start_dt} - {self.end_dt}]"

    def is_available(self):
        return self._is_available

    def get_assignment(self):
        return self._assignment

    def reserve(self, game):
        if self.is_available():
            self._is_available = False
            self._assignment = str(game)
            return

        raise ValueError("Permit has already been fully used.")

    def get_availability_interval(self):
        return self.start_dt, self.end_dt

    @staticmethod
    def generate_permits(name, field, size, start_dt, end_dt, permit_number, borough, map_location, assignment=None):
        if size == 'M' or size == 'L':
            return [
                Permit(name, field, size, start_dt, end_dt, permit_number, borough, map_location, assignment)
            ]
        elif size == 'XL':
            return [
                Permit(name, field, "L", start_dt, end_dt, permit_number, borough, map_location, assignment)
                for _ in range(2)
            ]

        return []

    @staticmethod
    def permit_copy_with_new_availability_interval(original_permit, new_availability_interval):
        new_permit_start_dt, new_permit_end_dt = new_availability_interval

        return Permit(original_permit.name,
                      original_permit.field,
                      original_permit.size,
                      new_permit_start_dt,
                      new_permit_end_dt,
                      original_permit.permit_number,
                      original_permit.borough,
                      original_permit.map_location)
