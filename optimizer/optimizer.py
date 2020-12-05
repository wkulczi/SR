import random
import json


class Optimizer:
    def __init__(self, optimize_option, product_id_label_enc) -> None:
        self.optimize_option = optimize_option
        self.product_id_label_enc = product_id_label_enc
        # self.optimize_options = {'random':self.random_exclusion}
        super().__init__()

    def optimize_day_zero(self) -> []:
        # todo -> nwm co tu
        return []

    def optimize_day(self, df_yesterday, df_today, log_exclusions=True) -> []:
        excluded_products = []
        # returns empty if gets empty, fu
        if type(df_yesterday) is not list:
            if self.optimize_option == 'random':
                excluded_products = self.random_exclusion(df_yesterday[df_yesterday['INCLUDE'] == True])
            if type(df_today) is not list:
                df_today.is_copy = False
                df_today.loc[df_today['product_id'].isin(excluded_products), 'INCLUDE'] = False
        if log_exclusions:
            self.log_exclusions(df_today, type(df_yesterday), excluded_products)
        return df_today

    def random_exclusion(self, df_day, how_many_ratio=20, randomseed=12) -> []:
        dummy_list_of_potentially_excluded_products = list(df_day['product_id'].unique())
        dummy_list_of_potentially_excluded_products = self.product_id_label_enc.inverse_transform(
            dummy_list_of_potentially_excluded_products)
        dummy_list_of_potentially_excluded_products.sort()

        dummy_how_many_products = round(len(dummy_list_of_potentially_excluded_products) / how_many_ratio)
        print('[LOG] Excluded {} products from day {}'.format(dummy_how_many_products, df_day['dayofyear'].values[0]))
        random.seed(randomseed)
        products_to_exclude = random.sample(dummy_list_of_potentially_excluded_products.tolist(),
                                            dummy_how_many_products)
        return self.product_id_label_enc.transform(products_to_exclude)

    def log_exclusions(self, day_dataframe, day_yesterday_type, products_to_exclude):
        if type(day_dataframe) is not list:
            date = day_dataframe['click_timestamp'].dt.date.values[0]
            actually_excluded_products = []
            prod2ex = []

            if day_yesterday_type is not list:
                available_products = set(day_dataframe['product_id'].values)
                actually_excluded_products = self.product_id_label_enc.inverse_transform(
                    list(available_products.intersection(products_to_exclude))).tolist()
                prod2ex = self.product_id_label_enc.inverse_transform(list(products_to_exclude)).tolist()

            with open("exclusions_log.txt", "a+") as logfile:
                logfile.write(json.dumps({"Date": str(date)}) + "\n")
                logfile.write(json.dumps({"Products to exclude": prod2ex}) + "\n")
                logfile.write(json.dumps({
                    "Actually excluded products": actually_excluded_products}) + "\n")
