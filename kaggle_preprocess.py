import numpy
import cPickle as pkl

from collections import OrderedDict

import glob
import os

from subprocess import Popen, PIPE

# tokenizer.perl is from Moses: https://github.com/moses-smt/mosesdecoder/tree/master/scripts/tokenizer
tokenizer_cmd = ['./tokenizer.perl', '-l', 'en', '-q', '-']

dataset_path='kaggleData/'


def tokenize(sentences):

    print 'Tokenizing..',
    text = "\n".join(sentences)
    tokenizer = Popen(tokenizer_cmd, stdin=PIPE, stdout=PIPE)
    tok_text, _ = tokenizer.communicate(text)
    toks = tok_text.split('\n')[:-1]
    print 'Done'

    return toks
	
	
def grab_data(path, dictionary,arg):
    sentences = []
    currdir = os.getcwd()
    os.chdir(path)
    label = []
    for line in open("data.tsv",'r'):
	a = line.strip().split("\t")
	if arg=="test":
		if len(a) < 3:
			print a
        sentences.append(a[2])
	if arg=="train":
		label.append(int(a[3]))
	else:
		if len(a) > 3:
			print a
		label.append(0)
    
    os.chdir(currdir)
    sentences = tokenize(sentences)

    seqs = [None] * len(sentences)
    for idx, ss in enumerate(sentences):
        words = ss.strip().lower().split()
        seqs[idx] = [dictionary[w] if w in dictionary else 1 for w in words]

    return seqs,label

def build_dict(path):
    sentences = []
    currdir = os.getcwd()
    os.chdir('%s' % path)
    #for ff in glob.glob("*.tsv"):
        #with open(ff, 'r') as f:
    for line in open("data.tsv",'r'):
            sentences.append(line.strip().split("\t")[2])
    	    #print line.strip().split("\t")[2]
    #print(sentences[0])
    #print(os.getcwd())
    os.chdir(currdir)

    sentences = tokenize(sentences)

    print 'Building dictionary..',
    wordcount = dict()
    for ss in sentences:
        words = ss.strip().lower().split()
        for w in words:
            if w not in wordcount:
                wordcount[w] = 1
            else:
                wordcount[w] += 1

    counts = wordcount.values()
    keys = wordcount.keys()

    sorted_idx = numpy.argsort(counts)[::-1]

    worddict = dict()

    for idx, ss in enumerate(sorted_idx):
        worddict[keys[ss]] = idx+2  # leave 0 and 1 (UNK)

    print numpy.sum(counts), ' total words ', len(keys), ' unique words'

    return worddict
	

def main():
    path = dataset_path
    dictionary = build_dict(os.path.join(path, 'train'))
  
    train_x,train_y = grab_data(path+'train/', dictionary,"train")
    #train_x_neg = grab_data(path+'train/neg', dictionary)
    #train_x = train_x_pos + train_x_
    #train_y = [1] * len(train_x_pos) + [0] * len(train_x_neg)
    print len(train_x)
    print len(train_y)
    test_x,test_y = grab_data(path+'test/', dictionary,"test")
    print len(test_x)
    print len(test_y)
    #test_x_neg = grab_data(path+'test/neg', dictionary)
    #test_x = test_x_pos + test_x_neg
    #test_y = [1] * len(test_x_pos) + [0] * len(test_x_neg)

    f = open('kaggle.pkl', 'wb')
    pkl.dump((train_x, train_y), f, -1)
    pkl.dump((test_x, test_y), f, -1)
    f.close()

    f = open('kaggle.dict.pkl', 'wb')
    pkl.dump(dictionary, f, -1)
    f.close()

if __name__ == '__main__':
    main()
