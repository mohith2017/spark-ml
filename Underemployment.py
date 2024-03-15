"""
title: "Underemployment"
output: html_document
date: "2023-03-23"
"""

# Data Preparation
import pandas as pd

#Paths
path_data = "../data/"
# path_csc = "../Documents/student_f/CollegeScorecard_Raw_Data_09012022/"
# path_codebook = "~/Documents/student_f/codebook/"
# path_ipums = "~/Documents/student_f/IPUMS/"

#Data setup 
acs_df = pd.read_csv("./data/usa_00007.csv")

#Assessment
# Using underemployment rate and underemployment to determine risk
working_df = acs_df.query("AGE >= 25 and AGE <= 65 and LABFORCE == 2")
print(working_df)

clean_working_df = working_df.groupby(["AGE","YEAR"])[working_df["INCTOT"] <= working_df["INCTOT"].quantile(0.9) and working_df["INCTOT"].quantile(0.1)]
print(clean_working_df)

grouped_df1 = working_df.groupby('EMPSTAT').agg(population=('EMPSTAT', 'size'))
print(grouped_df1)

filtered_df = working_df.loc[working_df['CLASSWKR'] != 0]
grouped_df2 = filtered_df.groupby(['CLASSWKR', 'EDUCD']).agg(population=('CLASSWKR', 'size'))
print(grouped_df2)

years_earning = clean_working_df.groupby('YEAR').agg(total=('INCTOT', 'sum'),mean=('INCTOT', 'mean'),median=('INCTOT', 'median'),fmedian=('FTOTINC', 'median'))

earning_conversion = years_earning.agg(year=('YEAR', 'first'),median_c=('median', lambda x: 50000/x),mean_c=('mean', lambda x: 55750.16/x),total_c=('total', lambda x: 56806565266/x),fmedian=('fmedian', lambda x: 90000/x)).assign(conv=lambda x: (x['median_c'] + x['mean_c'] + x['fmedian'])/3)

for year in range(2009, 2021):
    clean_working_df.loc[clean_working_df['YEAR'] == year, 'INCTOT'] *= earning_conversion.loc[earning_conversion['year'] == year, 'conv'].values[0]
    clean_working_df.loc[clean_working_df['YEAR'] == year, 'FTOTINC'] *= earning_conversion.loc[earning_conversion['year'] == year, 'conv'].values[0]

md_df = clean_working_df[clean_working_df['EMPSTAT'] == 1]
md_df = md_df[md_df['CLASSWKR'] == 2]
md_df = md_df.groupby(['EDUCD', 'DEGFIELD']).agg(MD_INC=('INCTOT', 'median'), MD_FT=('FTOTINC', 'median'))
print(md_df)

grouped_df = clean_working_df.loc[(clean_working_df['EMPSTAT'] == 1) & (clean_working_df['CLASSWKR'] == 2), ['EDUCD', 'DEGFIELD', 'OCC', 'IND', 'INCTOT', 'FTOTINC']].groupby(['EDUCD', 'DEGFIELD'])
clean_working_df = None
print(grouped_df)


#By occupation and Industry
grouped_df = clean_working_df.loc[(clean_working_df['EMPSTAT'] == 1) & (clean_working_df['CLASSWKR'] == 2), ['EDUCD', 'DEGFIELD', 'OCC', 'IND', 'INCTOT', 'FTOTINC']]
grouped_occ_ind = grouped_df.groupby(['OCC', 'IND']).agg(low_ed=('EDUCD', lambda x: sum(x < 101)), high_ed=('EDUCD', lambda x: sum(x >= 101)), ratio=('EDUCD', lambda x: sum(x < 101)/(sum(x < 101) + sum(x >= 101))), underemployment=('EDUCD', lambda x: 1 if sum(x < 101)/(sum(x < 101) + sum(x >= 101)) > 0.5 else 0))


#Save file
# write grouped_occ_ind to a CSV file
grouped_occ_ind.to_csv("underemployment.csv", index=False)

# write md_df to a CSV file
md_df.to_csv("degfield.csv", index=False)
