import curses
import datetime

MARGIN_TOP = 3
MARGIN_BOTTOM = 0
MARGIN_LEFT = 7
MARGIN_RIGHT = 0
# The width isn't actually adjustable. This is there for code readability
# where calculating widths/heights
OUTER_BORDER_WIDTH = 1
OUTER_BORDER_HEIGHT = 1
GRID_BORDER_WIDTH = 1
GRID_BORDER_HEIGHT = 1
TIMERANGE_BOX_BORDER_WIDTH = 1
TIMERANGE_BOX_BORDER_HEIGHT = 1
TIMERANGE_BOX_HEIGHT = 1

COLOR_CODE_KEYS = (
    "INC",
    "REQ",
    "CRQ",
    "PBI",
    "CCC",
    "TRN",
    "OTH",
    "MON",
    "EML",
    "SCR",
    "RPT",
    "CST",
    "TCS",
    "PTO"
)

class GTDCalendarData:
    REQUIRED_SCHEDULE_KEYS = [
        "uuid",
        "desc",
        "start_dttm",
        "end_dttm",
        "billing_cd"
    ]

    @property
    def start_dttm(self) -> datetime.datetime:
        return datetime.datetime(self._start_date.year, self._start_date.month, self._start_date.day, self._start_hour, 0, 0)

    @property
    def end_dttm(self) -> datetime.datetime:
        return self.start_dttm + datetime.timedelta(hours=self._num_hours)

    def _dttm_is_multiple_of_grid_cells_per_hour(self, dttm: datetime.datetime) -> bool:
        seconds_per_grid_cell_entry = (60 // self._grid_cells_per_hour) * 60
        remainder = dttm.timestamp() % seconds_per_grid_cell_entry
        return remainder == 0

    def _trunc_to_nearest_multiple_of_grid_cells_per_hour(self, dttm: datetime.datetime) -> datetime:
        seconds_per_grid_cell_entry = (60 // self._grid_cells_per_hour) * 60
        trunc_seconds = (dttm.timestamp() // seconds_per_grid_cell_entry) * seconds_per_grid_cell_entry
        return datetime.datetime.fromtimestamp(trunc_seconds)

    def _validate_schedule_entry(self, schedule_entry: dict) -> bool:
        for required_key in GTDCalendarData.REQUIRED_SCHEDULE_KEYS:
            if required_key not in schedule_entry:
                raise KeyError(required_key + " is a required field in schedule entry.")
        if schedule_entry['start_dttm'] >= schedule_entry['end_dttm']:
            raise ValueError("End time must be greater than start time. " + str(schedule_entry['start_dttm']) + ' ' + str(schedule_entry['end_dttm']))
        if schedule_entry['billing_cd'] not in COLOR_CODE_KEYS:
            raise ValueError("Invalid Billing Code " + schedule_entry['billing_cd'])
        return True

    def clear_selection(self):
        self._selected_time_range = None, None

    def select_prev_time_block(self):
        if self._selected_time_range == (None, None):
            return
        selected_start_dttm, selected_end_dttm = self._selected_time_range
        for i in range(len(self._schedule) - 1,-1,-1):
            schedule_entry = self._schedule[i]
            if schedule_entry['end_dttm'] == selected_start_dttm:
                self._selected_time_range = schedule_entry['start_dttm'], schedule_entry['end_dttm']
                return
        for i in range(len(self._schedule) - 1,-1,-1):
            schedule_entry = self._schedule[i]
            if schedule_entry['end_dttm'] < selected_start_dttm and i < len(self._schedule) - 1:
                self._selected_time_range = schedule_entry['end_dttm'], self._schedule[i+1]['start_dttm']
                return
        if self._schedule[0]['start_dttm'] > self.start_dttm:
            # If we made it here there is blank from the beginning of the day
            self._selected_time_range = self.start_dttm, self._schedule[0]['start_dttm']

    def select_next_time_block(self):
        if len(self._schedule) == 0:
           self._selected_time_range = None, None
           return
        if self._selected_time_range == (None, None):
            if self._schedule[0]['start_dttm'] <= self.start_dttm:
                self._selected_time_range = self._schedule[0]['start_dttm'], self._schedule[0]['end_dttm']
            else:
                self._selected_time_range = self.start_dttm, self._schedule[0]['start_dttm']
        else:
            selected_start_dttm, selected_end_dttm = self._selected_time_range
            for schedule_entry in self._schedule:
                if schedule_entry['start_dttm'] == selected_end_dttm:
                    self._selected_time_range = schedule_entry['start_dttm'], schedule_entry['end_dttm']
                    return
            for i in range(len(self._schedule)):
                schedule_entry = self._schedule[i]
                if schedule_entry['start_dttm'] > selected_end_dttm and i > 0:
                    self._selected_time_range = self._schedule[i-1]['end_dttm'], schedule_entry['start_dttm']
                    return
            if self._schedule[-1]['end_dttm'] < self.end_dttm:
                # If we made it here there is blank to the end of the day
                self._selected_time_range = self._schedule[-1]['end_dttm'], self.end_dttm

    def set_schedule(self, sched: list):
        self._schedule = []
        sched.sort(key=lambda x: x['start_dttm'])
        last_end_dttm = None
        for time_entry in sched:
            self._validate_schedule_entry(time_entry)
            entry_in_range = False
            if time_entry['end_dttm'] > self.start_dttm:
                if time_entry['start_dttm'] <= self.end_dttm:
                    entry_in_range = True
            if time_entry['start_dttm'] <= self.end_dttm:
                if time_entry['end_dttm'] > self.start_dttm:
                    entry_in_range = True
            if last_end_dttm is not None:
                if time_entry['start_dttm'] < last_end_dttm:
                    raise ValueError("Schedules cannot overlap")
            last_end_dttm = time_entry['end_dttm']
            if entry_in_range:
                self._schedule.append(time_entry)
        self._used_letters = set()
        for schedule_entry in self._schedule:
            if 'preferred_letter' in schedule_entry:
                if schedule_entry['preferred_letter'] not in self._used_letters:
                    self._used_letters.add(schedule_entry['preferred_letter'])
                    schedule_entry['letter'] = schedule_entry['preferred_letter']
                    continue
            for letter in schedule_entry['desc']:
                if letter not in self._used_letters:
                    self._used_letters.add(letter)
                    schedule_entry['letter'] = letter
                    break

    @property
    def grid_cells(self):
        grid_cells = []
        for i in range(self._num_hours * self._grid_cells_per_hour):
            grid_cells.append({'letter': '-', 'color_pair': 0})
        for schedule_entry in self._schedule:
            grid_cell_start_dttm = self._trunc_to_nearest_multiple_of_grid_cells_per_hour(schedule_entry['start_dttm'])
            start_grid_cell_index = self._get_grid_cell_from_dttm(grid_cell_start_dttm)
            grid_cell_end_dttm = self._trunc_to_nearest_multiple_of_grid_cells_per_hour(schedule_entry['end_dttm'])
            end_grid_cell_index = self._get_grid_cell_from_dttm(schedule_entry['end_dttm'])
            for i in range (start_grid_cell_index, end_grid_cell_index):
                cell_is_whole = False
                if i == 0:
                    if grid_cell_start_dttm == schedule_entry['start_dttm']:
                        cell_is_whole = True
                elif i == (self._num_hours * self._grid_cells_per_hour) - 1:
                    if grid_cell_end_dttm == schedule_entry['end_dttm']:
                        cell_is_whole = True
                        end_grid_cell_index -= 1
                else:
                    cell_is_whole = True
                if cell_is_whole:
                    grid_cells[i]['letter'] = schedule_entry['letter']
                    grid_cells[i]['color_pair'] = COLOR_CODE_KEYS.index(schedule_entry['billing_cd'])
                else:
                    grid_cells[i]['letter'] = '+'
                    grid_cells[i]['color_pair'] = 0

        return grid_cells

    def  _get_grid_cell_from_dttm(self, find_dttm: datetime.datetime) -> int:
        if self.start_dttm <= find_dttm < self.end_dttm:
            return int((find_dttm - self.start_dttm).total_seconds()) // 60 // (60 // self._grid_cells_per_hour)
        return -1

    def __init__(self, start_date: datetime.date, start_hour: int, num_hours: int, grid_cells_per_hour=12):
        self._job_letter_map = None
        self._selected_time_range = None, None
        self._start_date = start_date
        self._start_hour = start_hour
        self._num_hours = num_hours
        self._schedule = []
        self._grid_cells_per_hour = grid_cells_per_hour
        self._used_letters = set()


class DrawGTDCalendar:
    @staticmethod
    def init_colors():
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_YELLOW)
        curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_RED)
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLUE)
        curses.init_pair(8, curses.COLOR_BLUE, curses.COLOR_GREEN)
        curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_MAGENTA)
        curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(11, curses.COLOR_CYAN, curses.COLOR_MAGENTA)
        curses.init_pair(12, curses.COLOR_RED, curses.COLOR_YELLOW)
        curses.init_pair(13, curses.COLOR_MAGENTA, curses.COLOR_YELLOW)
        curses.init_pair(14, curses.COLOR_CYAN, curses.COLOR_BLUE)
        curses.init_pair(15, curses.COLOR_GREEN, curses.COLOR_WHITE)
