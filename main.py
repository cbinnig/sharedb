from deidentification import Regex, analyze_table
from datahub import DataHub

SSN = Regex(r'\d{3}-\d{2}-\d{4}')
TESTING_TOKEN = 'lJWdZA797heJkvoNk9KM3MR3pASxIV'

def rotate_table(table):
    """Transforms a list of dictionaries into a dictionaries of lists."""
    names = table[0].keys()
    columns = {}
    for name in names:
        columns[name] = []
    for row in table:
        for name in names:
            columns[name].append(row[name])
    return columns

def main():
    conn = DataHub(TESTING_TOKEN)
    table = conn.get_sample('test', 'out', 1000)
    table = rotate_table(table)
    print(analyze_table(table, {'ssn': SSN}))

if __name__ == '__main__':
    main()