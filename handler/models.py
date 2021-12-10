from decimal import Decimal


class Model(dict):
    def __init__(self, *args, **kwargs):
        for key, value in dict(*args, **kwargs).items():
            self[key] = value

    def to_dict(self):
        return dict(self)

    # transform Dynamo Decimal values into booleans or ints
    def __setitem__(self, key, value):
        if not isinstance(value, Decimal):
            dict.__setitem__(self, key, value)
        else:
            dict.__setitem__(self, key, int(value))

    # enable dot-notation
    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        return self.__setitem__(key, value)


# Example of a Model that can map a Dynamo row and also be used in Jinja templates! EnrcyptedAnswers is a PCI table.
class EncryptedAnswers(Model):
    """
    DynamoDB partion key (hashKey) and sort key pattern
    hashKey:  COMPANY_KEY:{formId} -> where formId is an external primary key from the ml-processor service
        - this represents the form definition's UUID that comes directly from the ml-processor Statement table
    contextId:  {contextId} -> where contextId is an external primary key from the ml-processor service
        - this represents the BotContext table's UUID for a given Form Request:Form Response pair. 1 to 1, only ever 1.

    Query Patterns:
        - GET specific answer for a given company, formId and contextId
        - (unused) GET all answers for a given form for a company
        - PUT answer for a given company, formId and contextId

    Attributes:
        hashKey: String
        contextId: String
        companyKey: String
        createdTSSeconds: Long
        ttlTSSeconds: Long
        encryptedAnswers: String | base64, symmetric-encrypted, json string {Map<string FieldId, string Value>}
        wrappedSymmetricKey: String | base64, asymmetric-encrypted, json string {Exported JWK format of symmetric key}
        iv: String | base64 encoded initialization vector used for symmetric-encrypted {encryptedAnswers} value


    Notes:
        - each row has a TTL (time to live), so there will be no DELETE pattern. This is handled automatically.
    """

    def __init__(self, dynamo_encrypted_answers):
        super().__init__(dynamo_encrypted_answers)
        self.hashKey = EncryptedAnswers.get_hash_key(self.companyKey, self.formId)

    @staticmethod
    def get_hash_key(company_key, form_id):
        return f"{company_key}:{form_id}"
