# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : Marz 2021 9:00 AM
# @Author  : María Blaschke
# @File    : recipe_graps
# @Project : Recipes
# @version : 0.1
# @lSoftware: PyCharm
# input="path+file", path_out,no. Recipe
# out=df each recipe, df all recipe
from __future__ import print_function
import spacy,string
import re,sys
from io import StringIO
import pandas as pd
import pickle,string,sys
import csv


class Graphs:
    def __init__(self,file,os,n,ids):

        self.num=int(n)
        self.os=os
        self.nlp = spacy.load("en_core_web_md")
        self.hash={}
        self.sentence=""
        self.sentag=""
        self.ingr=[]
        self.data=[]
        self.ids=ids
        self.recept={}
        self.ingredient={}
        with open(file) as csvfile:
            self.df = csv.DictReader(csvfile)
            for row in self.df:
                self.recept[row["id"]]={}
                self.recept[row["id"]]["detail"]=row["n_ingredients"],row["minutes"],row["contributor_id"],row["submitted"],row["tags"]
                self.recept[row["id"]]["name"]=row["name"]
                self.recept[row["id"]]["ingredients"]=row["ingredients"]
                self.recept[row["id"]]["steps"]=row["steps"]
                self.recept[row["id"]]["description"]=row["description"]
                self.recept[row["id"]]["nsteps"]=row["n_steps"]
        csvfile.close()

    def cvs_main(self):
        csv_all =self.os+"recipe2all.csv"
        csv_columns = ["Id", "Name", "AllIngredients", "Verbs", "Steps", "Ingredient"]
        try:
            with open(csv_all, 'a') as csv2all:
                writer2all = csv.DictWriter(csv2all, fieldnames=csv_columns)
                writer2all.writeheader()
                writer2all.writerows(self.data)
        except:
            print("I/O error")

    def csv_files(self, id):
        csv_file =self.os+str(id)+ '.csv'
        csv_columns=["Id","Name","AllIngredients","Verbs","Steps","Ingredient"]
        try:
            with open(csv_file, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()

                for _id in self.hash.keys():
                    for verb in self.hash[_id]["verb"].keys():
                        for step in self.hash[_id]["verb"][verb]["step"].keys():
                            if len(self.hash[_id]["verb"][verb]["step"][step].keys()) > 0:
                                data=self.hash[_id]["verb"][verb]["step"][step]["ingredients"]

                                writer.writerow({"Id":id,"Name":self.hash[id]["Name"],"AllIngredients":self.hash[id]["Ingredients"],"Verbs":verb,"Steps":step,"Ingredient":data})
                                self.data.append({"Id": id, "Name": self.hash[id]["Name"],
                                                 "AllIngredients": self.hash[id]["Ingredients"], "Verbs": verb,
                                                 "Steps": step, "Ingredient": data})
                            else:

                                writer.writerow({"Id": id, "Name": self.hash[id]["Name"],
                                                     "AllIngredients": self.hash[id]["Ingredients"], "Verbs": verb,
                                                     "Steps": step})
                                self.data.append({"Id": id, "Name": self.hash[id]["Name"],
                                                 "AllIngredients": self.hash[id]["Ingredients"], "Verbs": verb,
                                                 "Steps": step})

        except IOError:
            print("I/O error")

    def insert(self, nodos,id):


        if nodos[0] not  in self.hash[id]["verb"]:

            self.hash[id]["verb"][nodos[0]]={}
            self.hash[id]["verb"][nodos[0]]["step"]={}
            self.hash[id]["verb"][nodos[0]]["step"][nodos[1]]={}
            self.hash[id]["verb"][nodos[0]]["step"][nodos[1]]["ingredients"] = {}
        elif nodos[1] not in self.hash[id]["verb"][nodos[0]]["step"]:
            self.hash[id]["verb"][nodos[0]]["step"][nodos[1]] = {}
            self.hash[id]["verb"][nodos[0]]["step"][nodos[1]]["ingredients"] = {}
        else:
            pass


    def design(self):

        #build graphs

        if self.num==0 or self.num=="all" and len(self.ids)==0 or self.ids=="":
            list2id=self.recept.keys()
        elif len(self.ids)>0:
                list2id=self.ids
                self.num=len(list2id)
        else:
            listid=list(self.recept.keys())
            list2id=listid[0:self.num]
        for id in list2id:

            step = self.recept[id]["steps"]
            ing = self.recept[id]["ingredients"]
            self.hash[id] = {}

            # clean noise
            ings = re.sub('[\[\'\]]', '', ing)

            for  i in ings.split(","):

                self.ingredient[i]=1
                print(i)
            # ings=''.join(i for i in ing if not i in ["\"", "'", "]["])

            step = re.sub('(\'\,)', ' | ', step)
            step = re.sub('[\[\'\]]', '', step)

            steps = ''.join(i for i in step if not i in ["\"", "'", "]["])

            self.hash[id]["verb"] = {}
            self.hash[id]["Ingredients"] = ings
            self.hash[id]["Name"] = self.recept[id]["name"]


            c = 0

            for sent in steps.split("|"):
                c += 1
                ing2list = []
                verb2list = []
                sentence = self.nlp(sent)

                for token in sentence:
                    if token.text in ["wrap"] or token.pos_ == "VERB" and re.search("(became|could| would|will|can|should)",
                                                          token.lemma_) == None and not re.search("[^a-zA-Z]",
                                                                                                  token.text):
                        verb2list.append(token.text)
                    control=0
                    if token.pos_ == "NOUN" or token.pos=="JJ":
                        aux_list=list(self.ingredient.keys())
                        for aux_text in aux_list:

                            if re.search(token.text,aux_text):

                                #self.ingr.append(token.text)
                                if aux_text not in ing2list:
                                    ing2list.append(aux_text)
                #for n in self.ingr:
                #    if re.search(n, sent):
                #        ing2list.append(n)
                for verb in verb2list:
                    self.insert([verb, c], id)

                    value = sent.find("all the ingredients")
                    col = sent.find(verb)

                    if value > 0:
                        self.hash[id]["verb"][verb]["step"][c]["ingredients"] = ings
                        # self.hash[id]["verb"][verb]["step"][c]["ingredients"][ings] = 1
                    elif col > 0 and len(ing2list) > 1:
                        # self.hash[id]["verb"][verb]["step"][c]["ingredients"]={}
                        self.hash[id]["verb"][verb]["step"][c]["ingredients"] = [",".join(ing2list)]
                    elif col > 0 and len(ing2list) == 1:
                        # self.hash[id]["verb"][verb]["step"][c]["ingredients"] = {}
                        self.hash[id]["verb"][verb]["step"][c]["ingredients"] = [ing2list[0]]

                    else:
                        pass

            self.csv_files(id)
        self.cvs_main()

if __name__ == "__main__":
    """
    fp=sys.argv[1]
    os=sys.argv[2]
    n=sys.argv[3]
    ids=sys.argv[4]
    """
    fp = "/Users/blaschkec/Project_recipes/Data/archive/FilteredRecipes.csv" #you directory
    os = "/Users/blaschkec/Project_recipes/Data/archive/dataframes/"
    n = '2'
    ids=["2592"] #Ojo es una lista de ids de recetas aqui  solo  he  porbado con una.
    Graphs(fp,os,n,ids).design()

