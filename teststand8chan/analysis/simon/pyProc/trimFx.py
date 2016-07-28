

import matplotlib.pyplot as plt
import numpy as np
import os
import ROOT
import scipy.optimize as opt
import sys

def linFit(x, a,b):
    return a + x*b

rDir = "/home/simon/SoLid/P1/BristolTest/averagePeak/rootOut"
rFiles = os.listdir(rDir)
rFiles.sort()

hvList = []
HLVcomb = []
LoF = []
for fName in rFiles:
    if len(fName) < 20:
        # explude older versions of processed files
        continue
    
    LoF.append("%s/%s" %(rDir,fName))
    
    # list the available high voltages
    hv = float(fName[:5])
    if hv not in hvList:
        hvList.append(hv)
    
    # list the HV-LV combos
    if fName[:13] not in HLVcomb:
        HLVcomb.append(fName[:13])
        
'''
oDir = "/home/simon/SoLid/P1/BristolTest/averagePeak/pyproc/all"
oFiles = os.listdir(oDir)
oFiles.sort()
for fName in oFiles:
    if fName[:13] in HLVcomb:
        continue    
    hv = float(fName[:5])
    HLVcomb.append(fName[:13])
    LoF.append("%s/%s" %(oDir,fName))
    if hv not in hvList:
        hvList.append(hv)
'''    
     
ghvList = []
HVLowLim = 65.4
HVHighLim = 68.4
# check all high voltages to find the good ones,
# a good high voltage has at least 3 trim values
for hv in hvList:
    if hv < HVLowLim:
        continue
    if hv > HVHighLim:
        continue
    trimList = []
    for fName in LoF:
        sfn = fName.split("/")
        if float(sfn[-1][:5]) != hv:
            # this file does not have the HV being checked now
            continue
        
        trim = sfn[-1][11]  # determine the trim
        if trim not in trimList:
            trimList.append(trim)
            
    if len(trimList) > 2:
        ghvList.append(hv)
        
hvDict = {}
vbdDict = {}
vbdList = []
vbdeDict = {}
hvList = []
abList = []
agList = []
for hv in ghvList:
    biasDict = {}
    gainDict = {}
    biasList = []
    minB = 100
    maxB = 0
    for fName in LoF:
        sfn = fName.split("/")
        HV = float(sfn[-1][:5])
        if HV != hv:
            # only open the files that are needed
            continue
        trim = float(sfn[-1][11:15])
        bias = hv-trim
        #if bias > 66:
        #    continue
        
        rf = ROOT.TFile(fName,"read")
        for i in range(8):
            usePOint = True
            hg = rf.Get("gain_%i" %(i))
            try:
                gain = hg.GetBinContent(1)
            except ValueError:
                # the file doesn't have all histograms required
                hg.Delete()
                rf.Delete()
                break
            
            if gain > 100 or gain < 0:
                usePOint = False
                
            # special treatment for a single point
            if bias == 66 and gain < 40:
                usePOint = False
                
            hg.Delete()
            hg = rf.Get("amp_%i" %(i))
            if hg.GetMaximum() < 30:
                usePOint = False
            hg.Delete()
            
            if usePOint == True:
                if bias < minB:
                    minB = bias
                if bias > maxB:
                    maxB = bias
                if bias not in biasList:
                    biasList.append(bias)
                abList.append(bias)
                agList.append(gain)
                try:
                    biasDict[i].append(bias)
                    gainDict[i].append(gain)
                except KeyError:
                    biasDict[i] = [bias]
                    gainDict[i] = [gain]
        rf.Delete()

    nChans = 0
    # got all points for this HV,
    # now calculate trends
    for i in range(8):
        try:
            lbd = len(biasDict[i])
        except KeyError:
            continue
        dbl = []
        for b in biasDict[i]:
            if b not in dbl:
                dbl.append(b)
        if (len(dbl) > 2):
            nChans += 1
            #plt.plot(biasDict[i],gainDict[i],label="chan %i" %(i))
            
            # get the breakdown voltage
            # do an initial guess first
            xb = 0
            yb = 0
            xxb = 0
            xyb = 0
            n = len(biasDict[i])
            gel = []    # gain error list
            for j in range(n):
                x = biasDict[i][j]
                y = gainDict[i][j]
                xb += x
                yb += y
                xxb += x*x
                xyb += x*y
                
                # assume a 5pct error on the gain
                gel.append(0.05*y)
            xb /= n
            yb /= n
            xxb /= n
            xyb /= n
            beta = (xyb - xb*yb)/(xxb - xb*xb)
            alpha = yb - beta*xb
            
            # do the real fit that includes errors
            popt,pcov = opt.curve_fit(linFit, np.asarray(biasDict[i]),\
                                      np.asarray(gainDict[i]), p0=(alpha,beta),\
                                      sigma=gel, absolute_sigma=True)
            alpha = popt[0]
            beta = popt[1]
            sa = np.absolute(pcov[0][0])**0.5
            sb = np.absolute(pcov[1][1])**0.5
            sab = np.absolute(pcov[0][1])**0.5
            #print alpha,sa,beta,sb,sab
            dfda = -1/beta
            dfdb = alpha/(beta*beta)            
            
            # fill in the fitted values
            vbd = -alpha/beta
            vbde = np.sqrt(dfda*dfda*sa*sa + dfdb*dfdb*sb*sb)# + 2*dfda*dfdb*sab*sab)
            
            rcs = 0
            for j in range(len(biasDict[i])):
                x = biasDict[i][j]
                y = gainDict[i][j]
                e = gel[j]
                pg = alpha + x*beta # predicted gain
                rcs += (y - pg)*(y - pg)/(e*e)
            rcs /= len(gel) - 2
            
            # make a plot
            plt.errorbar(biasDict[i],gainDict[i],yerr=gel,\
                         fmt='o',label="datapoints")
            plt.plot([vbd,max(biasDict[i])],\
                     [0,alpha+max(biasDict[i])*beta],\
                     'r',label=r"Best fit ($\chi^2/NDF = %.2f$)" %(rcs))
            plt.errorbar([vbd],[0],xerr=[vbde],\
                         label = r'$V_{bd} = %.2f \pm %.2f V$' %(vbd,vbde))
                
            plt.xlabel("bias voltage (V)")
            plt.ylabel("gain (ADC/PA)")
            mgd = max(gainDict[i])
            plt.ylim(-0.05*mgd,1.05*mgd)
            plt.title(r'$V_{bd}$ estimate, chan %i, %.1f V HV' %(i,hv))
            plt.legend(loc='upper left')
            plt.savefig("imgs/c%i_hv%.1f.png" %(i,hv))
            plt.clf()
            
            print hv,i,vbd,"pm",vbde
            vbdList.append(vbd)
            hvList.append(hv)
            try:
                hvDict[i].append(hv)
                vbdDict[i].append(vbd)
                vbdeDict[i].append(vbde)
            except KeyError:
                hvDict[i] = [hv]
                vbdDict[i] = [vbd]
                vbdeDict[i] = [vbde]
            
                
            
    if False and nChans != 0 and len(biasList) > 2:
        plt.xlabel("bias voltage (V)")
        plt.ylabel("gain (ADC/PA)")
        plt.title("gain in channel %i" %(i))
        plt.legend(loc='upper left')
        plt.title("gain scan, high voltage = %.2f" %(hv))
        plt.xlim(minB-1,maxB+1)
        plt.savefig("imgs/trimFx_hv%.1f.png" %(hv))
    plt.clf()
 
def makeVbdVsHVplot(hvDict,vbdDict,vbdeDict,pName):    
    plt.figure(figsize=(10,8))
    hvl = []
    bvl = []
    bvel = []
    for i in range(8):
        #plt.errorbar(hvDict[i], vbdDict[i], yerr=vbdeDict[i],\
        plt.errorbar(hvDict[i], vbdDict[i],\
                     label='channel %i' %(i), linewidth=2)
        for j in range(len(hvDict[i])):
            hvl.append(hvDict[i][j])
            bvl.append(vbdDict[i][j])
            bvel.append(vbdeDict[i][j])
        
    xb = 0
    yb = 0
    xxb = 0
    xyb = 0
    n = len(hvl)
    for j in range(n):
        x = hvl[j]
        y = bvl[j]
        xb += x
        yb += y
        xxb += x*x
        xyb += x*y
    xb /= n
    yb /= n
    xxb /= n
    xyb /= n
    beta = (xyb - xb*yb)/(xxb - xb*xb)
    alpha = yb - beta*xb
    plt.plot([min(hvl),max(hvl)],[alpha + min(hvl)*beta,alpha + max(hvl)*beta],\
             'k--',linewidth=4)
    plt.text(min(hvl)+0.15,max(bvl)+0.05,r'V_{bd} = %.2f %.4f * V_{HV}' %(alpha,beta),\
             fontsize=24)    
    plt.xlabel('high voltage (V)')
    plt.ylabel('breakdown voltage (V)')
    plt.ylim(min(bvl)-0.15,max(bvl)+0.35)
    plt.xlim(min(hvl)-0.5,max(hvl)+0.5)
    plt.legend(ncol=4)
    plt.savefig('%s.png' %(pName))
    plt.clf()

# hamamatsu provided breakdown voltage
hpbdv = [64.25, 64.25, 64.3, 64.31, 64.29, 64.28, 64.3, 64.32]
bdvdDict = {}   # breakdwon voltage difference
for i in range(8):
    bdvdDict[i] = []
    for vbd in vbdDict[i]:
        bdvdDict[i].append(vbd - hpbdv[i])
        

makeVbdVsHVplot(hvDict,vbdDict,vbdeDict,'VbdVsHV_or')
makeVbdVsHVplot(hvDict,bdvdDict,vbdeDict,'VbdVsHV_cor')

sys.exit()

xb = 0
yb = 0
xxb = 0
xyb = 0
n = len(abList)
for j in range(n):
    x = abList[j]
    y = agList[j]
    xb += x
    yb += y
    xxb += x*x
    xyb += x*y
xb /= n
yb /= n
xxb /= n
xyb /= n
beta = (xyb - xb*yb)/(xxb - xb*xb)
alpha = yb - beta*xb
print "gain = %.2f + bias*%.2f" %(alpha,beta)
plt.scatter(abList,agList)
plt.plot([min(abList),max(abList)],[alpha + min(abList)*beta,alpha + max(abList)*beta])
plt.show()

d = []
for j in range(n):
    d.append(agList[j] - (alpha + beta*abList[j]))
plt.scatter(abList,d)
plt.show()

plt.hist(d,bins=100,range=(-5,5))
plt.show()