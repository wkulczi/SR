# per partner sim
import pandas as pd


class PerPartnerSimulator:
    def __init__(self, partner_id, partner_dataframe, optimizer, simulator_core, do_log_exclusions = True) -> None:
        self.result_dataframe = pd.DataFrame(columns=['Profit gain',
                                                      'Sustained profit',
                                                      'Accumulated profit gain',
                                                      'Accumulated sustained profit',
                                                      'Accumulated profit gain ratio'])
        self.clicks = 0
        self.conversions = 0
        self.partner_id = partner_id
        self.click_cost = 0
        self.optimizer = optimizer
        self.simulator_core = simulator_core
        self.df = partner_dataframe
        self.days_with_data = []
        self.day_groups_keys = []
        self.df_grouped_by_day = None
        self.do_log_exclusions = do_log_exclusions
        self.setup_parnter_info()
        super().__init__()

    def setup_parnter_info(self):
        # count additional stuff
        self.clicks = len(self.df)
        self.conversions = len(self.df[self.df['Sale'] == True])

        # count click-cost
        overall_income = self.df[self.df['Sale'] == True]['SalesAmountInEuro'].sum()
        self.click_cost = (overall_income * 0.12) / self.clicks

        # add INCLUDE column, will come in handy later
        self.df.insert(0, 'INCLUDE', True)

        self.df_grouped_by_day = {group: day_df for group, day_df in self.df.groupby('click_timestamp')}

        self.add_missing_days()

        print('[LOG] Init for partner {} done.'.format(self.partner_id))

    def add_missing_days(self):
        day_keys_sorted, missing_keys = self.find_missing_dates(list(self.df_grouped_by_day.keys()))
        self.day_groups_keys = day_keys_sorted
        self.df_grouped_by_day = self.fill_dict(missing_keys, self.df_grouped_by_day)

    def fill_dict(self, missing, dictionary):
        df_headers = ['INCLUDE', 'Sale', 'SalesAmountInEuro', 'time_delay_for_conversion', 'click_timestamp',
                      'nb_clicks_1week', 'product_price', 'product_age_group', 'device_type',
                      'audience_id', 'product_gender', 'product_brand',
                      'prod_category1', 'prod_category2', 'prod_category3', 'prod_category4',
                      'prod_category5', 'prod_category6', 'prod_category7', 'product_country',
                      'product_id', 'product_title', 'partner_id', 'user_id']
        for x in missing:
            dictionary[str(x.date())] = pd.DataFrame(columns=df_headers)
        return dictionary

    def find_missing_dates(self, days_in_df_as_strings):
        from datetime import date, timedelta, datetime
        days_as_datetime = [datetime.strptime(x, "%Y-%m-%d") for x in days_in_df_as_strings]
        date_set = set(
            days_as_datetime[0] + timedelta(x) for x in range((days_as_datetime[-1] - days_as_datetime[0]).days))
        missing = sorted(date_set - set(days_as_datetime))
        return [str(x.date()) for x in sorted(list(date_set))], missing

    def simulatePartner(self):
        self.simulator_core.reset_cumulative_values()

        for day_key in self.day_groups_keys:
            simulation_day_result = self.simulate_day(day_key)
            self.result_dataframe = self.result_dataframe.append(simulation_day_result, ignore_index=True)

        print('[LOG] Simulation for partner {} done.'.format(self.partner_id))

    def get_yester_day(self, current_day):
        if self.day_groups_keys.index(current_day) - 1 < 0:
            return []
        else:
            return self.df_grouped_by_day.get(self.day_groups_keys[self.day_groups_keys.index(current_day) - 1])

    def get_yesterday_key(self, current_day_key):
        if self.day_groups_keys.index(current_day_key) - 1 < 0:
            return ''
        else:
            return self.day_groups_keys[self.day_groups_keys.index(current_day_key) - 1]

    def simulate_day(self, current_day_key):
        self.df_grouped_by_day[current_day_key] = self.optimizer.optimize_day(
            df_yesterday=self.get_yester_day(current_day_key), df_today=self.df_grouped_by_day[current_day_key],
            df_today_dates_string=current_day_key, df_yesterday_dates_string=self.get_yesterday_key(current_day_key),
            log_exclusions=self.do_log_exclusions)

        self.optimizer.dump_logs('exclusion_logs_comparator/my_exclusion_logs/' + str(self.partner_id) + ".json")

        return self.simulator_core.calculate_performance_measures(self.df_grouped_by_day[current_day_key],
                                                                  self.click_cost)

    def save_simulation_results(self, path):
        self.result_dataframe.to_parquet(path + str(self.partner_id) + '.parquet')
        print('[LOG] Results saved.')
