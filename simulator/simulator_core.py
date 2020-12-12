class SimulatorCore:
    def __init__(self) -> None:
        self.accumulated_pg_ratio = 0
        self.accumulated_pg = 0
        self.accumulated_sustained_profit = 0
        self.accumulated_p_no_optimizer = 0
        super().__init__()

    def calculate_profit(self, df, click_cost):
        clicks = len(df)
        partner_income = df[df['Sale'] == True]['SalesAmountInEuro'].sum()
        return (partner_income * 0.22) - (clicks * click_cost)

    def new_calculate_profit(self, df, click_cost):
        clicks = len(df)
        partner_income = df[df['Sale'] == True]['SalesAmountInEuro'].sum()
        return clicks * click_cost - partner_income * 0.22

    def calculate_performance_measures(self, df, click_cost):
        if type(df) is not list:
            profit_without_optimizer = self.calculate_profit(df, click_cost)
            sustained_profit = self.calculate_profit(df[df['INCLUDE'] == True], click_cost)
            profit_gain = sustained_profit - profit_without_optimizer
            npg = self.new_calculate_profit(df[df['INCLUDE']==False], click_cost)
            self.accumulated_pg += profit_gain
            self.accumulated_sustained_profit += sustained_profit
            self.accumulated_p_no_optimizer += profit_without_optimizer
            # self.accumulated_pg_ratio = no idea

            return {'Profit gain': profit_gain, 'Sustained profit': sustained_profit,
                    'Profit w/o optimizer': profit_without_optimizer,
                    'NPG' : npg,
                    'Accumulated profit gain': self.accumulated_pg,
                    'Accumulated sustained profit': self.accumulated_sustained_profit,
                    'Accumulated profit w/o optimizer': self.accumulated_p_no_optimizer,
                    'Accumulated profit gain ratio': self.accumulated_pg_ratio}

        #     sustained profit = profit with optimizer
        #     profit gain = sustained profit - profit without optimizer
        #     accumulated sustained profit
        #     accumulated profit gain
        #     accumulated pg ratio ?
        else:
            return {'Profit gain': 0, 'Sustained profit': 0, 'Profit w/o optimizer': 0,
                    'Accumulated profit gain': self.accumulated_pg,
                    'Accumulated sustained profit': self.accumulated_sustained_profit,
                    'Accumulated profit w/o optimizer': self.accumulated_p_no_optimizer,
                    'Accumulated profit gain ratio': self.accumulated_pg_ratio}

    def reset_cumulative_values(self):
        self.accumulated_pg_ratio = 0
        self.accumulated_pg = 0
        self.accumulated_sustained_profit = 0
        self.accumulated_p_no_optimizer = 0
        pass
