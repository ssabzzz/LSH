import random
import time

class LSH:
    def __init__(self, config_file):
        self.dataFile = config_file['dataFile']
        self.validationFile = config_file['validationFile']
        self.number_of_hashFunctions = config_file['number_of_hashFunctions']
        self.similarity = config_file['similarity']
        self.r = config_file['r']
        self.b = config_file['b']
        self.shingleNumber = config_file['shingleNumber']
        self.candidates = []
        #self.shingles = set()
        self.largest_hashed_shingle =0
        self.docAndShingles = {}
        self.signatures = {}
        self.trueDuplicates = {}
        self.prepare()
        self.coef1_list = []
        self.coef2_list = []
        assert self.r * self.b == self.number_of_hashFunctions , "Values of r, b and number_of_hashFunctions are inconsistent"
        
    def gen_trueDuplicate_dict(self):
        with open(self.validationFile) as f:
            for line in f:
                docs = line.split(" ")
                self.trueDuplicates[docs[0]] = docs[1].replace('\n','')
                self.trueDuplicates[docs[1].replace('\n','')] = docs[0]
        return
    
    def prepare(self):
        sn = self.shingleNumber
        with open(self.dataFile) as f:
            print('Reading input file ...')
            for line in f:
                words = line.split(" ")
                docID = words[0]
                self.docAndShingles.setdefault(docID, [])
                del words[0]
                for i in range(0, (len(words) - sn) + 1 ):
                    word_hash = hash(" ".join(words[i:i+sn]))
                    self.docAndShingles[docID].append(word_hash)
                    self.largest_hashed_shingle = max(word_hash, self.largest_hashed_shingle)
                    #self.shingles.update(words)
        print("{} docs have been found.".format(len(self.docAndShingles.keys())))
        #print("{} shingles have been hashed overall.".format(len(self.shingles)))
        self.gen_trueDuplicate_dict()
        self.coef1_list, self.coef2_list = self.generate_hash_function_coeffs()
                    #print(self.coef1_list)
                    #print(self.coef2_list)
        self.generae_signatures() 
        self.combine()
        self.calc_metrics(self.validate_similarity())
        #print(self.signatures.keys())
        return
       # print(self.docAndShingles)
                    
    def generate_hash_function_coeffs(self):
        coef1_list = []
        coef2_list = []
        print("Generating hash functions ...")
        self.print_dots()
        for i in range(0, self.number_of_hashFunctions):
            coef1 = random.randint(0, 100)
            coef2 = random.randint(0, 100)
            while coef1 in coef1_list:
                coef1 = random.randint(0, 100)
            coef1_list.append(coef1)  
            while coef2 in coef2_list:
                coef2 = random.randint(0, 100)
            coef2_list.append(coef2)
        print("{} hash functions have been generated.".format(self.number_of_hashFunctions))
        self.print_dots()
        return coef1_list, coef2_list
        #print(coef1_list, coef2_list)
    
    def generae_signatures(self):
        print("Generating signature matrix ...")
        self.print_dots()
        for i in range(0,self.number_of_hashFunctions):
            for doc in self.docAndShingles:
                minimum_hashed_shingle_for_doc = self.largest_hashed_shingle +1
                for shingle in self.docAndShingles[doc]:
                    hashed_shingle = (self.coef1_list[i]*shingle + self.coef2_list[i]) % (self.largest_hashed_shingle + 1)
                    minimum_hashed_shingle_for_doc = min(self.largest_hashed_shingle,hashed_shingle)
                self.signatures.setdefault(doc, []).append(minimum_hashed_shingle_for_doc)
        assert len(self.signatures.keys()) == len(self.docAndShingles.keys()) , "#docs in signature matrix is not equal to #docs in representation matrix"
        print("Signature matrix generation completed.")
        self.print_dots()
        return
    
    def calc_sim(self, doc1, doc2): 
        sig1 = self.signatures[doc1]
        sig2 = self.signatures[doc2]
        sim = 0
        for i in range(0,self.b):
            for j in range(0,self.r):
                #print("{}".format(i*self.r+j))
                if sig1[i*self.r+j] == sig2[i*self.r+j]:
                    sim += 1
                    if sim == self.r:
                        self.candidates.append((doc1, doc2))
                        #print("Yep similar!")
                        return  
        #print("No similarity.")
        return
    
    def combine(self):
        t0 = time.time()
        i = 1
        for doc1 in self.signatures:
            for doc2 in list(self.signatures)[i:]:
                if( doc1 != doc2):
                    #print("Calculating similarity between {} and {}".format(doc1,doc2))
                    self.calc_sim(doc1, doc2)
            i += 1
        print("It took {} seconds to compare all documents using LSH technique.".format(time.time()-t0))
        self.print_dots()
        #print(self.candidates)
        #print(len(self.candidates))
    def calc_jaccard(self, doc1, doc2):
        doc1_shingles = set(self.docAndShingles[doc1])
        doc2_shingles = set(self.docAndShingles[doc2])
        jaccard_sim = len(doc1_shingles.intersection(doc2_shingles)) / len(doc1_shingles.union(doc2_shingles))
        if( jaccard_sim >= self.similarity):
            return True
        else:
            return False

    def validate_similarity(self):
        calculated_dups = []
        for i in self.candidates:
            if self.calc_jaccard(i[0], i[1]):
                #print("{} - {} similar".format(i[0], i[1]))
                calculated_dups.append(i)
        return calculated_dups
    def calc_metrics(self, calculated_dups):
        true_pos = 0
        false_pos = 0
        for dups in calculated_dups:
            if dups[0] in self.trueDuplicates and self.trueDuplicates[dups[0]] == dups[1]:
                true_pos += 1
            else:
                false_pos += 1
        all_trueDups = len(self.trueDuplicates) / 2
        false_neg = all_trueDups - true_pos 
        precision = true_pos / (true_pos + false_pos)
        recall = true_pos / (true_pos + false_neg)
        #print("true_pos {}".format(true_pos))
        #print("false_pos {}".format(false_pos))
        #print("false_neg {}".format(false_neg))
        print("Precision {}".format(precision))
        print("Recall {}".format(recall))
    def print_dots(self):
        i = 4
        while i > 0:
            print(".")
            i -= 1
                
            