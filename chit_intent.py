class chitintent:
    def __init__(self):
        self.intent_what = ['뭐야', '알아', '는?', '은?', '누구야', '어디야']
        self.intent_howto = ['하는 법', '어떻게', '치는 법']
        self.intent_recom = ['추천해줘']
    def classify(self, sentence):
        for intent in self.intent_what:
            if intent in sentence:
                return 'what'
        for intent in self.intent_howto:
            if intent in sentence:
                return 'howto'
        for intent in self.intent_recom:
            if intent in sentence:
                return 'recom'
        return 'other'

