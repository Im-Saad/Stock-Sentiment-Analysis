import praw
from data import *
import time
import pandas as pd
import matplotlib.pyplot as plt
import squarify
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
import emoji    # removes emojis
import re   # removes links
import en_core_web_sm
import string
from config import *


def data_extractor(reddit):   
    
    posts, count, c_analyzed, tickers, titles, a_comments = 0, 0, 0, {}, [], {}
    cmt_auth = {}
    
    for sub in subs:
        subreddit = reddit.subreddit(sub)
        hot_python = subreddit.hot()   
        for submission in hot_python:
            flair = submission.link_flair_text 
            author = submission.author.name         
            
            if submission.upvote_ratio >= upvoteRatio and submission.ups > ups and (flair in post_flairs or flair is None) and author not in ignoreAuthP:   
                submission.comment_sort = 'new'     
                comments = submission.comments
                titles.append(submission.title)
                posts += 1
                try: 
                    submission.comments.replace_more(limit=limit)   
                    for comment in comments:
                        try: auth = comment.author.name
                        except: pass
                        c_analyzed += 1
                        
                        if comment.score > upvotes and auth not in ignoreAuthC:      
                            split = comment.body.split(" ")
                            for word in split:
                                word = word.replace("$", "")       

                                if word.isupper() and len(word) <= 5 and word not in blacklist and word in us:
                                    
                                    if uniqueCmt and auth not in goodAuth:
                                        try: 
                                            if auth in cmt_auth[word]: break
                                        except: pass
                                        
                                    if word in tickers:
                                        tickers[word] += 1
                                        a_comments[word].append(comment.body)
                                        cmt_auth[word].append(auth)
                                        count += 1
                                    else:                               
                                        tickers[word] = 1
                                        cmt_auth[word] = [auth]
                                        a_comments[word] = [comment.body]
                                        count += 1   
                except Exception as e: print(e)
                
                           
    return posts, c_analyzed, tickers, titles, a_comments, picks, subs, picks_ayz


def print_helper(tickers, picks, c_analyzed, posts, subs, titles, time, start_time):

    symbols = dict(sorted(tickers.items(), key=lambda item: item[1], reverse = True))
    top_picks = list(symbols.keys())[0:picks]
    time = (time.time() - start_time)
    
    print("It took {t:.2f} seconds to analyze {c} comments in {p} posts in {s} subreddits.\n".format(t=time, c=c_analyzed, p=posts, s=len(subs)))
    print("Posts analyzed saved in titles")       
    print(f"\n{picks} most mentioned tickers: ")

    times = []
    top = []

    for i in top_picks:
        print(f"{i}: {symbols[i]}")
        times.append(symbols[i])
        top.append(f"{i}: {symbols[i]}")
   
    return symbols, times, top
    
    
def sentiment_analysis(picks_ayz, a_comments, symbols):

    scores = {}
     
    vader = SentimentIntensityAnalyzer()
    vader.lexicon.update(new_words)     
    picks_sentiment = list(symbols.keys())[0:picks_ayz]
    
    for symbol in picks_sentiment:
        stock_comments = a_comments[symbol]
        for cmnt in stock_comments:
    
            emojiless = emoji.get_emoji_regexp().sub(u'', cmnt) 
            
            text_punc  = "".join([char for char in emojiless if char not in string.punctuation])
            text_punc = re.sub('[0-9]+', '', text_punc)
                
            tokenizer = RegexpTokenizer('\w+|\$[\d\.]+|http\S+')
            tokenized_string = tokenizer.tokenize(text_punc)
            lower_tokenized = [word.lower() for word in tokenized_string] 
            
            nlp = en_core_web_sm.load()
            stopwords = nlp.Defaults.stop_words
            sw_removed = [word for word in lower_tokenized if not word in stopwords]
            
            lemmatizer = WordNetLemmatizer()
            lemmatized_tokens = ([lemmatizer.lemmatize(w) for w in sw_removed])
            
            score_cmnt = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
            
            word_count = 0
            for word in lemmatized_tokens:
                if word.upper() not in us:
                    score = vader.polarity_scores(word)
                    word_count += 1
                    for key, _ in score.items():
                        score_cmnt[key] += score[key]    
                else:
                    score_cmnt['pos'] = 2.0               
                    
            try:       
                for key in score_cmnt:
                    score_cmnt[key] = score_cmnt[key] / word_count
            except: pass
                
            
            if symbol in scores:
                for key, _ in score_cmnt.items():
                    scores[symbol][key] += score_cmnt[key]
            else:
                scores[symbol] = score_cmnt        
    
        for key in score_cmnt:
            scores[symbol][key] = scores[symbol][key] / symbols[symbol]
            scores[symbol][key]  = "{pol:.3f}".format(pol=scores[symbol][key])
            
    return scores


def visualization(picks_ayz, scores, picks, times, top):

    print(f"\nSentiment analysis of top {picks_ayz} picks:")
    df = pd.DataFrame(scores)
    df.index = ['Bearish', 'Neutral', 'Bullish', 'Total/Compound']
    df = df.T
    print(df)
      
    squarify.plot(sizes=times, label=top, alpha=.7 )
    plt.axis('off')
    plt.title(f"{picks} most mentioned picks")
    plt.show()

    df = df.astype(float)
    colors = ['red', 'springgreen', 'forestgreen', 'coral']
    df.plot(kind = 'bar', color=colors, title=f"Sentiment analysis of top {picks_ayz} picks:")
    plt.show()


def main():

    start_time = time.time()

    reddit = praw.Reddit(user_agent=reddit_user_agent,
                         client_id=reddit_client_id,
                         client_secret=reddit_client_secret,
                         username = username,
                         password = password)

    posts, c_analyzed, tickers, titles, a_comments, picks, subs, picks_ayz = data_extractor(reddit)
    symbols, times, top = print_helper(tickers, picks, c_analyzed, posts, subs, titles, time, start_time)
    scores = sentiment_analysis(picks_ayz, a_comments, symbols)
    visualization(picks_ayz, scores, picks, times, top)


if __name__ == '__main__':
    main()
    