class SimulatorCore:
    def __init__(self) -> None:
        self.accumulated_pg_ratio = 0
        self.accumulated_pg = 0
        self.accumulated_sustained_profit = 0
        super().__init__()

    def calculate_NPM(self, df, click_cost):
        clicks = len(df)
        partner_income = df[df['Sale'] == True]['SalesAmountInEuro'].sum()
        return clicks * click_cost - partner_income * 0.22

    def calculate_performance_measures(self, df, click_cost):
        if type(df) is not list:
            sustained_profit = self.calculate_NPM(df[df['INCLUDE'] == True], click_cost)
            npg = self.calculate_NPM(df[df['INCLUDE'] == False], click_cost)
            self.accumulated_pg += npg
            self.accumulated_sustained_profit += sustained_profit
            if self.accumulated_pg != 0:
                self.accumulated_pg_ratio = self.accumulated_sustained_profit / self.accumulated_pg

            return {'Profit gain': npg,
                    'Sustained profit': sustained_profit,
                    'Accumulated profit gain': self.accumulated_pg,
                    'Accumulated sustained profit': self.accumulated_sustained_profit,
                    'Accumulated profit gain ratio': self.accumulated_pg_ratio}

        else:
            return {'Profit gain': 0,
                    'Sustained profit': 0,
                    'Accumulated profit gain': self.accumulated_pg,
                    'Accumulated sustained profit': self.accumulated_sustained_profit,
                    'Accumulated profit gain ratio': self.accumulated_pg_ratio}

    def reset_cumulative_values(self):
        self.accumulated_pg_ratio = 0
        self.accumulated_pg = 0
        self.accumulated_sustained_profit = 0
