# per partner sim
import pandas as pd


class PerPartnerSimulator:
    def __init__(self, partner_id, partner_dataframe, optimizer, simulator_core) -> None:
        self.result_dataframe = pd.DataFrame(columns=['Profit gain',
                                                      'Sustained profit',
                                                      'Profit w/o optimizer',
                                                      'Accumulated profit gain',
                                                      'Accumulated sustained profit',
                                                      'Accumulated profit w/o optimizer',
                                                      'Accumulated profit gain ratio'])
        self.clicks = 0
        self.conversions = 0
        self.last_day = 0
        self.partner_id = partner_id
        self.click_cost = 0
        self.optimizer = optimizer
        self.simulator_core = simulator_core
        self.df = partner_dataframe
        self.days_with_data = []
        self.df_grouped_by_day = None
        self.setup_parnter_info()
        super().__init__()

    def setup_parnter_info(self):
        # count additional stuff
        self.clicks = len(self.df)
        self.conversions = len(self.df[self.df['Sale'] == True])

        # count click-cost
        overall_income = self.df[self.df['Sale'] == True]['SalesAmountInEuro'].sum()
        self.click_cost = (overall_income * 0.12) / self.clicks

        # add dayofyear column
        self.df['dayofyear'] = self.df['click_timestamp'].dt.dayofyear
        self.df['dayofyear'] = self.df['dayofyear'] - self.df['dayofyear'].min()

        # add INCLUDE column, will come in handy later
        self.df.insert(0, 'INCLUDE', True)

        self.last_day = self.df['dayofyear'].max()

        self.df_grouped_by_day = self.df.groupby('dayofyear')  # n.o. groups = last_day
        self.days_with_data = list(self.df_grouped_by_day.groups.keys())
        print('[LOG] Init for partner {} done.'.format(self.partner_id))

    def simulatePartner(self):
        self.simulator_core.reset_cumulative_values()

        for i in range(0, self.last_day + 1):
            if i in self.days_with_data:
                simulation_day_result = self.simulateDay(self.df_grouped_by_day.get_group(i), current_day_number=i)
            else:
                simulation_day_result = self.simulateDay([], current_day_number=i)
            self.result_dataframe = self.result_dataframe.append(simulation_day_result, ignore_index=True)
        print('[LOG] Simulation for partner {} done.'.format(self.partner_id))

    def get_yesterdays_data(self, current_day_number):
        if 0 <= (current_day_number - 1) <= self.last_day:
            return self.get_day(current_day_number - 1)
        else:
            return []

    def get_day(self, day):
        if day in self.days_with_data:
            return self.df_grouped_by_day.get_group(day)
        else:
            return []

    def simulateDay(self, day_df, current_day_number):
        day_df = self.optimizer.optimize_day(self.get_yesterdays_data(current_day_number=current_day_number), day_df)

        return self.simulator_core.calculate_performance_measures(day_df, self.click_cost)

    def save_simulation_results(self, path):
        self.result_dataframe.to_parquet('result.parquet')
        # self.result_dataframe.to_parquet(path + "partner_" + self.partner_id + ".parquet")
        print('[LOG] Results saved.')