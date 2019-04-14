import os
import numpy as np
import math

def csvtodict(csvfile,delimit,retainquots,orient,firstrowlabel,firstcollabel): #csvfile=file path , delimit = character separating columns, retainquots = 1/0 , orient = 'col'/'row' , firstrowlabel = 1/0 , firstcollabel = 1/0
	#read in csv
	fopen = open(csvfile,'r')
	csvtxt = fopen.read()
	fopen.close()
	
	#If records are in rows
	if orient == 'row':
		#split text into individual records
		rectxtarray = csvtxt.splitlines()
		#remove header line if exists
		if firstrowlabel == 1:
			rectxtarray = rectxtarray[1:len(rectxtarray)]		
		#split record text into individual fields
		recdict = {}
		for i in rectxtarray:
			#optionally remove quotes
			if retainquots == 0:
				i = i.replace('"','')
				
			thisrec = i.split(delimit)
			if firstcollabel == 1:
				pass
			else:
				recdict[int(float(thisrec[0]))] = float(thisrec[1])
				
	elif orient == 'col':
		recdict = []		
		recdict = 'under construction'
	
	return recdict


class stevenstest:
	def __init__(self,pA,pN,nonaeroF,so2hist):
		self.pA = pA
		#self.pB = pB
		self.pN = pN
		self.nonaeroFhist = nonaeroF
		self.so2hist = so2hist
		
	def stevenseq(self,year,pB):
		aerF = ((self.pA*self.so2hist[year])*-1) - (pB*math.log((self.so2hist[year]/self.pN)+1))
		return aerF
		
	def runitB(self,pB,fitdict,nh,nhsd): #After randomly sampling A and N, need to find B param for each 0.1 increment from 0 to 1.5
		#get 1850 total net forcing
		totanthroF1850 = self.nonaeroFhist[1850] + self.stevenseq(1850,pB)*np.random.normal(nh,nhsd)
		#get 1950 total net forcing
		totanthroF1950 = self.nonaeroFhist[1950] + self.stevenseq(1950,pB)*np.random.normal(nh,nhsd)
		#get 2005 total net forcing
		totanthroF2005 = self.nonaeroFhist[2005] + self.stevenseq(2005,pB)*np.random.normal(nh,nhsd)
		
		fitdictref = round(self.stevenseq(2005,pB),2) #round to make sure 2005 forcing equals relevant fitdict ref
		#print(fitdictref)
		
		if totanthroF1950-totanthroF1850>0:
			fitdict[fitdictref][0] += 1
		else:
			fitdict[fitdictref][1] += 1
		
	def runit(self,fitdict,nh,nhsd): #After randomly sampling A and N, need to find Bparam for each 0.05 increment from 0 to 1.5
		for i in range(31):
			#find Bparam to fit total present-day aerosol forcing
			aci = (i*-0.05) - ((self.pA*self.so2hist[2005])*-1)
			logrel = math.log((self.so2hist[2005]/self.pN)+1)
			pB = (aci / logrel)*-1
			#print(self.stevenseq(2005,pB))
			self.runitB(pB,fitdict,nh,nhsd)
			
			
def runstevens(runcount,nh,nhsd):
	rootdir = 'C:/Users/paul/Documents/climate/stevens2015/'
	so2hist = csvtodict(rootdir + 'forcingsetups/so2hist-stevenssmooth.csv',';',1,'row',1,0)
	nonaeroF = csvtodict(rootdir + '/forcingsetups/wmghgs_stevens2015orig.csv',';',1,'row',1,0)
	
	fitdict = {}
	for i in range(31): #initialise lookup for 2005aerF scores
		fitdict[round(i*-0.05,2)] = [0,0]
	#print(fitdict)
	
	nogo = 0 #initialise counter for N parameters drawn <= 0
	for j in range(runcount):
		pAF = np.random.normal(0.35,0.125) #random draw of direct aerF in normal distribution
		pA = pAF / so2hist[2005] # find alpha parameter corresponding to drawn direct aerF
		pN = np.random.normal(60,15) # draw random N parameter in normal distribution
		if pN<0:
			nogo += 1
		else:
			newtest = stevenstest(pA,pN,nonaeroF,so2hist)
			newtest.runit(fitdict,nh,nhsd)
		
	print(nogo)
	
	fopen = open(rootdir + 'stevens2015NHrep-1.txt','w')
	for i in range(31):
		thisprob = round(fitdict[round(i*-0.05,2)][0]/(runcount-nogo),4)
		fopen.write(str(round(i*-0.05,2)))
		fopen.write(';')
		fopen.write(str(thisprob))
		fopen.write('\n')
	fopen.close()
	#print(fitdict)
