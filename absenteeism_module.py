#!/usr/bin/env python
# coding: utf-8

# In[8]:


import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin

class CustomScaler(BaseEstimator,TransformerMixin): 
    
    # init or what information we need to declare a CustomScaler object
    # and what is calculated/declared as we do
    
    def __init__(self,columns,copy=True,with_mean=True,with_std=True):
        
        # scaler is nothing but a Standard Scaler object
        self.scaler = StandardScaler(copy,with_mean,with_std)
        # with some columns 'twist'
        self.columns = columns
        self.mean_ = None
        self.var_ = None
        
    
    # the fit method, which, again based on StandardScale
    
    def fit(self, X, y=None):
        self.scaler.fit(X[self.columns], y)
        self.mean_ = np.mean(X[self.columns])
        self.var_ = np.var(X[self.columns])
        return self
    
    # the transform method which does the actual scaling

    def transform(self, X, y=None, copy=None):
        
        # record the initial order of the columns
        init_col_order = X.columns
        
        # scale all features that you chose when creating the instance of the class
        X_scaled = pd.DataFrame(self.scaler.transform(X[self.columns]), columns=self.columns)
        
        # declare a variable containing all information that was not scaled
        X_not_scaled = X.loc[:,~X.columns.isin(self.columns)]
        
        # return a data frame which contains all scaled features and all 'not scaled' features
        # use the original order (that you recorded in the beginning)
        return pd.concat([X_not_scaled, X_scaled], axis=1)[init_col_order]
    
    
class Absenteeism_model():
    def init__(self, model_file, scaler_file):
        # Read the 'model' and 'scaler' file which are saved
        with open('model', 'rb') as model_file, open('scaler', 'rb') as scaler_file:
            self.reg = pickle.read(model_file)
            self.scaler = pickle.read(scaler_file)
            self.data = None
        
    def load_and_clean_data(self, data_file):
        """Take a csv file and preprocess the data"""
        # import the data
        df = pd.read_csv(data_file,delimiter=',')
        # store the data in a new variable for later use
        self.df_with_predictions = df.copy()
        # drop the 'ID' column
        df = df.drop(['ID'], axis = 1)
        # to preserve the code we've created in the previous section, we will add a column with 'NaN' strings
        df['Absenteeism Time in Hours'] = 'NaN'

        # create a separate dataframe, containing dummy values for ALL avaiable reasons
        reason_columns = pd.get_dummies(df['Reason for Absence'], drop_first = True)
            
        # split reason_columns into 4 types
        reason_type_1 = reason_columns.loc[:,1:14].max(axis=1)
        reason_type_2 = reason_columns.loc[:,15:17].max(axis=1)
        reason_type_3 = reason_columns.loc[:,18:21].max(axis=1)
        reason_type_4 = reason_columns.loc[:,22:].max(axis=1)
            
        # to avoid multicollinearity, drop the 'Reason for Absence' column from df
        df = df.drop(['Reason for Absence'], axis = 1)
          
        # concatenate df and the 4 types of reason for absence
        df = pd.concat([df, reason_type_1, reason_type_2, reason_type_3, reason_type_4], axis = 1)
           
        # assign names to the 4 reason type columns
        # note: there is a more universal version of this code, however the following will best suit our current purposes             
        column_names = ['Date', 'Transportation Expense', 'Distance to Work', 'Age',
                           'Daily Work Load Average', 'Body Mass Index', 'Education', 'Children',
                           'Pet', 'Absenteeism Time in Hours', 'Reason_1', 'Reason_2', 'Reason_3', 'Reason_4']
        df.columns = column_names

        # re-order the columns in df
        column_names_reordered = ['Reason_1', 'Reason_2', 'Reason_3', 'Reason_4', 'Date', 'Transportation Expense', 
                                      'Distance to Work', 'Age', 'Daily Work Load Average', 'Body Mass Index', 'Education', 
                                      'Children', 'Pet', 'Absenteeism Time in Hours']
        df = df[column_names_reordered]
      
        # convert the 'Date' column into datetime
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

        # create a list with month values retrieved from the 'Date' column
        list_months = [df_reason_mod['Date'][i].month for i in range(df_reason_mod.shape[0])]

        # insert the values in a new column in df, called 'Month Value'
        df['Month Value'] = list_months

        # create a new feature called 'Day of the Week'
        df['Day of the Week'] = df['Date'].apply(lambda x: x.weekday())


        # drop the 'Date' column from df
        df = df.drop(['Date'], axis = 1)

        # re-order the columns in df
        column_names_upd = ['Reason_1', 'Reason_2', 'Reason_3', 'Reason_4', 'Month Value', 'Day of the Week',
                                'Transportation Expense', 'Distance to Work', 'Age',
                                'Daily Work Load Average', 'Body Mass Index', 'Education', 'Children',
                                'Pet', 'Absenteeism Time in Hours']
        df = df[column_names_upd]


        # map 'Education' variables; the result is a dummy
        df['Education'] = df['Education'].map({1:0, 2:1, 3:1, 4:1})

        # replace the NaN values
        df = df.fillna(value=0)

        # drop the original absenteeism time
        df = df.drop(['Absenteeism Time in Hours'],axis=1)
            
        # drop the variables we decide we don't need
        df = df.drop(['Education'],axis=1)
            
        # we have included this line of code if you want to call the 'preprocessed data'
        self.preprocessed_data = df.copy()
            
        # we need this line so we can use it in the next functions
        self.data = self.scaler.transform(df)
        
            
        def predicted_probability(self):
            if (self.data is not None):  
                pred = self.reg.predict_proba(self.data)[:,1]
                return pred
        
        def predicted_output_category(self):
            if (self.data is not None):
                pred_outputs = self.reg.predict(self.data)
                return pred_outputs
            
        def predicted_outputs(self):
            if (self.data is not None):
                self.preprocessed_data['Probability'] = self.reg.predict_proba(self.data)[:,1]
                self.preprocessed_data ['Prediction'] = self.reg.predict(self.data)
                return self.preprocessed_data
            
            
        


# In[ ]:





# In[ ]:




