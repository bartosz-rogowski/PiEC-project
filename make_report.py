# -*- coding: utf-8-*-


'''
Project script by Bartosz Rogowski
'''

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import datetime
import os
import jinja2
from IPython.core.display import display, HTML
from pathlib import Path
import json
import seaborn
from scipy import optimize
import sys
import argparse

# -----------------------------------------

description='''This script creates report of songs' data from Spotify presented in form of graphs, bars, etc.
	Possible arguments:
		* string_1 - str, 'all' or name of decade
		* string_2 - str, 'decades' or name of decade
		- rep_name - str, name of result report (without .html extension) 
				[If not specified, then it will be named rep.html]
'''


########################################################################

def prepare_csv():
	'''
	Function that reads csv file, drops duplicates (repeating values) and formats artists columns
	returns: DataFrame object
	'''
	db = pd.read_csv('./data/new_dane.csv', encoding='utf-8', sep=';')
	db = db.drop_duplicates()
	#removing ' from artists column
	db['artists'] = db['artists'].apply(lambda x: x[1:-1].replace("'", ''))
	return db


########################################################################

def compare_decades(decade1, decade2, output_name):
	'''
	Analyses given decades, creates graphs of different categories, saves them to images and creates html page from template.
	'''

	#checking arguments
	switch_values = {
		"20s" : 1920,
		"30s" : 1930,
		"40s" : 1940,
		"50s" : 1950,
		"60s" : 1960,
		"70s" : 1970,
		"80s" : 1980,
		"90s" : 1990,
		"00s" : 2000,
		"10s" : 2010
	}

	try:
		if not (decade1 in switch_values and decade2 in switch_values):
			raise Exception("Input arguments are incorrect.")

		if(decade1 == decade2):
			raise Exception("Decades must be different to be compared to.")

	except Exception as e:
		print(e)
		print("HINT: Try two different of those:", " ".join([str(k) for k in switch_values.keys()]))
		return

	#checking whether file with given name exists already
	if(os.path.isfile(f"results/{output_name}.html")):
		yn = input("ATTENTION: File of this name already exists and it will be overwritten\nDo you want to continue? [y/n]\n")
		if(not(yn == 'y' or yn == 'Y')):
			print("Program has been stopped by the user.")
			return



	print("Preparing data, please wait...")
	baza = prepare_csv()

	q1 = baza.loc[(baza.year >= switch_values[decade1]) & (baza.year <= switch_values[decade1]+10)]
	q2 = baza.loc[(baza.year >= switch_values[decade2]) & (baza.year <= switch_values[decade2]+10)]

	categories = ['valence', 'acousticness', 'danceability','energy', 'instrumentalness', 'key', 'liveness', 'loudness', 'popularity', 'speechiness', 'tempo', 'length']

	dirname = f"{decade1}-{decade2}"

	if(not os.path.isdir("img/{dirname}")):
		try:
			os.mkdir(f"./img/{dirname}")
		except:
			yn = input("ATTENTION: Directory of this name already exists and it may contain files that will be overwritten\nDo you want to continue? [y/n]\n")
			if(not(yn == 'y' or yn == 'Y')):
				print("Program has been stopped by the user.")
				return


	print("Creating graphs, please wait...")

	for ct in range(len(categories)):
		fig, axs = plt.subplots(1, 2, figsize=(15, 4));
		axs[0].hist(q1[categories[ct]], bins=10, ec='black');
		axs[0].set_title(f"Music's {categories[ct]} histogram between {switch_values[decade1]} and {switch_values[decade1]+9}");
		axs[1].hist(q2[categories[ct]], bins=10, ec='black');
		axs[1].set_title(f"Music's {categories[ct]} histogram between {switch_values[decade2]} and {switch_values[decade2]+9}");
		plt.savefig(f'./img/{dirname}/{categories[ct]}.jpg', bbox_inches='tight', dpi=200)
		print("Image has been successfully saved to:", Path(f'./img/{dirname}/{categories[ct]}.jpg').resolve())


	#preparing explicitness graph
	percentage1 = 100*len(q1.loc[q1.explicit == 1])/len(q1)
	percentage2 = 100*len(q2.loc[q2.explicit == 1])/len(q2)
	fig1, ax1 = plt.subplots(1, 2, figsize=(15, 4))
	ax1[0].pie([percentage1, 100 - percentage1], labels=['Explicit', ''], autopct='%1.1f%%', startangle=90);
	ax1[0].axis('equal');
	ax1[0].set_title(f"Percentage of explicit songs in between {switch_values[decade1]} and {switch_values[decade1]+9}");
	ax1[1].pie([percentage2, 100 - percentage2], labels=['Explicit', ''], autopct='%1.1f%%', startangle=90);
	ax1[1].axis('equal');
	ax1[1].set_title(f"Percentage of explicit songs in between {switch_values[decade2]} and {switch_values[decade2]+9}");
	plt.savefig(f'./img/{dirname}/explicit.jpg', bbox_inches='tight', dpi=200)
	print("Image has been successfully saved to:", Path(f'./img/{dirname}/explicit.jpg').resolve())


	#preparing top 10 of decade graph
	fig, ax = plt.subplots(1, 2, figsize=(15, 4))
	t10_1 = pd.DataFrame({'Number of songs' : q1['artists'].value_counts().head(10)})
	seaborn.barplot(ax=ax[0], x=t10_1['Number of songs'], data=t10_1, y=t10_1.index, order=t10_1.sort_values('Number of songs',ascending=False).index, palette='Spectral');
	t10_2 = pd.DataFrame({'Number of songs' : q2['artists'].value_counts().head(10)})
	ax[0].set_title(f"Top 10 artists between {switch_values[decade1]} and {switch_values[decade1]+9}")
	seaborn.barplot(ax=ax[1], x=t10_2['Number of songs'], data=t10_2, y=t10_2.index, order=t10_2.sort_values('Number of songs',ascending=False).index, palette='Spectral');
	ax[1].set_title(f"Top 10 artists between {switch_values[decade2]} and {switch_values[decade2]+9}")
	plt.tight_layout()
	plt.savefig(f'./img/{dirname}/top10.jpg', bbox_inches='tight', dpi=200)
	print("Image has been successfully saved to:", Path(f'./img/{dirname}/top10.jpg').resolve())


	#preparing top 10 most popular artists of all times graph
	populars1 = pd.DataFrame(q1.groupby('artists')['popularity'].sum().sort_values(ascending=False).head(10))
	populars2 = pd.DataFrame(q2.groupby('artists')['popularity'].sum().sort_values(ascending=False).head(10))
	fig, ax = plt.subplots(1, 2, figsize=(15, 4))
	seaborn.barplot(ax=ax[0], x=populars1['popularity'], data=populars1, y=populars1.index, palette='Spectral');
	ax[0].set_title(f"Top 10 most popular artists between {switch_values[decade1]} and {switch_values[decade1]+9}")
	seaborn.barplot(ax=ax[1], x=populars2['popularity'], data=populars2, y=populars2.index, palette='Spectral');
	ax[1].set_title(f"Top 10 most popular artists between {switch_values[decade2]} and {switch_values[decade2]+9}")
	plt.tight_layout()
	plt.savefig(f'./img/{dirname}/top10popular.jpg', bbox_inches='tight', dpi=200)
	print("Image has been successfully saved to:", Path(f'./img/{dirname}/top10popular.jpg').resolve())

	print("Creating report page, please wait...")

	#saving report
	all_categories = categories
	all_categories.append("explicit")
	all_categories.append("top10")
	all_categories.append("top10popular")

	ad = './templates/'
	loader = jinja2.FileSystemLoader(ad)
	loader.list_templates()
	env = jinja2.Environment(loader = loader)
	g = []
	for ct in all_categories:
		g.append(f"../img/{dirname}/{ct}.jpg")


	tmpl = env.get_template('tpl.html')
	keys = 'date,author,country,academy,faculty'
	vals = '13/01/2021,Bartosz Rogowski,Poland,AGH,Physics and Applied Computer Science'
	infos = dict(zip(keys.split(','), vals.split(',')))
	ys = f"{switch_values[decade1]} - {switch_values[decade1]+9} in comparison to {switch_values[decade2]} - {switch_values[decade2]+9}"
	with open(f"./results/{output_name}.html", "w") as f:
		f.write(tmpl.render(years_string = ys, general=g, category = all_categories, coef_info = False, infos=infos))

	print("Report has been successfully saved to:", Path(f'./results/{output_name}.html').resolve())


###########################################################################################################

def analise_all_decades(output_name):
	'''
	Analyses all decades, creates graphs of different categories, saves them to images and creates html page from template.
	'''

	#checking whether file with given name exists already
	if(os.path.isfile(f"results/{output_name}.html")):
		yn = input("ATTENTION: File of this name already exists and it will be overwritten\nDo you want to continue? [y/n]\n")
		if(not(yn == 'y' or yn == 'Y')):
			print("Program has been stopped by the user.")
			return

	print("Preparing data, please wait...")
	baza = prepare_csv()

	rok = list(range(1921, 2021))
	categories = ['valence', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'key', 'liveness', 'loudness', 'popularity', 'speechiness', 'tempo', 'length']

	expl_no = []
	statistics = []

	#counting explicitness
	for r in rok:
		expl_no.append(100*len(baza.loc[(baza.year == r) & (baza.explicit == 1)])/len(baza.loc[baza.year == r]))


	#counting other categories means
	for ct in range(len(categories)):
		single_cat = []
		for r in rok:
			single_cat.append((baza.loc[baza.year == r])[categories[ct]].mean())
		statistics.append(single_cat)


	#creating directory that images will be saved in
	dirname = "all_decades"
	if(not os.path.isdir("img/{dirname}")):
		try:
			os.mkdir(f"./img/{dirname}")
		except:
			yn = input("ATTENTION: Directory of this name already exists and it may contain files that will be overwritten\nDo you want to continue? [y/n]\n")
			if(not(yn == 'y' or yn == 'Y')):
				print("Program has been stopped by the user.")
				return

	print("Creating graphs, please wait...")

	for ct in range(len(categories)):
		plt.figure()
		plt.plot(rok, statistics[ct]);
		plt.title(f"Average {categories[ct]} of songs")
		plt.xlabel("Year")
		plt.ylabel(categories[ct])
		plt.xlim(1920, 2021)
		plt.ylim(0.99*min(statistics[ct]), 1.01*max(statistics[ct]))
		plt.grid()
		plt.savefig(f'./img/{dirname}/{categories[ct]}.jpg', bbox_inches='tight', dpi=200)
		print("Image has been successfully saved to:", Path(f'./img/{dirname}/{categories[ct]}.jpg').resolve())


	#preparing explicitness graph
	plt.figure()
	plt.plot(rok, expl_no);
	plt.title("Percentage of explicit songs")
	plt.xlabel("Year")
	plt.ylabel("Explicitness [%]")
	plt.ylim(0, 51)
	plt.xlim(1920, 2021)
	plt.grid()
	plt.savefig(f'./img/{dirname}/explicit.jpg', bbox_inches='tight', dpi=200)
	print("Image has been successfully saved to:", Path(f'./img/{dirname}/explicit.jpg').resolve())

	#preparing top 10 of all times graph
	plt.figure()
	t10 = pd.DataFrame({'Number of songs' : baza['artists'].value_counts().head(10)})
	seaborn.barplot(x=t10['Number of songs'], data=t10, y=t10.index, order=t10.sort_values('Number of songs',ascending=False).index, palette='Spectral');
	plt.title("Top 10 artists between 1921 and 2020")
	plt.savefig(f'./img/{dirname}/top10.jpg', bbox_inches='tight', dpi=200)
	print("Image has been successfully saved to:", Path(f'./img/{dirname}/top10.jpg').resolve())

	#preparing top 10 most popular artists of all times graph
	plt.figure()
	populars = pd.DataFrame(baza.groupby('artists')['popularity'].sum().sort_values(ascending=False).head(10))
	seaborn.barplot(x=t10['Number of songs'], data=t10, y=t10.index, order=t10.sort_values('Number of songs',ascending=False).index, palette='Spectral');
	seaborn.barplot(x=populars['popularity'], data=populars, y=populars.index, palette='Spectral');
	plt.title("Top 10 most popular artists between 1921 and 2020")
	plt.savefig(f'./img/{dirname}/top10popular.jpg', bbox_inches='tight', dpi=200)
	print("Image has been successfully saved to:", Path(f'./img/{dirname}/top10popular.jpg').resolve())


	#preparing correlations chart
	plt.figure(figsize=(20, 10))
	seaborn.color_palette("hls", 18)
	seaborn.heatmap(baza.corr(), annot=True, vmax=0.9, cmap='BrBG_r');
	plt.title("Table of correlation coefficients between all categories");
	plt.savefig(f'./img/{dirname}/coefs.jpg', bbox_inches='tight', dpi=200)
	print("Image has been successfully saved to:", Path(f'./img/{dirname}/coefs.jpg').resolve())


	print("Creating report page, please wait...")

	#finding correlations that might be useful
	corrs = baza.corr().unstack()
	so = pd.DataFrame({"values":corrs.sort_values(kind="quicksort")})
	so = so.drop_duplicates()
	so = so[so.values < 1]
	minima = so[so.values < -0.7].iloc[:3]
	maxima = so[so.values > 0.7].iloc[-3:]
	texts = []
	for i in range(len(minima)):
		kategorie = minima.iloc[i].name
		texts.append(f"<b>Negative correlation</b> that equals {round(minima.iloc[i]['values'], ndigits=3)} has been detected <b>between {kategorie[0]} and {kategorie[1]}</b>.")

	for i in range(len(maxima)):
		kategorie = maxima.iloc[i].name
		texts.append(f"<b>Correlation</b> that equals {round(maxima.iloc[i]['values'], ndigits=3)} has been detected <b>between {kategorie[0]} and {kategorie[1]}</b>.")

	coef_info = '<br>'.join(texts)

	#saving report
	all_categories = categories
	all_categories.append("explicit")
	all_categories.append("top10")
	all_categories.append("top10popular")
	all_categories.append("coefs")

	ad = './templates/'
	loader = jinja2.FileSystemLoader(ad)
	loader.list_templates()
	env = jinja2.Environment(loader = loader)
	g = []
	for ct in all_categories:
		g.append(f"../img/{dirname}/{ct}.jpg")


	tmpl = env.get_template('tpl.html')
	keys = 'date,author,country,academy,faculty'
	vals = '13/01/2021,Bartosz Rogowski,Poland,AGH,Physics and Applied Computer Science'
	infos = dict(zip(keys.split(','), vals.split(',')))
	ys = "1921 and 2020"
	with open(f"./results/{output_name}.html", "w") as f:
		f.write(tmpl.render(years_string = ys, general=g, category = all_categories, coef_info = coef_info, infos=infos))

	print("Report has been successfully saved to:", Path(f'./results/{output_name}.html').resolve())

###########################################################################################################################

def parserFunction():
	parser = argparse.ArgumentParser(description)
	parser.add_argument('string_1', type=str, help=u'''Name of country''')
	parser.add_argument('string_2', type=str, help=u'''Name of country''')
	parser.add_argument('-n', '--name', type=str, help=u'''Name of output file - report (without .html extension)''', metavar='name_of_report', default='rep')

	args = parser.parse_args()
	return args





if __name__ == '__main__':

	args = parserFunction()
	if (args.string_1 == "all" and args.string_2 == "decades"):
		analise_all_decades(args.name)
	else:
		compare_decades(args.string_1, args.string_2, args.name)
