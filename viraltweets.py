# -*- coding: utf-8 -*-
"""viraltweets.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bsQpJf--VByQ8DKSSWpEjWYoR33ZMfpJ

# Importing libraries
"""

# Commented out IPython magic to ensure Python compatibility.
# essentials
import pandas as pd
import numpy as np 

# misc libraries
import random
import timeit
import math 
import collections 

# surpress warnings
import warnings
warnings.filterwarnings('ignore')

# Data Visualization
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_theme(style='darkgrid', color_codes=True)
plt.style.use('fivethirtyeight')
# %matplotlib inline

# model building
import lightgbm as lgb
import graphviz
import xgboost as xgb
from sklearn import tree
from skimage.io import imshow,imread,imsave
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_selection import SelectFromModel as sel
from sklearn.feature_selection import mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split,RandomizedSearchCV
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
#from tpot import TPOTClassifier

"""## helper functions"""

from google.colab import drive
drive.mount('/content/drive')

def printColumnTypes(df):
    non_num_df = df.select_dtypes(include=['object'])
    num_df = df.select_dtypes(exclude=['object'])
    '''separates non-numeric and numeric columns'''
    print("Non-Numeric columns:")
    for col in non_num_df:
        print(f"{col}")
    print("")
    print("Numeric columns:")
    for col in num_df:
        print(f"{col}")

def missing_cols(df):
    '''prints out columns with its amount of missing values with its %'''
    total = 0
    for col in df.columns:
        missing_vals = df[col].isnull().sum()
        pct = df[col].isna().mean() * 100
        total += missing_vals
        if missing_vals != 0:
          print('{} => {} [{}%]'.format(col, df[col].isnull().sum(), round(pct, 2)))
    
    if total == 0:
        print("no missing values")

"""# Loading data"""

# Note: this path will be different depending on where you store the dataset
tweets_path = '/content/drive/MyDrive/Tweets/'
users_path = '/content/drive/MyDrive/Users/'

# Load training datasets
train_tweets = pd.read_csv(tweets_path + 'train_tweets.csv')
train_tweets_vectorized_media = pd.read_csv(tweets_path + 'train_tweets_vectorized_media.csv')
train_tweets_vectorized_text = pd.read_csv(tweets_path + 'train_tweets_vectorized_text.csv')

# Load test dataset
test_tweets = pd.read_csv(tweets_path + 'test_tweets.csv')
test_tweets_vectorized_media = pd.read_csv(tweets_path + 'test_tweets_vectorized_media.csv')
test_tweets_vectorized_text = pd.read_csv(tweets_path + 'test_tweets_vectorized_text.csv')

# Load user dataset
users = pd.read_csv(users_path + 'users.csv')
user_vectorized_descriptions = pd.read_csv(users_path + 'user_vectorized_descriptions.csv')
user_vectorized_profile_images = pd.read_csv(users_path + 'user_vectorized_profile_images.csv')

# print dimensions of data
print('Dimension of train tweets is', train_tweets.shape)
print('Dimension of train tweets vectorized media is', train_tweets_vectorized_media.shape)
print('Dimension of train tweets vectorized text is', train_tweets_vectorized_text.shape)
print()

print('Dimension of test tweets is', test_tweets.shape)
print('Dimension of test tweets vectorized media is', test_tweets_vectorized_media.shape)
print('Dimension of test tweets vectorized text is', test_tweets_vectorized_text.shape)
print()

print('Dimension of users is', users.shape)
print('Dimension of user vectorized descriptions is', user_vectorized_descriptions.shape)
print('Dimension of user vectorized profile images is', user_vectorized_profile_images.shape)
print()

"""# Exploratory Data Analysis"""

train_tweets.head()

train_tweets_vectorized_media.head()

train_tweets_vectorized_text.head()

train_tweets.info()

printColumnTypes(train_tweets)

"""## train tweets features"""

train_tweets['virality'].describe()

sns.countplot(x = 'virality', data = train_tweets, palette="Set1");

fig, axs = plt.subplots(2, 2, figsize=(12, 8))

sns.histplot(train_tweets, x = 'tweet_created_at_year', discrete = True, ax = axs[0,0]);
sns.histplot(train_tweets, x = 'tweet_created_at_day', discrete = True, ax = axs[0,1]);
sns.histplot(train_tweets, x = 'tweet_created_at_month', discrete = True, ax = axs[1,0]);
sns.histplot(train_tweets, x = 'tweet_created_at_hour', discrete = True, ax = axs[1,1]);

fig, axs = plt.subplots(3, 1, figsize=(12, 10))

sns.histplot(x = 'tweet_hashtag_count', data = train_tweets, discrete = True, ax = axs[0]);
sns.histplot(x = 'tweet_url_count', data = train_tweets, discrete = True, ax = axs[1]);
sns.histplot(x = 'tweet_mention_count', data = train_tweets, discrete = True, ax = axs[2]);

fig, axs = plt.subplots(2, 1, figsize=(10, 7))

sns.countplot(x = 'tweet_attachment_class', data = train_tweets, palette="Set1", ax = axs[0]);
sns.countplot(x = 'tweet_language_id', data = train_tweets, ax = axs[1]);

sns.countplot(x = 'tweet_has_attachment', data = train_tweets, palette="Set1");

corrmat = train_tweets.corr()[2:] 
sns.heatmap(corrmat, vmax=.8, square=True);

df_corr = train_tweets.corr()['virality'][2:-1]
top_features = df_corr.sort_values(ascending=False)
top_features

"""## Eda on users data"""

user_vectorized_descriptions.head()

user_vectorized_descriptions.describe()

user_vectorized_profile_images.head()

users.info()

fig, axs = plt.subplots(2, 2, figsize=(12, 8))

sns.histplot(users, x = 'user_like_count', ax = axs[0,0]);
sns.histplot(users, x = 'user_followers_count', ax = axs[0,1]);
sns.histplot(users, x = 'user_following_count', ax = axs[1,0]);
sns.histplot(users, x = 'user_listed_on_count', ax = axs[1,1]);

fig, axs = plt.subplots(3, 1, figsize=(12, 10))

sns.histplot(users, x = 'user_tweet_count', ax = axs[0]);
sns.histplot(users, x = 'user_created_at_year', discrete = True, ax = axs[1]);
sns.histplot(users, x = 'user_created_at_month', discrete = True, ax = axs[2]);

fig, axs = plt.subplots(1, 3, figsize=(12, 8))

sns.countplot(x = 'user_has_location', data = users, ax = axs[0], palette="Set1");
sns.countplot(x = 'user_has_url', data = users, ax = axs[1], palette="Set1");
sns.countplot(x = 'user_verified', data = users, ax = axs[2], palette="Set1");

"""# Data Preprocessing

## Dealing with missing data
"""

missing_cols(users)

missing_cols(train_tweets)

train_tweets['tweet_topic_ids'].value_counts()

train_tweets['tweet_topic_ids'].mode()


train_tweets['tweet_topic_ids'].fillna(train_tweets['tweet_topic_ids'].mode()[0], inplace=True)

# train_tweets.tweet_hashtag_count.value_counts()
# train_tweets.tweet_url_count.value_counts()
# train_tweets.tweet_mention_count.value_counts()

# convert floats to ints
cols = ['tweet_hashtag_count', 'tweet_url_count', 'tweet_mention_count']
train_tweets[cols] = train_tweets[cols].applymap(np.int64)
train_tweets[cols].head()

"""## one hot encoding"""

topic_ids = (
    train_tweets['tweet_topic_ids'].str.strip('[]').str.split('\s*,\s*').explode()
    .str.get_dummies().sum(level=0).add_prefix('topic_id_')
) 
topic_ids.rename(columns = lambda x: x.replace("'", ""), inplace=True)

year = pd.get_dummies(train_tweets.tweet_created_at_year, prefix='year')
month = pd.get_dummies(train_tweets.tweet_created_at_month , prefix='month')
day = pd.get_dummies(train_tweets.tweet_created_at_day, prefix='day')
attachment = pd.get_dummies(train_tweets.tweet_attachment_class, prefix='attatchment')
language = pd.get_dummies(train_tweets.tweet_language_id, prefix='language')

## Cyclical encoding
sin_hour = np.sin(2*np.pi*train_tweets['tweet_created_at_hour']/24.0)
sin_hour.name = 'sin_hour'
cos_hour = np.cos(2*np.pi*train_tweets['tweet_created_at_hour']/24.0)
cos_hour.name = 'cos_hour'

columns_drop = [
                "tweet_topic_ids",
                "tweet_created_at_year",
                "tweet_created_at_month",
                "tweet_created_at_day",
                "tweet_attachment_class",
                "tweet_language_id",
                "tweet_created_at_hour",
               ]

dfs = [topic_ids, year, month, day, attachment, language, 
       sin_hour, cos_hour]

train_tweets_final = train_tweets.drop(columns_drop, 1).join(dfs)

train_tweets_final.head()

"""## one hot encoding on users"""

year = pd.get_dummies(users.user_created_at_year, prefix='year')
month = pd.get_dummies(users.user_created_at_month , prefix='month')
user_verified = pd.get_dummies(users.user_verified, prefix='verified')

columns_drop = [
                "user_created_at_year",
                "user_created_at_month",
                "user_verified"
              ]

dfs = [
        year,
        month,
        user_verified
      ]

users_final = users.drop(columns_drop, 1).join(dfs)

users_final.head()

"""## feature selection"""

# create new data frame that matches row number between train tweets and vectorized media
vectorized_media_df = pd.merge(train_tweets,train_tweets_vectorized_media, on ='tweet_id', how = 'right')
vectorized_media_df.drop(train_tweets.columns.difference(['virality']), axis=1, inplace=True)
vectorized_media_df.head()

vectorized_media_df.describe()

"""train_tweets_vectorized_media  """

x = vectorized_media_df.loc[:, vectorized_media_df.columns.str.contains("img_")] 
x_cols=x.columns
for i in x_cols:
    
    # fit on training data column
    scale = MinMaxScaler().fit(x[[i]])
    
    # transform the training data column
    x[i] = scale.transform(x[[i]])

x.describe()

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
y = vectorized_media_df['virality']

#apply SelectKBest class to extract top 10 best features
bestfeatures = SelectKBest(score_func=chi2, k=10)
fit = bestfeatures.fit(x,y)
dfscores = pd.DataFrame(fit.scores_)
dfcolumns = pd.DataFrame(x.columns)
#concat two dataframes for better visualization 
featureScores = pd.concat([dfcolumns,dfscores],axis=1)
featureScores.columns = ['Specs','Score']  #naming the dataframe columns
print(featureScores.nlargest(2048,'Score'))  
print(featureScores.describe())

index_names = featureScores[ featureScores['Score'] <= 11.8].index
  
featureScores.drop(index_names, inplace = True)
print(featureScores)

x = vectorized_media_df.loc[:, vectorized_media_df.columns.str.contains("img_")]
x1=x.columns
print(x1)
del_cols=[]
for i in range(0,len(x.columns)):
  if i not in featureScores['Specs']:
    del_cols.append(x1[i])
print(len(del_cols))

x.drop(del_cols,axis=1,inplace=True)

media_ind_df = pd.DataFrame(x[x.columns])
train_tweets_media_final = pd.concat([train_tweets_vectorized_media[['media_id', 'tweet_id']], media_ind_df], axis=1)
train_tweets_media_final.head()

"""train_tweets_vectorized_text  

"""

# create new data frame that matches row number between train tweets and vectorized media
vectorized_text_df = pd.merge(train_tweets,train_tweets_vectorized_text, on ='tweet_id', how = 'right')
vectorized_text_df.drop(train_tweets.columns.difference(['virality']), axis=1, inplace=True)
vectorized_text_df.head()

vectorized_text_df.describe()

x = vectorized_text_df.loc[:, train_tweets_vectorized_text.columns.str.contains("feature_")] 
x_cols=x.columns
for i in x_cols:
    
    # fit on training data column
    scale = MinMaxScaler().fit(x[[i]])
    
    # transform the training data column
    x[i] = scale.transform(x[[i]])

x.describe()

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
y = vectorized_text_df['virality']
#apply SelectKBest class to extract top 10 best features
bestfeatures = SelectKBest(score_func=chi2, k=10)
fit = bestfeatures.fit(x,y)
dfscores = pd.DataFrame(fit.scores_)
dfcolumns = pd.DataFrame(x.columns)
#concat two dataframes for better visualization 
featureScorest = pd.concat([dfcolumns,dfscores],axis=1)
featureScorest.columns = ['Specs','Score']  #naming the dataframe columns
print(featureScorest.nlargest(768,'Score'))  
print(featureScorest.describe())

index_names = featureScorest[ featureScorest['Score'] <= 6.41].index
  
featureScorest.drop(index_names, inplace = True)
print(featureScorest)

x1=x.columns
print(x1)
del_colst=[]
for i in range(0,len(x1)):
  if i not in featureScorest['Specs']:
    del_colst.append(x1[i])
print(len(del_colst))

x.drop(del_colst,axis=1,inplace=True)
x.head()



text_ind_df = pd.DataFrame(x[x.columns])
train_tweets_text_final = pd.concat([train_tweets_vectorized_text[['tweet_id']], text_ind_df], axis=1)
train_tweets_text_final.head()

# Find the median of virality for each user to reduce features for user vectorized
# description and profile
average_virality_df =train_tweets.groupby('tweet_user_id').agg(pd.Series.median)['virality']

descriptions_df = pd.merge(average_virality_df, user_vectorized_descriptions, left_on ='tweet_user_id', right_on = 'user_id', how = 'right')
profile_images_df = pd.merge(average_virality_df, user_vectorized_profile_images, left_on ='tweet_user_id', right_on = 'user_id', how = 'right')
descriptions_df.head()

profile_images_df.shape

"""user_vectorized_descriptions"""

y = descriptions_df['virality']
x = descriptions_df.loc[:, descriptions_df.columns.str.contains("feature_")] 

x_cols=x.columns
for i in x_cols:
    
    # fit on training data column
    scale = MinMaxScaler().fit(x[[i]])
    
    # transform the training data column
    x[i] = scale.transform(x[[i]])

x.describe()

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
#apply SelectKBest class to extract top 10 best features
bestfeatures = SelectKBest(score_func=chi2, k=10)
fit = bestfeatures.fit(x,y)
dfscores = pd.DataFrame(fit.scores_)
dfcolumns = pd.DataFrame(x.columns)
#concat two dataframes for better visualization 
featureScoresud = pd.concat([dfcolumns,dfscores],axis=1)
featureScoresud.columns = ['Specs','Score']  #naming the dataframe columns
print(featureScoresud.nlargest(768,'Score'))  
print(featureScoresud.describe())

index_names = featureScoresud[ featureScoresud['Score'] <= 0.3515 ].index
  
featureScoresud.drop(index_names, inplace = True)
print(featureScoresud)

x1=x.columns
print(x1)
del_colsud=[]
for i in range(0,len(x1)):
  if i not in featureScoresud['Specs']:
    del_colsud.append(x1[i])
print(len(del_colsud))

x.drop(del_colsud,axis=1,inplace=True)

desc_ind_df = pd.DataFrame(x[x.columns])
user_descriptions_final = pd.concat([user_vectorized_descriptions[['user_id']], desc_ind_df], axis=1)
user_descriptions_final.head()

"""user_vectorized_profile_images"""

y = profile_images_df['virality']
x = profile_images_df.loc[:, profile_images_df.columns.str.contains("feature_")] 
x.describe()

x_cols=x.columns
for i in x_cols:
    
    # fit on training data column
    scale = MinMaxScaler().fit(x[[i]])
    
    # transform the training data column
    x[i] = scale.transform(x[[i]])
x.describe()
x.shape

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
#apply SelectKBest class to extract top 10 best features
bestfeatures = SelectKBest(score_func=chi2, k=10)
fit = bestfeatures.fit(x,y)
dfscores = pd.DataFrame(fit.scores_)
dfcolumns = pd.DataFrame(x.columns)
#concat two dataframes for better visualization 
featureScoresup = pd.concat([dfcolumns,dfscores],axis=1)
featureScoresup.columns = ['Specs','Score']  #naming the dataframe columns
print(featureScoresup.nlargest(2048,'Score'))  
print(featureScoresup.describe())

index_names = featureScoresup[ featureScoresup['Score'] <= 3].index
  
featureScoresup.drop(index_names, inplace = True)
print(featureScoresup)

x1=x.columns
print(x1)
del_colsup=[]
for i in range(0,len(x1)):
  if i not in featureScoresup['Specs']:
    del_colsup.append(x1[i])
print(len(del_colsup))

x.drop(del_colsup,axis=1,inplace=True)

user_prof_ind_df = pd.DataFrame(x[x.columns])
user_profile_images_final = pd.concat([user_vectorized_profile_images[['user_id']], user_prof_ind_df], axis=1)
user_profile_images_final.head()

print(train_tweets_final.shape)
print(train_tweets_media_final.shape) # join on tweet id
print(train_tweets_text_final.shape) # join on tweet id
print(users_final.shape) # join on user_id
print(user_profile_images_final.shape) # join on user_id

media_df =train_tweets_media_final.groupby('tweet_id').mean()
cols = train_tweets_text_final.columns[train_tweets_text_final.columns.str.contains('feature_')]
train_tweets_text_final.rename(columns = dict(zip(cols, 'text_' + cols)), inplace=True)
train_tweets_text_final.head()

tweet_df = pd.merge(media_df, train_tweets_text_final, on = 'tweet_id', how = 'right')
tweet_df.fillna(0, inplace=True)

# join users data
user_df = pd.merge(users_final, user_profile_images_final, on='user_id')

# join tweets data on train_tweets
tweet_df_final = pd.merge(train_tweets_final, tweet_df, on = 'tweet_id')

# join that with the users data
final_df = pd.merge(tweet_df_final, user_df, left_on = 'tweet_user_id', right_on='user_id')

final_df.shape

X = final_df.drop(['virality', 'tweet_user_id', 'tweet_id', 'user_id'], axis=1)
y = final_df['virality']

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25, random_state = 0,stratify=y)
print('Training set shape ', X_train.shape)
print('Test set shape ', X_test.shape)













"""## preprocessing on test data"""

missing_cols(test_tweets)

test_tweets

#test_tweets.fillna({'tweet_topic_ids':"['0']"}, inplace=True)
test_tweets.ffill(axis=0,inplace=True)

# convert floats to ints
cols = ['tweet_hashtag_count', 'tweet_url_count', 'tweet_mention_count']
test_tweets[cols] = test_tweets[cols].applymap(np.int64)
test_tweets[cols].head()

topic_ids = (
    test_tweets['tweet_topic_ids'].str.strip('[]').str.split('\s*,\s*').explode()
    .str.get_dummies().sum(level=0).add_prefix('topic_id_')
) 
topic_ids.rename(columns = lambda x: x.replace("'", ""), inplace=True)

year = pd.get_dummies(test_tweets.tweet_created_at_year, prefix='year')
month = pd.get_dummies(test_tweets.tweet_created_at_month , prefix='month')
day = pd.get_dummies(test_tweets.tweet_created_at_day, prefix='day')
attachment = pd.get_dummies(test_tweets.tweet_attachment_class, prefix='attatchment')
language = pd.get_dummies(test_tweets.tweet_language_id, prefix='language')

## Cyclical encoding
sin_hour = np.sin(2*np.pi*test_tweets['tweet_created_at_hour']/24.0)
sin_hour.name = 'sin_hour'
cos_hour = np.cos(2*np.pi*test_tweets['tweet_created_at_hour']/24.0)
cos_hour.name = 'cos_hour'


columns_drop = [
                "tweet_topic_ids",
                "tweet_created_at_year",
                "tweet_created_at_month",
                "tweet_created_at_day",
                "tweet_attachment_class",
                "tweet_language_id",
                "tweet_created_at_hour",
              ]

dfs = [
        topic_ids,
        year,
        month,
        day,
        attachment,
        language,
        sin_hour,
        cos_hour,
      ]

test_tweets_final = test_tweets.drop(columns_drop, 1).join(dfs)

test_tweets_final.head()

"""match number of columns between test and train"""

cols_test = set(test_tweets_final.columns) - set(train_tweets_final.columns)
cols_test # train is missing these 4 columns from test

for col in cols_test:
  final_df[col] = 0

# columns missing in test from train
cols_train = set(train_tweets_final.columns) - set(test_tweets_final.columns)
cols_train.remove('virality') # remove virality from columns to add to test
len(cols_train)

for col in cols_train:
  test_tweets_final[col] = 0

test_tweets_media_final = pd.concat([test_tweets_vectorized_media[['media_id', 'tweet_id']], media_ind_df], axis=1)
test_tweets_text_final = pd.concat([test_tweets_vectorized_text[['tweet_id']], text_ind_df], axis=1)

media_df = test_tweets_media_final.groupby('tweet_id').mean()

cols = test_tweets_text_final.columns[test_tweets_text_final.columns.str.contains('feature_')]
test_tweets_text_final.rename(columns = dict(zip(cols, 'text_' + cols)), inplace=True)

# join tweets data
tweet_df = pd.merge(media_df, test_tweets_text_final, on = 'tweet_id', how = 'right')
tweet_df.fillna(0, inplace=True)

# join users data
user_df = pd.merge(users_final, user_profile_images_final, on='user_id')

# join tweets data on train_tweets
tweet_df_final = pd.merge(test_tweets_final, tweet_df, on = 'tweet_id')

# join that with the users data
p_final_df = pd.merge(tweet_df_final, user_df, left_on = 'tweet_user_id', right_on='user_id')

p_final_df.shape

final_df.shape # one more than test because of virality column

x= final_df.drop(['virality', 'tweet_user_id', 'tweet_id', 'user_id'], axis=1)
y = final_df['virality']

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size = 0.25, random_state = 0,stratify=y)
print('Training set shape ', X_train.shape)
print('Test set shape ', X_test.shape)



"""

```
# This is formatted as code
```

# Building random forest classifier
"""

rfs_model=RandomForestClassifier(n_estimators=250,random_state=42)

rfs_model.fit(X_train,y_train)

#prediction on the test dataset
y_pred_rfs=rfs_model.predict(X_test)

accuracy=accuracy_score(y_pred_rfs, y_test)
print('RFddModel accuracy score: {0:0.4f}'.format(accuracy_score(y_test, y_pred_rfs)))



# sorted(zip(clf.feature_importances_, X.columns), reverse=True)
feature_imp = pd.DataFrame(sorted(zip(rfs_model.feature_importances_,X.columns)), columns=['Value','Feature'])

plt.figure(figsize=(20, 10))
sns.barplot(x="Value", y="Feature", data=feature_imp.sort_values(by="Value", ascending=False)[:10], color='blue');

"""## Fit model to test/public data"""

X = p_final_df.drop(['tweet_user_id', 'tweet_id', 'user_id','language_26', 'topic_id_117', 'topic_id_123', 'topic_id_38'], axis=1)

solution = rfs_model.predict(X)
solution_df = pd.concat([p_final_df[['tweet_id']], pd.DataFrame(solution, columns = ['virality'])], axis=1)
solution_df.head()

solution_df.to_csv('solutionfinal.csv', index=False)
