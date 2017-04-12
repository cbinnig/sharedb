from classification import SSN, Lookup
from filter import SSNFilter, Drop
from pipeline import Pipe, Pipeline
from datahub import DataHub

TESTING_TOKEN = 'hyhnXY88aAGenabNO6LmOFYi03c8RI'

def read_names():
    names = set()
    with open('data/names.dat') as f:
        for name in f:
            names.add(name.strip().lower())
    return names

def main():
    conn = DataHub(TESTING_TOKEN)
    table = conn.get_sample('test', 'out', 1000)

    name = Lookup(read_names())

    pipeline = Pipeline()
    pipeline.add_data(table)
    pipeline.add_pipe('ssn', Pipe(SSN, SSNFilter()))
    pipeline.add_pipe('name', Pipe(name, Drop()))

    ratings = pipeline.classify()
    print(ratings)
    print({col: max(scores.items(), key=lambda s: s[1])[0] for col, scores in pipeline.ratings.items()})

    pipeline.filter({'ssn': 'ssn', 'first_name': 'name'})

    #print(pipeline.csv())

if __name__ == '__main__':
    main()
