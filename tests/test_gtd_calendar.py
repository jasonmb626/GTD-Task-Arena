import datetime
import copy

import pytest

from widgets.gtd_calendar import GTDCalendarData
from tests.test_data import test_schedule_1

class TestGTDCalendar:

    def setup_method(self):
        self.schedule = copy.deepcopy(test_schedule_1)
        self.cal = GTDCalendarData(datetime.datetime(2025, 3, 16), 8, 12)

    def test_get_start_dttm(self):
        assert self.cal.start_dttm == datetime.datetime(2025, 3, 16, 8)

    def test_get_end_dttm(self):
        assert self.cal.end_dttm == datetime.datetime(2025, 3, 16, 20)

    def test_will_validate_all_required_fields_schedule_entry(self):
        del self.schedule[1]['end_dttm']
        with pytest.raises(KeyError):
            self.cal._validate_schedule_entry(self.schedule[1])

    def test_will_validate_end_dttm_greater_than_start_dttm(self):
        self.schedule[1]['end_dttm'] = self.schedule[1]['start_dttm']
        with pytest.raises(ValueError):
            self.cal._validate_schedule_entry(self.schedule[1])
        assert self.cal._validate_schedule_entry(self.schedule[0])

    def test_will_clear_selection(self):
        self.cal.clear_selection()
        assert self.cal._selected_time_range == (None, None)

    def test_will_not_select_prev_time_block_from_none_selected(self):
        self.cal.clear_selection()
        self.cal.select_prev_time_block()
        assert self.cal._selected_time_range == (None, None)

    def test_can_select_next_block_from_none_selected_beginning_of_cal_has_time_data(self):
        self.cal.set_schedule(self.schedule)
        self.cal.clear_selection()
        self.cal.select_next_time_block()
        assert self.cal._selected_time_range == (datetime.datetime(2025, 3, 16, 6),
                                                 datetime.datetime(2025, 3, 16, 8, 35))

    def test_can_select_next_block_from_none_selected_beginning_of_cal_does_not_have_time_data(self):
        del self.schedule[1]
        self.cal.set_schedule(self.schedule)
        self.cal.clear_selection()
        self.cal.select_next_time_block()
        assert self.cal._selected_time_range == (datetime.datetime(2025, 3, 16, 8),
                                                 datetime.datetime(2025, 3, 16, 8, 45))

    def test_next_will_select_empty_block_from_non_empty_block_selected(self):
        self.cal.set_schedule(self.schedule)
        selected_start_dttm = self.schedule[1]['start_dttm']
        selected_end_dttm = self.schedule[1]['end_dttm']
        self.cal._selected_time_range = selected_start_dttm, selected_end_dttm
        self.cal.select_next_time_block()
        assert self.cal._selected_time_range == (datetime.datetime(2025, 3, 16, 8, 35),
                                                 datetime.datetime(2025, 3, 16, 8, 45))

    def test_next_will_select_non_empty_block_from_empty_block_selected(self):
        self.cal.set_schedule(self.schedule)
        selected_start_dttm = self.schedule[1]['end_dttm']
        selected_end_dttm = self.schedule[2]['start_dttm']
        self.cal._selected_time_range = selected_start_dttm, selected_end_dttm
        self.cal.select_next_time_block()
        assert self.cal._selected_time_range == (datetime.datetime(2025, 3, 16, 8, 45),
                                                 datetime.datetime(2025, 3, 16, 9, 0))

    def test_next_will_select_non_empty_block_from_non_empty_block_selected(self):
        self.cal.set_schedule(self.schedule)
        selected_start_dttm = self.schedule[2]['start_dttm']
        selected_end_dttm = self.schedule[2]['end_dttm']
        self.cal._selected_time_range = selected_start_dttm, selected_end_dttm
        self.cal.select_next_time_block()
        assert self.cal._selected_time_range == (datetime.datetime(2025, 3, 16, 9, 0),
                                                 datetime.datetime(2025, 3, 16, 10, 35))

    def test_will_select_prev_block_from_last_block_selected_selection_empty(self):
        self.schedule[4]['end_dttm'] -= datetime.timedelta(minutes=20)
        self.cal.set_schedule(self.schedule)
        self.cal._selected_time_range = self.schedule[4]['end_dttm'], self.cal.end_dttm
        self.cal.select_prev_time_block()
        assert self.cal._selected_time_range == (datetime.datetime(2025, 3, 16, 19, 35),
                                                 datetime.datetime(2025, 3, 16, 19, 45))

    def test_will_select_prev_block_from_last_block_selected_selection_not_empty(self):
        self.cal.set_schedule(self.schedule)
        self.cal._selected_time_range = self.schedule[4]['start_dttm'], self.schedule[4]['end_dttm']
        self.cal.select_prev_time_block()
        assert self.cal._selected_time_range == (datetime.datetime(2025, 3, 16, 10, 35),
                                                 datetime.datetime(2025, 3, 16, 19, 35))

    def test_will_select_prev_block_from_first_block_selected_no_data_at_start_of_day(self):
        del self.schedule[1]
        self.cal.set_schedule(self.schedule)
        self.cal._selected_time_range = self.schedule[1]['start_dttm'], self.schedule[1]['end_dttm']
        self.cal.select_prev_time_block()
        assert self.cal._selected_time_range == (datetime.datetime(2025, 3, 16, 8, 0),
                                                 datetime.datetime(2025, 3, 16, 8, 45))


    def test_will_not_select_next_block_from_last_block_selected_schedule_goes_to_end(self):
        self.cal.set_schedule(self.schedule)
        self.cal._selected_time_range = (datetime.datetime(2025, 3, 16, 19, 35),
                                                 datetime.datetime(2025, 3, 16, 20, 5))
        self.cal.select_next_time_block()
        assert self.cal._selected_time_range == (datetime.datetime(2025, 3, 16, 19, 35),
                                                 datetime.datetime(2025, 3, 16, 20, 5))


    def test_will_select_to_end_next_block_from_last_block_selected_schedule_does_not_go_to_end(self):
        self.schedule[4]['end_dttm'] = datetime.datetime(2025, 3, 16, 19, 45)
        self.cal.set_schedule(self.schedule)
        self.cal._selected_time_range = self.schedule[4]['start_dttm'], self.schedule[4]['end_dttm']
        #Last non-empty block now selected, proceed to select the end blank block
        self.cal.select_next_time_block()
        assert self.cal._selected_time_range == (datetime.datetime(2025, 3, 16, 19, 45),
                                                 datetime.datetime(2025, 3, 16, 20, 0))

    def test_will_sort_schedule_entries(self):
        temp = self.schedule[4]
        self.schedule[4] = self.schedule[0]
        self.schedule[0] = temp
        self.cal.set_schedule(self.schedule)
        last_start_dttm = None
        schedule_is_sorted = True
        for i in range(len(self.cal._schedule)):
            if i == 0:
                last_start_dttm = self.cal._schedule[i]['start_dttm']
                continue
            if self.cal._schedule[i]['start_dttm'] < last_start_dttm:
                schedule_is_sorted = False
            last_start_dttm = self.cal._schedule[i]['start_dttm']
        assert schedule_is_sorted

    def test_will_find_schedule_overlap(self):
        self.schedule[1]['start_dttm'] = self.schedule[0]['end_dttm'] - datetime.timedelta(minutes=15)
        with pytest.raises(ValueError):
            self.cal.set_schedule(self.schedule)

    def test_will_filter_sched_data_outside_calendar_timerange(self):
        self.cal.set_schedule(self.schedule)
        should_not_be_in_list = [
                "a73e25f7-07cb-49c8-aafc-4365b2674bc4",
                "aae24f8b-4333-4b8b-82c2-a56593303733",
        ]
        should_be_in_list = [
            "19ebebf0-e438-4dba-9716-8aa11faf49d0",
            "6f19c52a-e376-4e69-b8bb-84e724c41333",
            "af96b4c1-b058-423e-971e-a6c4f764216b",
            "e24e3889-6ce4-4162-9561-b2cb6b010f27",
        ]
        should_be_in_list_missing_entries = False
        for uuid in should_be_in_list:
            record = next(iter([i for i in self.cal._schedule if i['uuid'] == uuid]), {})
            if record == {}:
                should_be_in_list_missing_entries = True
        should_not_be_in_list_present_entries = False
        for uuid in should_not_be_in_list:
            record = next(iter([i for i in self.cal._schedule if i['uuid'] == uuid]), {})
            if record != {}:
                should_not_be_in_list_present_entries = True
        assert not should_be_in_list_missing_entries and not should_not_be_in_list_present_entries

    def test_will_pick_preferred_letter_for_job(self):
        self.cal.set_schedule(self.schedule)
        schedule_entry = next(iter([i for i in self.cal._schedule if i['uuid'] == '19ebebf0-e438-4dba-9716-8aa11faf49d0']), {'letter': ''})
        assert schedule_entry['letter'] == 'O'

    def test_will_pick_letter_for_job_no_preferred_letter(self):
        self.cal.set_schedule(self.schedule)
        schedule_entry = next(iter([i for i in self.cal._schedule if i['uuid'] == '6f19c52a-e376-4e69-b8bb-84e724c41333']), {'letter': ''})
        assert schedule_entry['letter'] == 'I'

    def test_will_pick_letter_for_job_no_preferred_letter_1st_letter_in_use(self):
        self.cal.set_schedule(self.schedule)
        schedule_entry = next(iter([i for i in self.cal._schedule if i['uuid'] == 'e24e3889-6ce4-4162-9561-b2cb6b010f27']), {'letter': ''})
        assert schedule_entry['letter'] == 'm'

    def test_gets_1st_grid_cell_index_from_dttm(self):
        grid_cell_index = self.cal._get_grid_cell_from_dttm(datetime.datetime(2025, 3, 16, 8, 0))
        assert grid_cell_index == 0

    def test_gets_grid_cell_index_from_dttm_not_5_minute_interval(self):
        grid_cell_index = self.cal._get_grid_cell_from_dttm(datetime.datetime(2025, 3, 16, 9, 12, 54))
        assert grid_cell_index == 14

    def test_fails_gets_grid_cell_index_from_dttm_too_early(self):
        grid_cell_index = self.cal._get_grid_cell_from_dttm(datetime.datetime(2025, 3, 15, 9, 12, 54))
        assert grid_cell_index == -1

    def test_fails_gets_grid_cell_index_from_dttm_too_late(self):
        grid_cell_index = self.cal._get_grid_cell_from_dttm(datetime.datetime(2025, 3, 16, 20, 0, 0))
        assert grid_cell_index == -1

    def test_gets_last_grid_cell_index_from_dttm(self):
        grid_cell_index = self.cal._get_grid_cell_from_dttm(datetime.datetime(2025, 3, 16, 19, 55))
        assert grid_cell_index == 143

    def test_will_reject_schedule_data_invalid_billing_cd(self):
        self.schedule[1]['billing_cd'] = 'DSFS'
        with pytest.raises(ValueError):
            self.cal.set_schedule(self.schedule)

    def test_will_return_right_grid_data_one_small_schedule_entry(self):
        schedule = self.schedule[2:3]
        self.cal.set_schedule(schedule)
        expected_grid_data = [
            {'letter': '-', 'color_pair': 0},
            {'letter': '-', 'color_pair': 0},
            {'letter': '-', 'color_pair': 0},
            {'letter': '-', 'color_pair': 0},
            {'letter': '-', 'color_pair': 0},
            {'letter': '-', 'color_pair': 0},
            {'letter': '-', 'color_pair': 0},
            {'letter': '-', 'color_pair': 0},
            {'letter': '-', 'color_pair': 0},
            {'letter': 'I', 'color_pair': 11},
            {'letter': 'I', 'color_pair': 11},
            {'letter': 'I', 'color_pair': 11},
            {'letter': '-', 'color_pair': 0},
        ]
        assert self.cal.grid_cells[:len(expected_grid_data)] == expected_grid_data

    def test_will_return_right_grid_data_one_small_schedule_entry_2(self):
        schedule = self.schedule[1:2]
        self.cal.set_schedule(schedule)
        expected_grid_data = [
            {'letter': 'O', 'color_pair': 9},
            {'letter': 'O', 'color_pair': 9},
            {'letter': 'O', 'color_pair': 9},
            {'letter': 'O', 'color_pair': 9},
            {'letter': 'O', 'color_pair': 9},
            {'letter': 'O', 'color_pair': 9},
            {'letter': 'O', 'color_pair': 9},
            {'letter': '-', 'color_pair': 0},
        ]
        assert self.cal.grid_cells[:len(expected_grid_data)] == expected_grid_data

    def test_trunc_to_nearest_5_minutes_works(self):
        nearest = self.cal._trunc_to_nearest_multiple_of_grid_cells_per_hour(datetime.datetime(2025, 3,16, 8, 4))
        assert nearest == datetime.datetime(2025, 3, 16, 8, 0)
        nearest = self.cal._trunc_to_nearest_multiple_of_grid_cells_per_hour(datetime.datetime(2025, 3,16, 9, 0))
        assert nearest == datetime.datetime(2025, 3, 16, 9, 0)

    def test_gets_dttm_is_multiple_of_grid_cells_per_hour(self):
        is_multiple = self.cal._dttm_is_multiple_of_grid_cells_per_hour(datetime.datetime(2025, 3, 16, 8, 0))
        assert is_multiple
        is_multiple = self.cal._dttm_is_multiple_of_grid_cells_per_hour(datetime.datetime(2025, 3, 16, 8, 1))
        assert not is_multiple
