"""
Pre-defined Pipelines to match certain deidentification standards,
like HIPAA.
"""
from pipeline import Pipe, Pipeline
from classification import SSNClassifier, EmailClassifier, PhoneNumberClassifier, MACAddressClassifier, IPAddressClassifier, URLClassifier, ZipCodeClassifier, NumberClassifier, AddressClassifier, Lookup, DateClassifier, FaceClassifier
from filter import Drop, ZipCodeFilter, AddressFilter, DateFilter

class Bundle:
    def __init__(self, pipeline, description):
        """
        Creates a new bundle from a pre-configured pipeline and a description.
        """
        self.pipeline = pipeline
        self.description = description

def read_names():
    names = set()
    with open('data/names.dat') as f:
        for name in f:
            names.add(name.strip().lower())
    return names

def build_hipaa():
    pipeline = Pipeline()
    pipeline.add_pipe('name', Pipe(Lookup(read_names()), Drop()))
    pipeline.add_pipe('zip', Pipe(ZipCodeClassifier, ZipCodeFilter()))
    pipeline.add_pipe('address', Pipe(AddressClassifier(), AddressFilter()))
    pipeline.add_pipe('date', Pipe(DateClassifier(), DateFilter()))
    pipeline.add_pipe('phone_number', Pipe(PhoneNumberClassifier, Drop()))
    pipeline.add_pipe('email', Pipe(EmailClassifier, Drop()))
    pipeline.add_pipe('url', Pipe(URLClassifier, Drop()))
    pipeline.add_pipe('ssn', Pipe(SSNClassifier, Drop()))
    pipeline.add_pipe('ip_address', Pipe(IPAddressClassifier, Drop()))
    pipeline.add_pipe('mac_address', Pipe(MACAddressClassifier, Drop()))
    pipeline.add_pipe('face', Pipe(FaceClassifier(), Drop()))
    # TODO: This is far too sensitive
    # pipeline.add_pipe('number', Pipe(NumberClassifier, Drop()))
    return pipeline

HIPAABundle = Bundle(build_hipaa(), 'HIPAA PII Removal')

def build_ferpa():
    pipeline = Pipeline()
    pipeline.add_pipe('name', Pipe(Lookup(read_names()), Drop()))
    pipeline.add_pipe('zip', Pipe(ZipCodeClassifier, ZipCodeFilter()))
    pipeline.add_pipe('address', Pipe(AddressClassifier(), AddressFilter()))
    pipeline.add_pipe('date', Pipe(DateClassifier(), DateFilter()))
    pipeline.add_pipe('phone_number', Pipe(PhoneNumberClassifier, Drop()))
    pipeline.add_pipe('email', Pipe(EmailClassifier, Drop()))
    pipeline.add_pipe('ssn', Pipe(SSNClassifier, Drop()))
    return pipeline

FERPABundle = Bundle(build_ferpa(), 'FERPA PII Removal')
