import click
import json


@click.command()
@click.option('--base', default='file1.json',
              help='path to json file to test against. Default = file1.json')
@click.option('--test', default='file2.json', help='path to json file to test with. Default= file2.json')
def hello(base, test):
    """Script to test the correctness of the optimizer exclusion logs"""
    base_file = open(base)
    base_json = json.load(base_file)
    my_file = open(test)
    my_json = json.load(my_file)
    show_results(base_json, my_json)


def json_days_dict(json_file):
    return {json_file['days'].index(day_log): day_log['day'] for day_log in json_file['days']}


def check_extra_days(dr_s_json, student_json):
    student_days = json_days_dict(student_json)
    dr_s_days = json_days_dict(dr_s_json)
    extra_days_in_dr_logs = list(set(dr_s_days.values()) - set(student_days.values()))
    extra_days_in_student_log = list(set(student_days.values()) - set(dr_s_days.values()))
    if len(extra_days_in_dr_logs) > 0:
        click.echo(
            '{} days missing in student log file: {}'.format(str(len(extra_days_in_dr_logs)), extra_days_in_dr_logs))
    if len(extra_days_in_student_log) > 0:
        click.echo('{} days missing in student log file: {}'.format(str(len(extra_days_in_student_log)),
                                                                    extra_days_in_student_log))


def show_results(dr_s_json, student_json):
    check_extra_days(dr_s_json, student_json)
    not_found_days = 0
    correctPtes = 0
    correctPaes = 0
    correctPssf = 0
    alldays = len(dr_s_json['days'])
    for dr_log_day in dr_s_json['days']:
        found_day = next((item for item in student_json['days'] if item["day"] == dr_log_day['day']), None)
        if found_day == None:
            click.echo('[DAY {}] not found {}, skipping.'.format(dr_log_day['day'],
                                                                 'and has no excluded products' if len(
                                                                     dr_log_day['productsToExclude']) == 0 else ''))
            not_found_days = not_found_days + 1
        else:
            pte_correct = set(dr_log_day['productsToExclude']) == set(found_day['productsToExclude'])
            pae_correct = set(dr_log_day['productsActuallyExcluded']) == set(found_day['productsActuallyExcluded'])
            pssf_correct = set(dr_log_day['productsSeenSoFar']) == set(found_day['productsSeenSoFar'])
            click.echo("[DAY {}] productsToExclude: {}, productsActuallyExcluded: {}, productsSeenSoFar: {}".format(
                dr_log_day['day'], 'valid' if pte_correct else 'invalid', 'valid' if pae_correct else 'invalid',
                'valid' if pssf_correct else 'invalid'))
            if not pte_correct:
                click.echo("[ERR] productsToExclude: expected - yours: {}".format(
                    (set(dr_log_day['productsToExclude']) - set(found_day['productsToExclude']))))
            else:
                correctPtes = correctPtes + 1
            if not pae_correct:
                click.echo("[ERR] productsActuallyExcluded: expected - yours: {}".format(
                    (set(dr_log_day['productsActuallyExcluded']) - set(found_day['productsActuallyExcluded']))))
            else:
                correctPaes = correctPaes + 1
            if not pssf_correct:
                click.echo("[ERR] productsSeenSoFar: expected - yours: {}".format(
                    (set(dr_log_day['productsActuallyExcluded']) - set(found_day['productsActuallyExcluded']))))
            else:
                correctPssf = correctPssf + 1
    click.echo(
        '{}/{} correct productsToExclude\n{}/{} correct productsActuallyExcluded\n{}/{} correct productsSeenSoFar\n{}'.format(
            str(correctPtes), str(alldays), str(correctPaes), str(alldays), str(correctPssf), str(alldays),
            ('Not found: {} days'.format(str(not_found_days)) if not_found_days > 0 else '')))


if __name__ == "__main__":
    hello()
