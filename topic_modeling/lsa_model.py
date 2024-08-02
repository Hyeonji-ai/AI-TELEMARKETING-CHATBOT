from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
class LSA_Model:
    def __init__(self,text):
        topic_text=text 
        text_file = topic_text
        documents = [topic_text]
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(documents)
        try:
            svd_model = TruncatedSVD(n_components=3, algorithm='randomized', n_iter=100, random_state=122)
            svd_model.fit(X)
        except ValueError as V:
            svd_model = TruncatedSVD(n_components=1, algorithm='randomized', n_iter=100, random_state=122)
            svd_model.fit(X)

        terms = vectorizer.get_feature_names_out()
        n = 2
        components = svd_model.components_
        tt=[]
        for index, topic in enumerate(components):
            tq=[terms[i] for i in topic.argsort()]
            tt.append(tq)
        self.lsa_result = tt
        f= open('t1.txt','w')
        for i in range(len(tt)):
            for x in range(len(tt[i])):
                f= open('t1.txt','a')
                f.write(self.lsa_result[i][x]+'\n')
                f.close()


    def LSAmodel(self):
        return self.lsa_result
        
    
