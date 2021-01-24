import os
import sys
import ROOT
import math
import datetime
import copy
from array import array
from FakeRatio_utils_2 import *

usage = "python FakeRatio_2.py [nome_dataset_come_salvato_in_samples.py] [indice, di default 0] [path_file_da_processare] local chosenTrigger"
usageCopyPaste = "python FakeRatio_2.py DataHTC_2017 7 DataHTC_2017_ntuple.root local"

chosenTrigger = "Depending on sample"
if sys.argv[5]=="Ele" or sys.argv[5]=="Mu" or sys.argv[5]=="HT": chosenTrigger = sys.argv[5]

print("Saving events with trigger: ", chosenTrigger)

if sys.argv[4] == 'remote':
    from samples import *
    Debug = False
else:
    from samples.samples import *
    Debug = True
print('Debug' , Debug)

sample = sample_dict[sys.argv[1]]
part_idx = sys.argv[2]
file_list = list(map(str, sys.argv[3].strip('[]').split(',')))
print(file_list)

MCReco = True
startTime = datetime.datetime.now()
print("Starting running at " + str(startTime))

ROOT.gROOT.SetBatch()
chain = ROOT.TChain('Events')
for infile in file_list: 
    print("Adding %s to the chain" %(infile))
    chain.Add(infile)

print(chain)
print("Number of events in chain " + str(chain.GetEntries()))
print("Number of events in tree from chain " + str((chain.GetTree()).GetEntries()))
tree = InputTree(chain)
isMC = True
if ('Data' in sample.label):
    isMC = False

MCReco = MCReco * isMC

#++++++++++++++++++++++++++++++++++
#++   branching the new trees    ++
#++++++++++++++++++++++++++++++++++
outTreeFile = ROOT.TFile(sample.label+"_part"+str(part_idx)+".root", "RECREATE") # output file

trees = []
for i in range(10):
    trees.append(None)
maxSysts = 0
addPDF = True
addQ2 = False
addTopPt = False
addVHF = False
addTTSplit = False
addTopTagging = False
addWTagging = False
addTrigSF = False
nPDF = 0

systTree = systWeights()
systTree.prepareDefault(True, addQ2, addPDF, addTopPt, addVHF, addTTSplit)
systTree.addSelection("all")
systTree.initTreesSysts(trees, outTreeFile)

systTree.setWeightName("w_nominal",1.)
systTree.setWeightName("puSF",1.)
systTree.setWeightName("puUp",1.)
systTree.setWeightName("puDown",1.)
systTree.setWeightName("lepSF",1.)
systTree.setWeightName("lepUp",1.)
systTree.setWeightName("lepDown",1.)
systTree.setWeightName("PFSF",1.)
systTree.setWeightName("PFUp",1.)
systTree.setWeightName("PFDown",1.)

#++++++++++++++++++++++++++++++++++
#++     variables to branch      ++
#++++++++++++++++++++++++++++++++++

var_list=[]

#Leptons
FakeLepton_pt               =   array.array('f', [-999.])
FakeLepton_eta              =   array.array('f', [-999.])
FakeLepton_phi              =   array.array('f', [-999.])
FakeLepton_mass             =   array.array('f', [-999.])
FakeLepton_pdgid            =   array.array('i', [-999])
FakeLepton_pfRelIso04       =   array.array('f', [-999.])
FakeLepton_isPrompt         =   array.array('f', [-999.])
FakeLepton_isTight          =   array.array('f', [-999.])
var_list.append(FakeLepton_pt)
var_list.append(FakeLepton_isPrompt)
var_list.append(FakeLepton_eta)
var_list.append(FakeLepton_phi)
var_list.append(FakeLepton_mass)
var_list.append(FakeLepton_pdgid)
var_list.append(FakeLepton_pfRelIso04)
var_list.append(FakeLepton_isTight)

FakeElectron_pt             =   array.array('f', [-999.])
FakeElectron_relIso         =   array.array('f', [-999.])
FakeElectron_eta            =   array.array('f', [-999.])
FakeElectron_phi            =   array.array('f', [-999.])
FakeElectron_mass           =   array.array('f', [-999.])
FakeElectron_pdgid          =   array.array('i', [-999])
FakeElectron_pfRelIso04     =   array.array('f', [-999.])
FakeElectron_isPrompt       =   array.array('f', [-999.])
FakeElectron_WP90           =   array.array('f', [-999.])
var_list.append(FakeElectron_pt)
var_list.append(FakeElectron_relIso)
var_list.append(FakeElectron_isPrompt)
var_list.append(FakeElectron_eta)
var_list.append(FakeElectron_phi)
var_list.append(FakeElectron_mass)
var_list.append(FakeElectron_pdgid)
var_list.append(FakeElectron_pfRelIso04)
var_list.append(FakeElectron_WP90)

FakeMuon_pt             =   array.array('f', [-999.])
FakeMuon_relIso         =   array.array('f', [-999.])
FakeMuon_eta            =   array.array('f', [-999.])
FakeMuon_phi            =   array.array('f', [-999.])
FakeMuon_mass           =   array.array('f', [-999.])
FakeMuon_pdgid          =   array.array('i', [-999])
FakeMuon_pfRelIso04     =   array.array('f', [-999.])
FakeMuon_isPrompt       =   array.array('f', [-999.])
FakeMuon_TightId        =   array.array('f', [-999.])
var_list.append(FakeMuon_pt)
var_list.append(FakeMuon_relIso)
var_list.append(FakeMuon_isPrompt)
var_list.append(FakeMuon_eta)
var_list.append(FakeMuon_phi)
var_list.append(FakeMuon_mass)
var_list.append(FakeMuon_pdgid)
var_list.append(FakeMuon_pfRelIso04)
var_list.append(FakeMuon_TightId)

FakeTau_pt                  =   array.array('f', [-999.])
FakeTau_isPrompt            =   array.array('f', [-999.])
FakeTau_eta                 =   array.array('f', [-999.])
FakeTau_phi                 =   array.array('f', [-999.])
FakeTau_charge              =   array.array('i', [-999])
FakeTau_mass                =   array.array('f', [-999.])
FakeTau_DeepTauWP           =   array.array('f', [-999.])
var_list.append(FakeTau_pt)
var_list.append(FakeTau_isPrompt)
var_list.append(FakeTau_eta)
var_list.append(FakeTau_phi)
var_list.append(FakeTau_charge)
var_list.append(FakeTau_mass)
var_list.append(FakeTau_DeepTauWP)

#mT
mT_eleMET                   =   array.array('f', [-999.])
mT_muMET                   =   array.array('f', [-999.])
mT_tauMET                   =   array.array('f', [-999.])
mT_lepMET                   =   array.array('f', [-999.])
var_list.append(mT_muMET)
var_list.append(mT_eleMET)
var_list.append(mT_tauMET)
var_list.append(mT_lepMET)

#Vetoes
Veto_LightLeptons           =   array.array('f', [-999.])
Veto_Electrons              =   array.array('f', [-999.])
Veto_Muons                  =   array.array('f', [-999.])
Veto_TauLeptons             =   array.array('f', [-999.])
Veto_TauZMass               =   array.array('f', [-999.])
var_list.append(Veto_LightLeptons)
var_list.append(Veto_Electrons)
var_list.append(Veto_Muons)
var_list.append(Veto_TauLeptons)
var_list.append(Veto_TauZMass)

#luminosity
HLT_effLumi                 =   array.array('f', [-999.])
var_list.append(HLT_effLumi)

#MET
MET_pt                      =   array.array('f', [-999.])
MET_phi                     =   array.array('f', [-999.])
var_list.append(MET_pt)
var_list.append(MET_phi)

w_PDF_all = array.array('f', [0.]*110) 
w_nominal_all = array.array('f', [0.])
#++++++++++++++++++++++++++++++++++
#++          branches            ++
#++++++++++++++++++++++++++++++++++

systTree.branchTreesSysts(trees, "all", "FakeLepton_pt",            outTreeFile, FakeLepton_pt)
systTree.branchTreesSysts(trees, "all", "FakeLepton_isPrompt",      outTreeFile, FakeLepton_isPrompt)
systTree.branchTreesSysts(trees, "all", "FakeLepton_eta",           outTreeFile, FakeLepton_eta)
systTree.branchTreesSysts(trees, "all", "FakeLepton_phi",           outTreeFile, FakeLepton_phi)
systTree.branchTreesSysts(trees, "all", "FakeLepton_mass",          outTreeFile, FakeLepton_mass)
systTree.branchTreesSysts(trees, "all", "FakeLepton_pdgid",         outTreeFile, FakeLepton_pdgid)
systTree.branchTreesSysts(trees, "all", "FakeLepton_pfRelIso04",    outTreeFile, FakeLepton_pfRelIso04)
systTree.branchTreesSysts(trees, "all", "FakeLepton_isTight",       outTreeFile, FakeLepton_isTight)

systTree.branchTreesSysts(trees, "all", "FakeElectron_pt",          outTreeFile, FakeElectron_pt)
systTree.branchTreesSysts(trees, "all", "FakeElectron_relIso",      outTreeFile, FakeElectron_relIso)
systTree.branchTreesSysts(trees, "all", "FakeElectron_isPrompt",    outTreeFile, FakeElectron_isPrompt)
systTree.branchTreesSysts(trees, "all", "FakeElectron_eta",         outTreeFile, FakeElectron_eta)
systTree.branchTreesSysts(trees, "all", "FakeElectron_phi",         outTreeFile, FakeElectron_phi)
systTree.branchTreesSysts(trees, "all", "FakeElectron_mass",        outTreeFile, FakeElectron_mass)
systTree.branchTreesSysts(trees, "all", "FakeElectron_pdgid",       outTreeFile, FakeElectron_pdgid)
systTree.branchTreesSysts(trees, "all", "FakeElectron_pfRelIso04",  outTreeFile, FakeElectron_pfRelIso04)
systTree.branchTreesSysts(trees, "all", "FakeElectron_WP90",        outTreeFile, FakeElectron_WP90)

systTree.branchTreesSysts(trees, "all", "FakeMuon_pt",              outTreeFile, FakeMuon_pt)
systTree.branchTreesSysts(trees, "all", "FakeMuon_relIso",          outTreeFile, FakeMuon_relIso)
systTree.branchTreesSysts(trees, "all", "FakeMuon_isPrompt",        outTreeFile, FakeMuon_isPrompt)
systTree.branchTreesSysts(trees, "all", "FakeMuon_eta",             outTreeFile, FakeMuon_eta)
systTree.branchTreesSysts(trees, "all", "FakeMuon_phi",             outTreeFile, FakeMuon_phi)
systTree.branchTreesSysts(trees, "all", "FakeMuon_mass",            outTreeFile, FakeMuon_mass)
systTree.branchTreesSysts(trees, "all", "FakeMuon_pdgid",           outTreeFile, FakeMuon_pdgid)
systTree.branchTreesSysts(trees, "all", "FakeMuon_pfRelIso04",      outTreeFile, FakeMuon_pfRelIso04)
systTree.branchTreesSysts(trees, "all", "FakeMuon_TightId",         outTreeFile, FakeMuon_TightId)
#lumi stuff
systTree.branchTreesSysts(trees, "all", "HLT_effLumi",              outTreeFile, HLT_effLumi)
#all taus for fake calculation
systTree.branchTreesSysts(trees, "all", "FakeTau_pt",               outTreeFile, FakeTau_pt)
systTree.branchTreesSysts(trees, "all", "FakeTau_isPrompt",         outTreeFile, FakeTau_isPrompt)
systTree.branchTreesSysts(trees, "all", "FakeTau_eta",              outTreeFile, FakeTau_eta)
systTree.branchTreesSysts(trees, "all", "FakeTau_phi",              outTreeFile, FakeTau_phi)
systTree.branchTreesSysts(trees, "all", "FakeTau_mass",             outTreeFile, FakeTau_mass)
systTree.branchTreesSysts(trees, "all", "FakeTau_DeepTauWP",        outTreeFile, FakeTau_DeepTauWP)
#Veto variables
systTree.branchTreesSysts(trees, "all", "Veto_LightLeptons",        outTreeFile, Veto_LightLeptons)
systTree.branchTreesSysts(trees, "all", "Veto_TauLeptons",          outTreeFile, Veto_TauLeptons)
systTree.branchTreesSysts(trees, "all", "Veto_TauZMass",            outTreeFile, Veto_TauZMass)
systTree.branchTreesSysts(trees, "all", "MET_pt",                   outTreeFile, MET_pt)
systTree.branchTreesSysts(trees, "all", "mT_lepMET",                outTreeFile, mT_lepMET)
systTree.branchTreesSysts(trees, "all", "mT_eleMET",                outTreeFile, mT_eleMET)
systTree.branchTreesSysts(trees, "all", "mT_muMET",                 outTreeFile, mT_muMET)
systTree.branchTreesSysts(trees, "all", "mT_tauMET",                outTreeFile, mT_tauMET)

if(isMC and addPDF):
    systTree.branchTreesSysts(trees, "all", "w_PDF", outTreeFile, w_PDF_all)

#++++++++++++++++++++++++++++++++++
#++      taking MC weights       ++
#++++++++++++++++++++++++++++++++++
print("isMC: ", isMC)
if(isMC):
    newfile = ROOT.TFile.Open(file_list[0])
    dirc = ROOT.TDirectory()
    dirc = newfile.Get("plots")
    isthere_gen = bool(dirc.GetListOfKeys().Contains("h_genweight"))
    isthere_pdf = bool(dirc.GetListOfKeys().Contains("h_PDFweight"))
    print("gen?: ", isthere_gen, " pdf?: ", isthere_pdf)

    if isthere_gen or isthere_pdf:
        if isthere_gen:
            h_genweight = ROOT.TH1F()
            h_genweight.SetNameTitle('h_genweight', 'h_genweight')
            h_genw_tmp = ROOT.TH1F(dirc.Get("h_genweight"))
            if(ROOT.TH1F(h_genweight).Integral() < 1.):
                h_genweight.SetBins(h_genw_tmp.GetXaxis().GetNbins(), h_genw_tmp.GetXaxis().GetXmin(), h_genw_tmp.GetXaxis().GetXmax())
            h_genweight.Add(h_genw_tmp)
    
        if isthere_pdf:
            h_PDFweight = ROOT.TH1F()
            h_PDFweight.SetNameTitle("h_PDFweight","h_PDFweight")
            h_pdfw_tmp = ROOT.TH1F(dirc.Get("h_PDFweight"))
            if(ROOT.TH1F(h_PDFweight).Integral() < 1.):
                h_PDFweight.SetBins(h_pdfw_tmp.GetXaxis().GetNbins(), h_pdfw_tmp.GetXaxis().GetXmin(), h_pdfw_tmp.GetXaxis().GetXmax())
            h_PDFweight.Add(h_pdfw_tmp)
        else:
            addPDF = False
    newfile.Close()

#++++++++++++++++++++++++++++++++++
#++   looping over the events    ++
#++++++++++++++++++++++++++++++++++

for i in range(tree.GetEntries()):
    
    #reinitialize all variables to -999
    for j, var in enumerate(var_list):
        if j<len(var_list):
            var_list[j][0] = -999
    
    w_nominal_all[0] = 1.

    #++++++++++++++++++++++++++++++++++
    #++        taking objects        ++
    #++++++++++++++++++++++++++++++++++
    #if Debug:
    #    if(i%1000==0): print("event n. ------ " + str(i))
    #    if i>1000000: 
    #        break
    event       = Event(tree, i)
    electrons   = Collection(event, "Electron")
    muons       = Collection(event, "Muon")
    jets        = Collection(event, "Jet")
    njets       = len(jets)
    fatjets     = Collection(event, "FatJet")
    taus        = Collection(event, "Tau")
    HT          = Object(event, "HT")
    PV          = Object(event, "PV")
    HLT         = Object(event, "HLT")
    Flag        = Object(event, 'Flag')
    met         = Object(event, "MET")
    
    genpart = None

    if isMC:
        genpart = Collection(event, "GenPart")
        if not ("WZ" in sample.label):
            LHE = Collection(event, "LHEPart")
    elif not isMC:
        if not Flag.eeBadScFilter:
            continue
    
    chain.GetEntry(i)

    year = sample.year
    if(isMC):
        runPeriod = ''
    else:
        runPeriod= sample.runP
    
    passMu, passEle, passHT, noTrigger, passMuLoose, passEleLoose = trig_map(HLT, PV, year, runPeriod)

    saveIf = False

    #trigger management
    
    if chosenTrigger == "Depending on sample" and isMC == False:
        if "Electron" in sample.dataset:
            saveIf = passEleLoose
        elif "Muon" in sample.dataset:
            saveIf = passMuLoose
        elif "JetHT" in sample.dataset:
            saveIf = passHT
    elif chosenTrigger == "Depending on sample" and isMC == True:
        saveIf = passHT    
    elif chosenTrigger == "Ele":
        saveIf = passEleLoose
    elif chosenTrigger == "Mu":
        saveIf = passMuLoose
    elif chosenTrigger == "HT":
        saveIf = passHT

    if (i+1)%10000 == 0: print ("Processing event n. " + str(i) + "------------")

    if not saveIf: continue

    if isMC:
        vTrigEle, vTrigMu, vTrigHT = trig_finder(HLT, sample.year)
        if chosenTrigger == "Ele": HLT_effLumi[0] = lumiFinder(chosenTrigger, vTrigEle)
        if chosenTrigger == "Mu":  HLT_effLumi[0] = lumiFinder(chosenTrigger, vTrigMu)
        if chosenTrigger == "HT":  HLT_effLumi[0] = lumiFinder(chosenTrigger, vTrigHT)
    
    #actually runnin'

    MET_pt[0]=met.pt
    MET_phi[0]=met.phi

    #Taus

    Veto_TauLeptons[0]  =   Veto_Tau_Leptons(taus, electrons, muons)    #1 if there's another lepton, 0 if not
    Veto_TauZMass[0]    =   Veto_Tau_ZMass(taus, electrons, muons)      #1 if there's another lepton in the Z mass range, 0 if not

    if len(taus)>0:

        mT_tauMET[0]                    =   mTlepMet(met, taus[0])
        FakeTau_pt[0]                   =   taus[0].pt
        FakeTau_eta[0]                  =   taus[0].eta
        FakeTau_phi[0]                  =   taus[0].phi
        FakeTau_mass[0]                 =   taus[0].mass
        FakeTau_charge[0]               =   taus[0].charge
        FakeTau_DeepTauWP[0]            =   taus[0].idDeepTau2017v2p1VSjet
        if isMC: 
            FakeTau_isPrompt[0]         =   taus[0].genPartFlav


    #light leptons
    
    Veto_LightLeptons[0], isEle=Veto_Light_Leptons(list(electrons), list(muons))

    if isEle:
        leptons = list(electrons)
    else:
        leptons = list(muons)
    
    if len(leptons)>0:

        lepGood=None
        if isEle:
            for ele in leptons:
                if ele.jetRelIso<1 and ele.mvaFall17V2Iso_WPL:
                    lepGood = ele
                    break
        else:
            for mu in leptons:
                if mu.pfRelIso04_all<1 and mu.looseId:
                    lepGood = mu
                    break
        
        if lepGood!=None:
            mT_lepMET[0]        =   mTlepMet(met, lepGood)
            FakeLepton_pt[0]    =   lepGood.pt
            FakeLepton_eta[0]   =   lepGood.eta
            FakeLepton_phi[0]   =   lepGood.phi
            FakeLepton_mass[0]  =   lepGood.mass
            FakeLepton_pdgid[0] =   lepGood.pdgId

            if isEle:
                FakeLepton_pfRelIso04[0]    =   lepGood.jetRelIso
            else:
                FakeLepton_pfRelIso04[0]    =   lepGood.pfRelIso04_all
            if isMC: 
                FakeLepton_isPrompt[0]      =   lepGood.genPartFlav
    
    systTree.setWeightName("w_nominal",copy.deepcopy(w_nominal_all[0]))
    systTree.fillTreesSysts(trees, "all")

outTreeFile.cd()
if(isMC):
    h_genweight.Write()
    if not ("WZ" in sample.label):
        h_PDFweight.Write()


systTree.writeTreesSysts(trees, outTreeFile)
print("Number of events in output tree " + str(trees[0].GetEntries()))

endTime = datetime.datetime.now()
print("Ending running at " + str(endTime))
