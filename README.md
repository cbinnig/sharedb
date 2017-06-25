# ShareDB
## HIPAA PII removal

Our main starting point for the removal of PII is working off of the [HIPAA guidelines](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/).
Specifically, we want to work off of the "Safe Harbor" method, which focuses on the removal of:

1. Names
1. All geographic subdivisions smaller than a state, including street address, city, county, precinct, ZIP code, and their equivalent geocodes, except for the initial three digits of the ZIP code if, according to the current publicly available data from the Bureau of the Census:
    1. The geographic unit formed by combining all ZIP codes with the same three initial digits contains more than 20,000 people; and
    1. The initial three digits of a ZIP code for all such geographic units containing 20,000 or fewer people is changed to 000
1. All elements of dates (except year) for dates that are directly related to an individual, including birth date, admission date, discharge date, death date, and all ages over 89 and all elements of dates (including year) indicative of such age, except that such ages and elements may be aggregated into a single category of age 90 or older
1. Phone numbers
1. Vehicle identifiers and serial numbers, including license plate numbers
1. Fax numbers (see: phone numbers)
1. Device identifiers and serial numbers (MAC addresses, IMEID, etc.)
1. Email addresses
1. URLs and URIs
1. SSNs
1. IP addresses
1. Medical record numbers
1. Biometric identifiers, including finger and voice prints (I don't think there's an easy way to automagically identify these, but I should look into standard formats.)
1. Health plan beneficiary numbers
1. Full-face photographs and any comparable images (i.e. wounds, tattoos, etc.)
1. Account numbers
1. Any other unique identifying number, characteristic, or code, except: Implementation specifications: re-identification. A covered entity may assign a code or other means of record identification to allow information de-identified under this section to be re-identified by the covered entity, provided that:
    1. Derivation. The code or other means of record identification is not derived from or related to information about the individual and is not otherwise capable of being translated so as to identify the individual; and
    1. Security. The covered entity does not use or disclose the code or other means of record identification for any other purpose, and does not disclose the mechanism for re-identification.
1. Certificate/license numbers

Finally, as an overarching requirement, HIPAA requires that "The covered entity does not have actual knowledge that the information could be used alone or in combination with other information to identify an individual who is a subject of the information."

### Leads and existing tools

- [CUSpider](http://www.columbia.edu/acis/security/spider/about.html), which is supposedly open source.

### Simple things:

One easy thing to recognize are SSNs, which are typically of the form ###-##-####, nine digits separated
by dashes. We can easily use `\d{3}-\d{2}-\d{4}` as a regex to find normally formatted SSNs.
If we want to make the dashes optional, we can either just use `-?` or allow for random punctuation breaks, i.e. look for a nine-digit number with random breaks.

## Environment
My work here so far has been done using a virtual environment in the `sharedb` folder.

--

name classifier using labelled dataset -> word embeddings
names w/ bloom filter
glove word vec

--
http://www.cs.cmu.edu/Groups/AI/util/areas/nlp/corpora/names/other/