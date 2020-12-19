import random
import json
import numpy as np


class Optimizer:
    def __init__(self, optimize_option) -> None:
        self.optimize_option = optimize_option
        self.seen_so_far = []
        self.logs = {}
        self.setup_logs()
        super().__init__()

    def setup_logs(self):
        self.logs['days'] = []

    def optimize_day(self, df_yesterday, df_today, log_exclusions=True) -> []:
        products_to_exclude_today = []
        if type(df_yesterday) is not list:
            if self.optimize_option == 'random':
                yesterdays_optimized_products = df_yesterday[df_yesterday['INCLUDE'] == True]['product_id'].unique()
                self.seen_so_far = np.unique(np.concatenate(
                    (yesterdays_optimized_products, self.seen_so_far),
                    axis=0)).tolist()
                products_to_exclude_today = self.random_exclusion(
                    self.seen_so_far,
                    df_yesterday['click_timestamp'].values[0])

                df_today.is_copy = False
                df_today.loc[df_today['product_id'].isin(products_to_exclude_today), 'INCLUDE'] = False
        if log_exclusions:
            self.log_exclusions(df_today, type(df_yesterday), products_to_exclude_today)
        return df_today

    def random_exclusion(self, products, date, how_many_ratio=20, randomseed=12) -> []:
        dummy_list_of_potentially_excluded_products = list(products)
        dummy_list_of_potentially_excluded_products.sort()

        dummy_how_many_products = round(len(dummy_list_of_potentially_excluded_products) / how_many_ratio)
        print('[LOG] Excluded {} products from day {}'.format(dummy_how_many_products, date))
        random.seed(randomseed)
        products_to_exclude = random.sample(dummy_list_of_potentially_excluded_products,
                                            dummy_how_many_products)
        return products_to_exclude

    def log_exclusions(self, day_dataframe, day_yesterday_type, products_to_exclude):
        if type(day_dataframe) is not list:
            date = day_dataframe['click_timestamp'].values[0]
            actually_excluded_products = []
            prod2ex = []

            if day_yesterday_type is not list:
                available_products = set(day_dataframe['product_id'].values)
                actually_excluded_products = list(available_products.intersection(products_to_exclude))
                prod2ex = products_to_exclude

                self.seen_so_far.sort()
                prod2ex.sort()
                actually_excluded_products.sort()

            self.logs['days'].append({
                'day': str(date),
                'productsToExclude': prod2ex,
                'productsSeenSoFar': self.seen_so_far,
                'productsActuallyExcluded': actually_excluded_products
            })

            # with open("exclusions_log.txt", "a+") as logfile:
            #     logfile.write(json.dumps({"Date": str(date)}) + "\n")
            #     logfile.write(json.dumps({"Products to exclude": prod2ex}) + "\n")
            #     logfile.write(json.dumps({
            #         "Actually excluded products": actually_excluded_products}) + "\n")

    def dump_logs(self, filename):
        with open(filename, 'w') as outfile:
            json.dump(self.logs, outfile)
