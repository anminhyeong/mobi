import pandas as pd
import argparse
import os

#read all of csv files starts with given prefix of individual person
def read_data_with_person_entity(p_name, e_name):
    prefixed = [filename for filename in os.listdir('data/original/' + p_name+'/') if filename.startswith(e_name+'-')]
    df = pd.DataFrame()
    for filename in prefixed:
        temp = pd.read_csv('data/original/' + p_name + '/' + filename)
        df = df.append(temp)
    return df

#for reading PhysicalActivityTransitionEntity and processing data
def ProcessPhysicalActivityTransition(p_name):
    prefixed = [filename for filename in os.listdir('data/original/' + p_name+'/') if filename.startswith('PhysicalActivityTransitionEntity')]
    df = pd.DataFrame()
    for filename in prefixed:
        temp = pd.read_csv('data/original/' + p_name + '/' + filename)
        temp['start_time'] = pd.to_datetime(temp['timestamp'], unit = 'ms')
        if not temp.empty:
            temp.sort_values(['timestamp', 'transitionType'], ascending = [True, False], inplace = True)
            temp.reset_index(drop = True, inplace = True)
            temp.drop('timestamp', axis = 1, inplace = True)
            if temp.loc[len(temp)-1]['transitionType'].startswith('ENTER'):
                temp.loc[len(temp)] = [temp.loc[len(temp)-1]['transitionType'].replace(r'ENTER', 'EXIT'), temp.loc[len(temp)-1]['start_time'].ceil('1d')]
            if temp.loc[0]['transitionType'].startswith('EXIT'):
                temp.loc[-1] = [temp.loc[0]['transitionType'].replace(r'EXIT', 'ENTER'), temp.loc[0]['start_time'].floor('1d')]
        else:
            temp.drop('timestamp', axis = 1, inplace = True)
        df = df.append(temp)
    df.drop_duplicates(inplace=True)
    df.sort_values(['start_time', 'transitionType'], ascending = [True, False], inplace = True)
    df['end_time'] = df['start_time'].shift(-1)
    df = df.loc[df.transitionType.str.startswith('ENTER')]
    df.transitionType = df.transitionType.str.replace(r'ENTER_', '')
    df.rename(columns = {'transitionType' : 'actionType'}, inplace = True)
    df.reset_index(drop = True, inplace = True)
    return df

#for reading AppUsageEventEntity of P0701 and processing data
def ProcessAppUsageEvent(p_name):
    df = read_data_with_person_entity(p_name, 'AppUsageEventEntity')
    df.drop_duplicates(inplace=True)
    df = df.groupby('packageName').apply(lambda x : x.fillna(x.mode().iloc[0])).reset_index(drop=True)
    df['name'].fillna(df['packageName'], inplace= True)
    df['start_time'] = pd.to_datetime(df['timestamp'], unit = 'ms')
    df.sort_values('start_time', inplace = True)
    df_back = df[df['type'] == 'MOVE_TO_BACKGROUND'][:]
    df = df[df['type'] == 'MOVE_TO_FOREGROUND'][:]
    def end_time(x):
        end = df_back[(df_back['name'] == x['name'])&(df_back['start_time']>x['start_time'])]['start_time']
        return pd.NaT if end.empty else end.iloc[0]
    df['end_time'] = df.apply(end_time, axis = 1)
    df.dropna(inplace = True)
    df.drop(['timestamp', 'type'], axis = 1, inplace = True)
    df.reset_index(drop = True, inplace = True)
    return df

def ProcessAUEwithPAT(AUE, PAT):
    def PAT_merge(x):
        temp = PAT[(PAT['start_time'] < x['end_time']) & (PAT['end_time'] > x['start_time'])].copy(deep = True)
        if temp.empty:
            return
        temp.iat[0, 1] = x['start_time']
        temp.iat[len(temp) - 1, 2] = x['end_time']
        temp['name'] = x['name']
        temp['packageName'] = x['packageName']
        temp = temp[['actionType', 'name', 'packageName', 'start_time', 'end_time']]
        return temp
    temp = pd.concat([PAT_merge(row) for _, row in AUE.iterrows()])
    return temp
    
def ProcessPersonData(p_name):
    PAT = ProcessPhysicalActivityTransition(p_name)
    AUE = ProcessAppUsageEvent(p_name)
    AUE_PAT = ProcessAUEwithPAT(AUE, PAT)
    os.makedirs('data/Processed/', exist_ok= True)
    PAT.to_csv(f'data/Processed/{p_name}_PAT.csv', index = False)
    AUE.to_csv(f'data/Processed/{p_name}_AUE.csv', index = False)
    AUE_PAT.to_csv(f'data/Processed/{p_name}_AUEwithPAT.csv', index = False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--P_name')
    args = parser.parse_args()
    if args.P_name is None:
        for folder in os.listdir('data/original/'):
            ProcessPersonData(folder)
    else:
        ProcessPersonData(args.P_name)