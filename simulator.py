import pandas as pd
import pickle
import random
from dask_ml import preprocessing


# dummy optimizer
def get_excluded_products_pseudorandomly(df):
    dummy_list_of_potentially_excuded_products = list(df['product_id'].unique())
    dummy_list_of_potentially_excuded_products.sort()

    how_many_ratio = 3.1
    dummy_how_many_products = round(len(dummy_list_of_potentially_excuded_products) / how_many_ratio)
    random.seed(12)
    excluded_products = random.sample(dummy_list_of_potentially_excuded_products, dummy_how_many_products)
    return excluded_products


def read_partner_parquet(partner_number):
    return pd.read_parquet('../data/partners/partner_' + str(partner_number) + '.parquet')


def calculate_partner_day_profit(df, click_cost):
    clicks = len(df)
    partner_income = df[df['Sale'] == True]['SalesAmountInEuro'].sum()
    return partner_income + (0.1 * partner_income) - (click_cost * clicks)  # NPM?


def simulate_partner_day(df, click_cost):
    return calculate_partner_day_profit(df[df['INCLUDE'] == True], click_cost), calculate_partner_day_profit(df,
                                                                                                             click_cost)


def optimize_ads(df, product_id_label_encoder):
    df['product_id'] = product_id_label_encoder.inverse_transform(df['product_id'].values)
    excluded_list = get_excluded_products_pseudorandomly(df)
    df.loc[df['product_id'].isin(excluded_list), 'INCLUDE'] = False
    return df


def split_partner_records(df):
    df['click_date'] = df['click_timestamp'].apply(lambda x: x.date())
    df_grouped_by_date = df.groupby('click_date')
    return df_grouped_by_date, df_grouped_by_date.groups.keys()


# average partner click cost
def calculate_partner_click_cost(df, number_of_events):
    overall_partner_income = df[df['Sale'] == True]['SalesAmountInEuro'].sum()
    # 12.5% according to GEI
    return (overall_partner_income / number_of_events) * 0.125


def calculate_partner_stats(df, partner_id_label_encoder, number_of_events):
    decoded_partner_id = partner_id_label_encoder.inverse_transform(
        df['partner_id'].unique()[0])
    number_of_sales = len(df[df['Sale'] == True])
    return pd.Series(data=[decoded_partner_id, number_of_events, number_of_sales, number_of_sales / number_of_events],
                     index=['Advertiser', 'Events', 'Sales', 'Efficiency'])


def simulate_partner(df, partner_id_label_encoder, product_id_label_encoder):
    number_of_events = len(df)
    partner_summary_score = calculate_partner_stats(
        df, partner_id_label_encoder, number_of_events)
    partner_click_cost = calculate_partner_click_cost(df, number_of_events)

    partner_simulation_performance = pd.DataFrame(
        columns=['Day', 'Sustained profit', 'Profit gain'])

    # set all values of INCLUDE column to True
    df['INCLUDE'] = True

    df = optimize_ads(df, product_id_label_encoder)

    partner_days, day_keys = split_partner_records(df)

    for day in day_keys:
        performance_with_optimizer, performance_without_optimizer = simulate_partner_day(
            partner_days.get_group(day), partner_click_cost)
        partner_simulation_performance = partner_simulation_performance.append(
            {'Day': day, 'Sustained profit': performance_with_optimizer,
             'Profit gain': performance_with_optimizer - performance_without_optimizer,
             'Bez optymalizatora': performance_without_optimizer}, ignore_index=True)

    # clear memory hack
    x = [df]
    del x

    return partner_summary_score, partner_simulation_performance


def simulate_all_partners(partner_id_label_encoder, product_id_label_encoder):
    partner_summary_scores = pd.DataFrame(
        columns=['Advertiser', 'Events', 'Sales', 'Efficiency'])
    for i in range(220, 250):
        partner_summary_score, partner_simulation_performance = simulate_partner(
            read_partner_parquet(i), partner_id_label_encoder, product_id_label_encoder)
        partner_summary_scores = partner_summary_scores.append(
            partner_summary_score, ignore_index=True)
        partner_simulation_performance.to_parquet(
            '../data/partners_performance/partner_' + str(i) + '.parquet')

        x = [partner_summary_score, partner_simulation_performance]
        del x

    partner_summary_scores.to_parquet('../data/partners_performance_summary.parquet')


if __name__ == "__main__":
    labelEncoders = pickle.load(open("../data/lablencoder.pickle", "rb"))
    simulate_all_partners(labelEncoders.get('partner_id'), labelEncoders.get('product_id'))
