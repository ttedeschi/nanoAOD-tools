import ROOT
import ROOT.TMath as TMath
import math
from array import array
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object, Event
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import *
from PhysicsTools.NanoAODTools.postprocessing.framework.preskimming import preSkim
print "PhysicsTools implemented"

from preliminary_tools import *
print "Agostino's tools implemented"

from topreco import *
print "Andrea's tools implemented"


inputpath = "/eos/home-a/adeiorio/Wprime/nosynch/"
'''
inpfiles = [#"Wprime_4000_RH"
            #"Wprimetotb_M2000W20_RH_MG_1",
            #"Wprimetotb_M4000W400_RH_MG_1"
            "TT_Mtt-700to1000"
            #,"WJets"
            #,"QCD_Pt_600to800_1"
            #,"SingleMuon_Run2016G_1"
]

'''
inputpath = "/eos/home-a/apiccine/private/Wprime_BkgSample/merged/"
inpfiles = ["Wprimetotb_M4000W400_RH_TuneCP5_13TeV-madgraph-pythia8",
            "Wprimetotb_M3000W300_RH_TuneCP5_13TeV-madgraph-pythia8",
            "Wprimetotb_M2000W20_RH_TuneCP5_13TeV-madgraph-pythia8"
]

subfolds = ["Wp_m4000w400_pt350_mt500",
           #"Wp_m4000w400_pt350_mt400",
           #"Wp_m4000w400_pt350",
           "Wp_m3000w300_pt350_mt500",
           #"Wp_m3000w300_pt350_mt400",
           #"Wp_m3000w300_pt350",
           "Wp_m2000w20_pt350_mt500",
           #"Wp_m2000w20_pt350_mt400",
           #"Wp_m2000w20_pt350",
           #"TT_mtt700to1000_pt350_mt500",
           #"TT_mtt700to1000_pt350_mt400",
           #"TT_mtt700to1000_pt350",
           #"TT_mtt700to1000_pt250",
]

print "input pathed"

#ROOT.gROOT.SetStyle('Plain')
#ROOT.gStyle.SetPalette(1)   
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch()        # don't pop up canvases
ROOT.TH1.SetDefaultSumw2()
ROOT.TGaxis.SetMaxDigits(3)
print "root setted"

def genpart_filter(genparts, IdMother, flav1, flav2): #returns a collection of desired genparts (to use only for MC samples)
    return list(filter(lambda x : x.genPartIdxMother == IdMother and (abs(x.pdgId) == flav1 or abs(x.pdgId) == flav2), genparts))

def flav_filter(genparts, flav): #returns a collection of desired genparts (to use only for MC samples)
    return list(filter(lambda x : abs(x.pdgId) == flav, genparts))

def bjet_filter(jets): #returns a collection of only b-gen jets (to use only for MC samples)
    return list(filter(lambda x : x.partonFlavour == -5 or x.partonFlavour == 5, jets))

def IsMCbjet(jet): #returns a collection of only b-gen jets (to use only for MC samples)
    if jet.partonFlavour == -5 or x.partonFlavour == 5:
        return True
    else:
        return False

def nobjet_filter(jets): #returns a collection of only b-gen jets (to use only for MC samples)
    return list(filter(lambda x : not x.partonFlavour == -5 and not x.partonFlavour == 5, jets))

def sameflav_filter(jets, flav): #returns a collection of only b-gen jets (to use only for MC samples)
    return list(filter(lambda x : x.partonFlavour == flav, jets))

def Chi_TopMass(mT):
  sigma = 28.8273
  mST = 174.729
  chi = ( TMath.Power((mST-mT), 2.) ) / ( TMath.Power(sigma, 2.))
  return chi

def GetTGAEfromTE(teff, stringlabel = None):
    c1 = ROOT.TCanvas()
    teff.Draw("AP")
    c1.Pad().Update()
    tgae = ROOT.TGraphAsymmErrors()
    tgae = teff.GetPaintedGraph()
    Low = teff.GetTotalHistogram().GetXaxis().GetBinLowEdge(1)
    Nbin = teff.GetTotalHistogram().GetXaxis().GetNbins()
    High = teff.GetTotalHistogram().GetXaxis().GetBinUpEdge(Nbin)
    
    tgae.GetXaxis().Set(Nbin, Low, High)
    tgae.SetTitle(teff.GetTitle())
    tgae.SetName(teff.GetName())
        
    if stringlabel is not None:
        if len(stringlabel) != Nbin:
            print "number of strings must be equal to number of bins!"
            return None
        else:
            for i in range(Nbin):
                tgae.GetXaxis().SetBinLabel(i+1, str(stringlabel[i]))

    return tgae

def insert_char_into_string(position, char, string):
    new_string = string[:position] + str(char) + string[position:]
    return new_string

Debug = False
print Debug

#Step control booleans
HLTrig = True
LepHLTrig = False
HadHLTrig = False
AK8Reco = False
MCReco = True
DetReco = True
BTagging = False

#tresholds
miniIso_cut = 0.1
jet_ptcut = 35.
leadingjet_ptcut = 350.
mass_cut = 500.
mass_cut_inf = -100.

jetptcut_str = "JetPtCuts" + str(leadingjet_ptcut)
naeff = ["nEvents", "nEventsPrePres", "HLTrigger", "LepSel", jetptcut_str, "sublead", "chimass", "closest", "best"]

for i in range(len(inpfiles)):
    inpfile = inpfiles[i]
    subfold = subfolds[i]
    filetoopen = inputpath + inpfile
    infile = ROOT.TFile.Open(filetoopen + ".root")
    tree = InputTree(infile.Events)
    print '%s opened' %(filetoopen)
    
    #hio booking
    nbins_edges = 15
    nbins = 40
    nmin = 0
    nmax = 2400
    nbinst = 15
    nbinst = nbins
    nmint = 0
    nmint = nmin
    nmaxt = 3000
    nmaxt = nmax
    wnbins = 50
    wnmin = 0
    wnmax = 10000
    
    #edges = array('f',[0., 20., 40., 60., 80., 100., 130., 160., 190., 230., 270., 320., 360., 400., 700., 1000.])
    
    if MCReco:
        h_mclepton_pt = {'electron': ROOT.TH1F("MC_Ele_pt", "MC_Ele_pt;electron pt [GeV];Countings", nbins, nmin, nmax),
                         'muon': ROOT.TH1F("MC_Mu_pt", "MC_Mu_pt;muon pt [GeV];Countings", nbins, nmin, nmax),
                    }
        h_mclepton_pt_unHLT = copy.deepcopy(h_mclepton_pt)
        for value in h_mclepton_pt_unHLT.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = 'unHLT_' + old_title
            new_name = 'unHLT_' + old_name
            value.SetTitle(new_title)
            value.SetName(new_name)
        if HadHLTrig:
            h_mclepton_pt_hadHLT = copy.deepcopy(h_mclepton_pt)
            for value in h_mclepton_pt_hadHLT.values():
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'hadHLT_' + old_title
                new_name = 'hadHLT_' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)
        if LepHLTrig:
            h_mclepton_pt_lepHLT = copy.deepcopy(h_mclepton_pt)
            for value in h_mclepton_pt_lepHLT.values():
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'lepHLT_' + old_title
                new_name = 'lepHLT_' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)
        
        
        h_mcbjet_pt = {
            'Wbjet': ROOT.TH1F("MC_Wbjet_pt", "MC_Wbjet_pt;prompt bjet pt [GeV];Countings", nbins, nmin, nmax),
            'topbjet': ROOT.TH1F("MC_topbjet_pt", "MC_topbjet_pt;top bjet pt [GeV];Countings", nbins, nmin, nmax),
            'top': ROOT.TH1F("MC_recotop_pt", "MC_recotop_pt;recotop pt [GeV];Countings", nbins, nmin, nmax)
            }
        h_mcrecotop_mass = {
            'top': ROOT.TH1F("MC_recotop_mass", "MC_recotop_mass;recotop mass [GeV];Countings", nbins, nmin, nmax)
            }
        h_mcrecotop_mass_IsNeg = copy.deepcopy(h_mcreport_mass)
        for value in h_mcrecotop_mass_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('MC_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('MC_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)

        h_mcrecotop_vs_mcWprime_mass = ROOT.TH1F("MC_recotop_Wprime_massesratio", "MC_recotop_Wprime_massesratio;recotop mass/W' mass;Countings", 22, 0, 1.1)
        h_mcrecotop_vs_mcWprime_mass_IsNeg = copy.deepcopy(h_mcrecotop_vs_mcWprime_mass)
        for value in h_mcrecotop_vs_mcWprime_mass_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('MC_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('MC_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)

        h_mc_criteria_quant = {'deltaR': ROOT.TH1F("MC_closest_deltaR", "MC_closest_deltaR;#DeltaR;Countings", 60, 0, 3),
                               'chimass': ROOT.TH1F("MC_chimass", "MC_chimass;#Chi^{2};Countings", 100, 0, 25),
                               'sublead': ROOT.TH1F("MC_subleading_pt", "MC_subleading_pt;subleading jet pt [GeV];Countings", nbins, nmin, nmax)
            }
        h_mc_2dcriteria = {'dR_vs_chi': ROOT.TH2F("MC_deltaR_vs_chi", "MC_deltaR_vs_chi;#Chi^{2};#DeltaR", 100, 0, 25, 60, 0, 3),
                           'dR_vs_sublead': ROOT.TH2F("MC_deltaR_vs_sublead_pt", "MC_deltaR_vs_sublead_pt;subleading jet pt [GeV];#DeltaR", nbins, nmin, nmax, 60, 0, 3),
                           'chi_vs_sublead': ROOT.TH2F("MC_chi_vs_sublead_pt", "MC_chi_vs_sublead_pt;subleading jet pt [GeV];#Chi^{2}", nbins, nmin, nmax, 100, 0, 25),
        }
        h_mc_criteria_quant_IsNeg = copy.deepcopy(h_mc_criteria_quant)
        for value in h_mc_criteria_quant_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('MC_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('MC_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        h_mc_2dcriteria_IsNeg = copy.deepcopy(h_mc_criteria_quant)
        for value in h_mc_2dcriteria_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('MC_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('MC_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        
        h_mcbjet_pt_unHLT = copy.deepcopy(h_mcbjet_pt)
        for value in h_mcbjet_pt_unHLT.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = 'unHLT_' + old_title
            new_name = 'unHLT_' + old_name
            value.SetTitle(new_title)
            value.SetName(new_name)
        if HadHLTrig:
            h_mcbjet_pt_hadHLT = copy.deepcopy(h_mcbjet_pt)
            for value in h_mcbjet_pt_hadHLT.values():
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'hadHLT_' + old_title
                new_name = 'hadHLT_' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)
        if LepHLTrig:
            h_mcbjet_pt_lepHLT = copy.deepcopy(h_mcbjet_pt)
            for value in h_mcbjet_pt_lepHLT.values():
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'lepHLT_' + old_title
                new_name = 'lepHLT_' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)
            
        h_mcWprime_mass = {'gen': ROOT.TH1F("MC_GenPart_Wprime_mass", "MC_GenPart_Wprime_mas;GenPart W' mass [GeV];Countings", wnbins, wnmin, wnmax),
                           'all': ROOT.TH1F("MC_Lep_Wprime_mass", "MC_Lep_Wprime_mass;MCReco Lep W' mass [GeV];Countings", wnbins, wnmin, wnmax),
                           'ele_all': ROOT.TH1F("MC_Ele_Wprime_mass", "MC_Ele_Wprime_mass;MCReco Ele W' mass [GeV];Countings", wnbins, wnmin, wnmax),
                           'mu_all': ROOT.TH1F("MC_Mu_Wprime_mass", "MC_Mu_Wprime_mass;MCReco Mu W' mass [GeV];Countings", wnbins, wnmin, wnmax),
        }
        h_mcWprime_mass_IsNeg = copy.deepcopy(h_mcWprime_mass)
        for value in h_mcWprime_mass_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('MC_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('MC_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        h_mcWprime_mass_unHLT = copy.deepcopy(h_mcWprime_mass)
        for value in h_mcWprime_mass_unHLT.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = 'unHLT_' + old_title
            new_name = 'unHLT_' + old_name
            value.SetTitle(new_title)
            value.SetName(new_name)
        if HadHLTrig:
            h_mcWprime_mass_hadHLT = copy.deepcopy(h_mcWprime_mass)
            for value in h_mcWprime_mass_hadHLT.values():
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'hadHLT_' + old_title
                new_name = 'hadHLT_' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)
        if LepHLTrig:
            h_mcWprime_mass_lepHLT = copy.deepcopy(h_mcWprime_mass)
            for value in h_mcWprime_mass_lepHLT.values():
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'lepHLT_' + old_title
                new_name = 'lepHLT_' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)
        
        h_mcWprime_tmass = {'all': ROOT.TH1F("MC_Lep_Wprime_transverse_mass", "MC_Lep_Wprime_transverse_mass;MCReco Lep W' M_{T} [GeV];Countings", wnbins, wnmin, wnmax),
                            'ele_all': ROOT.TH1F("MC_Ele_Wprime_transverse_mass", "MC_Ele_Wprime_transverse_mass;MCReco Ele W' M_{T} [GeV];Countings", wnbins, wnmin, wnmax),
                            'mu_all': ROOT.TH1F("MC_Mu_Wprime_transverse_mass", "MC_Mu_Wprime_transverse_mass;MCReco Mu W' M_{T} [GeV];Countings", wnbins, wnmin, wnmax),
        }
        h_mcWprime_tmass_unHLT = copy.deepcopy(h_mcWprime_tmass)
        for value in h_mcWprime_tmass_unHLT.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = 'unHLT_' + old_title
            new_name = 'unHLT_' + old_name
            value.SetTitle(new_title)
            value.SetName(new_name)
        if HadHLTrig:
            h_mcWprime_tmass_hadHLT = copy.deepcopy(h_mcWprime_tmass)
            for value in h_mcWprime_tmass_hadHLT.values():
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'hadHLT_' + old_title
                new_name = 'hadHLT_' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)
        if LepHLTrig:
            h_mcWprime_tmass_lepHLT = copy.deepcopy(h_mcWprime_tmass)
            for value in h_mcWprime_tmass_lepHLT.values():
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'lepHLT_' + old_title
                new_name = 'lepHLT_' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)

        h_sameflav_bjet_deltaR = ROOT.TH1F("MC_Same_Flavour_bjet_DeltaR", "Same_Flavour_bjet_DeltaR", 100, 0, 5)

        h_mcmet_q = {'pt': ROOT.TH1F("MC_MET_pt", "MC_MET_pt;MET pt [GeV];Countings", nbins, nmin, nmax),
                     'Et': ROOT.TH1F("MC_MET_Et", "MC_MET_Et;MET Et [GeV];Countings", wnbins, wnmin, wnmax),
                     'phi': ROOT.TH1F("MC_MET_phi", "MC_MET_phi;MET phi;Countings", 50, 0, 4),
        }
        h_mcmet_q_IsNeg = copy.deepcopy(h_mcmet_q)
        for value in h_mcmet_q_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('MC_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('MC_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        h_mcmet_q_unHLT = copy.deepcopy(h_mcmet_q)
        for value in h_mcmet_q_unHLT.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = 'unHLT_' + old_title
            new_name = 'unHLT_' + old_name
            value.SetTitle(new_title)
            value.SetName(new_name)
        if HadHLTrig:
            h_mcmet_q_hadHLT = copy.deepcopy(h_mcmet_q)
            for value in h_mcmet_q_hadHLT.values():
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'hadHLT_' + old_title
                new_name = 'hadHLT_' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)
        if LepHLTrig:
            h_mcmet_q_lepHLT = copy.deepcopy(h_mcmet_q)
            for value in h_mcmet_q_lepHLT.values():
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'lepHLT_' + old_title
                new_name = 'lepHLT_' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)
        
        if AK8Reco:
            h_mcfatlepton_pt = {'electron': ROOT.TH1F("MC_fatEle_pt", "MC_fatEle_pt;fatelectron pt [GeV];Countings", nbins, nmin, nmax),
                                'muon': ROOT.TH1F("MC_fatMu_pt", "MC_fatMu_pt;fatmu pt [GeV];Countings", nbins, nmin, nmax),
            }
        
            h_mcfatbjet_pt = {'Wbjet': ROOT.TH1F("MC_Wfatbjet_pt", "MC_Wfatbjet_pt;prompt fatbjet pt [GeV];Countings", nbins, nmin, nmax),
                              'topbjet': ROOT.TH1F("MC_topfatbjet_pt", "MC_topfatbjet_pt;top fatbjet pt [GeV];Countings", nbins, nmin, nmax),
                              'top': ROOT.TH1F("MC_fattop_pt", "MC_fattop_pt;fatrecotop bjet pt [GeV];Countings", nbins, nmin, nmax)
            }

            h_mcfatWprime_mass = {'all': ROOT.TH1F("MC_Lep_fatWprime_mass", "MC_Lep_fatWprime_mass;fatMCReco Lep W' mass [GeV];Countings", wnbins, wnmin, wnmax),
                                  'ele_all': ROOT.TH1F("MC_Ele_fatWprime_mass", "MC_Ele_fatWprime_mass;fatMCReco Ele W' mass [GeV];Countings", wnbins, wnmin, wnmax),
                                  'mu_all': ROOT.TH1F("MC_Mu_fatWprime_mass", "MC_Mu_fatWprime_mass;fatMCReco Mu W' mass [GeV];Countings", wnbins, wnmin, wnmax),
            }

            h_mcfatWprime_tmass = {'all': ROOT.TH1F("MC_Lep_fatWprime_transverse_mass", "MC_Lep_fatWprime_transverse_mass;fatMCReco Lep W' M_{T} [GeV];Countings", wnbins, wnmin, wnmax),
                                   'ele_all': ROOT.TH1F("MC_Ele_fatWprime_transverse_mass", "MC_Ele_fatWprime_transverse_mass;fatMCReco Ele W' M_{T} [GeV];Countings", wnbins, wnmin, wnmax),
                                   'mu_all': ROOT.TH1F("MC_Mu_fatWprime_transverse_mass", "MC_Mu_fatWprime_transverse_mass;fatMCReco Mu W' M_{T} [GeV];Countings", wnbins, wnmin, wnmax),
            }

            h_mcfatmet_q = {'pt': ROOT.TH1F("MC_fatMET_pt", "MC_fatMET_pt;fat MET pt [GeV];Countings", nbins, nmin, nmax),
                          'Et': ROOT.TH1F("MC_fatMET_Et", "MC_fatMET_Et;fat MET Et [GeV];Countings", wnbins, wnmin, wnmax),
                          'phi': ROOT.TH1F("MC_fatMET_phi", "MC_fatMET_phi;fat MET phi;Countings", 80, 0, 4),
            }

    #DetReco histos
    if DetReco:
        h_lepton_pt = {'electron': ROOT.TH1F("DetReco_Ele_pt", "DetReco_Ele_pt;electron pt [GeV];Countings", nbins, nmin, nmax),
                       'muon': ROOT.TH1F("DetReco_Mu_pt", "DetReco_Mu_pt;muon pt [GeV];Countings", nbins, nmin, nmax),
        }
        if BTagging:
            h_lepton_pt.update({
                'electron_0btag': ROOT.TH1F("DetReco_0btag_Ele_pt", "DetReco_0btag_Ele_pt;0btagged electron pt [GeV];Countings", nbins, nmin, nmax),
                'muon_0btag': ROOT.TH1F("DetReco_0btag_Mu_pt", "DetReco_0btag_Mu_pt;0btagged muon pt [GeV];Countings", nbins, nmin, nmax),
                'electron_1btag': ROOT.TH1F("DetReco_1btag_Ele_pt", "DetReco_1btag_Ele_pt;1btagged electron pt [GeV];Countings", nbins, nmin, nmax),
                'muon_1btag': ROOT.TH1F("DetReco_1btag_Mu_pt", "DetReco_1btag_Mu_pt;1btagged muon pt [GeV];Countings", nbins, nmin, nmax),
                'electron_2btag': ROOT.TH1F("DetReco_2btag_Ele_pt", "DetReco_2btag_Ele_pt;2btagged electron pt [GeV];Countings", nbins, nmin, nmax),
                'muon_2btag': ROOT.TH1F("DetReco_2btag_Mu_pt", "DetReco_2btag_Mu_pt;2btagged muon pt [GeV];Countings", nbins, nmin, nmax),
            })
                
        h_jet_pt_sublead = {
            'Wbjet': ROOT.TH1F("DetReco_Wjet_pt", "DetReco_Wjet_pt;prompt jet pt [GeV];Countings", nbins, nmin, nmax),
            'topbjet': ROOT.TH1F("DetReco_topbjet_pt", "DetReco_topjet_pt;top jet pt [GeV];Countings", nbins, nmin, nmax),
            'top': ROOT.TH1F("DetReco_recotop_pt", "DetReco_recotop_pt;recotop pt [GeV];Countings", nbins, nmin, nmax)
        }
        h_recotop_mass_sublead = {
            'top': ROOT.TH1F("DetReco_recotop_mass", "DetReco_recotop_mass;recotop mass [GeV];Countings", nbinst, nmint, nmaxt)
            }
        if BTagging:
            h_jet_pt_sublead.update({
                'Wbjet_nobtag': ROOT.TH1F("DetReco_nobtag_Wjet_pt", "DetReco_nobtag_Wjet_pt;prompt nobtagged jet pt [GeV];Countings", nbinst, nmint, nmaxt),
                'Wbjet_btag': ROOT.TH1F("DetReco_btag_Wjet_pt", "DetReco_btag_Wjet_pt;prompt btagged jet pt [GeV];Countings", nbinst, nmint, nmaxt),
            
                'topbjet_nobtag': ROOT.TH1F("DetReco_nobtag_topjet_pt", "DetReco_nobtag_topjet_pt;top nobtagged jet pt [GeV];Countings", nbinst, nmint, nmaxt),
                'topbjet_btag': ROOT.TH1F("DetReco_btag_topjet_pt", "DetReco_btag_topjet_pt;top btagged jet pt [GeV];Countings", nbins, nmin, nmaxt),
            
                'top_nobtag': ROOT.TH1F("DetReco_nobtag_recotop_pt", "DetReco_nobtag_recotop_pt;nobtagged recotop pt [GeV];Countings", nbinst, nmint, nmaxt),
                'top_btag': ROOT.TH1F("DetReco_btag_recotop_pt", "DetReco_btag_recotop_pt;btagged recotop pt [GeV];Countings", nbinst, nmint, nmaxt)
            })
            h_recotop_mass_sublead.update({
                'top_nobtag': ROOT.TH1F("DetReco_nobtag_recotop_mass", "DetReco_nobtag_recotop_mass;nobtagged recotop mass [GeV];Countings", nbinst, nmint, nmaxt),
                'top_btag': ROOT.TH1F("DetReco_btag_recotop_mass", "DetReco_btag_recotop_mass;btagged recotop mass [GeV];Countings", nbinst, nmint, nmaxt)
            })

        h_jet_pt_closest = copy.deepcopy(h_jet_pt_sublead)
        h_recotop_mass_closest = copy.deepcopy(h_recotop_mass_sublead)
        h_recotop_mass_closest['top'].SetTitle(insert_char_into_string(len('DetReco_'), 'closest_', h_recotop_mass_sublead['top'].GetTitle()))
        h_recotop_mass_closest['top'].SetName(insert_char_into_string(len('DetReco_'), 'closest_', h_recotop_mass_sublead['top'].GetName()))
        for value in h_jet_pt_closest.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_'), 'closest_', old_title)
            new_name = insert_char_into_string(len('DetReco_'), 'closest_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        
        h_jet_pt_chi = copy.deepcopy(h_jet_pt_sublead)
        h_recotop_mass_chi = copy.deepcopy(h_recotop_mass_sublead)
        h_recotop_mass_chi['top'].SetTitle(insert_char_into_string(len('DetReco_'), 'chimass_', h_recotop_mass_sublead['top'].GetTitle()))
        h_recotop_mass_chi['top'].SetName(insert_char_into_string(len('DetReco_'), 'chimass_', h_recotop_mass_sublead['top'].GetName()))
        for value in h_jet_pt_chi.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_'), 'chimass_', old_title)
            new_name = insert_char_into_string(len('DetReco_'), 'chimass_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)

        h_jet_pt_best = copy.deepcopy(h_jet_pt_sublead)
        h_recotop_mass_best = copy.deepcopy(h_recotop_mass_sublead)
        h_recotop_mass_best['top'].SetTitle(insert_char_into_string(len('DetReco_'), 'best_', h_recotop_mass_sublead['top'].GetTitle()))
        h_recotop_mass_best['top'].SetName(insert_char_into_string(len('DetReco_'), 'best_', h_recotop_mass_sublead['top'].GetName()))

        for value in h_jet_pt_best.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_'), 'best_', old_title)
            new_name = insert_char_into_string(len('DetReco_'), 'best_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        
        h_recotop_mass_sublead['top'].SetTitle(insert_char_into_string(len('DetReco_'), 'sublead_', h_recotop_mass_sublead['top'].GetTitle()))
        h_recotop_mass_sublead['top'].SetName(insert_char_into_string(len('DetReco_'), 'sublead_', h_recotop_mass_sublead['top'].GetName()))

        for value in h_jet_pt_sublead.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_'), 'sublead_', old_title)
            new_name = insert_char_into_string(len('DetReco_'), 'sublead_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)

        h_recotop_mass_sublead_IsNeg = copy.deepcopy(h_recotop_mass_sublead_IsNeg)
        for value in h_recotop_mass_sublead_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_sublead_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('DetReco_sublead_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        h_recotop_mass_closest_IsNeg = copy.deepcopy(h_recotop_mass_closest_IsNeg)
        for value in h_recotop_mass_closest_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_closest_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('DetReco_closest_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        h_recotop_mass_chi_IsNeg = copy.deepcopy(h_recotop_mass_chi_IsNeg)
        for value in h_recotop_mass_chi_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_chi_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('DetReco_chi_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        h_recotop_mass_best_IsNeg = copy.deepcopy(h_recotop_mass_best_IsNeg)
        for value in h_recotop_mass_best_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_best_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('DetReco_best_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        
        h_recotop_vs_Wprime_mass_sublead = {'nobtag': ROOT.TH1F("DetReco_recotop_Wprime_massesratio", "DetReco_recotop_Wprime_massesratio;recotop mass/W' mass;Countings", 22, 0, 1.1)
        }
        if BTagging:
            h_recotop_vs_Wprime_mass_sublead.update({
                'tnobtag_w0btag': ROOT.TH1F("DetReco_tnobtag_w0btag_recotop_Wprime_massesratio", "DetReco_tnobtag_w0btag_recotop_Wprime_massesratio;(nobtagged top, 0btag W') recotop mass/W' mass;Countings", 22, 0, 1.1),
            })
        h_recotop_vs_Wprime_mass_closest = copy.deepcopy(h_recotop_vs_Wprime_mass_sublead)
        for value in h_recotop_vs_Wprime_mass_closest.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_'), 'closest_', old_title)
            new_name = insert_char_into_string(len('DetReco_'), 'closest_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        
        h_recotop_vs_Wprime_mass_best = copy.deepcopy(h_recotop_vs_Wprime_mass_sublead)
        for value in h_recotop_vs_Wprime_mass_best.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_'), 'best_', old_title)
            new_name = insert_char_into_string(len('DetReco_'), 'best_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        
        h_recotop_vs_Wprime_mass_chi = copy.deepcopy(h_recotop_vs_Wprime_mass_sublead)
        for value in h_recotop_vs_Wprime_mass_chi.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_'), 'chimass_', old_title)
            new_name = insert_char_into_string(len('DetReco_'), 'chimass_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        
        for value in h_recotop_vs_Wprime_mass_sublead.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_'), 'sublead_', old_title)
            new_name = insert_char_into_string(len('DetReco_'), 'sublead_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        
        h_recotop_vs_Wprime_mass_sublead_IsNeg = copy.deepcopy(h_recotop_vs_Wprime_mass_sublead_IsNeg)
        for value in h_recotop_vs_Wprime_mass_sublead_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_sublead_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('DetReco_sublead_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)

        h_recotop_vs_Wprime_mass_closest_IsNeg = copy.deepcopy(h_recotop_vs_Wprime_mass_closest_IsNeg)
        for value in h_recotop_vs_Wprime_mass_closest_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_closest_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('DetReco_closest_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)

        h_recotop_vs_Wprime_mass_chi_IsNeg = copy.deepcopy(h_recotop_vs_Wprime_mass_chi_IsNeg)
        for value in h_recotop_vs_Wprime_mass_chi_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_chi_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('DetReco_chi_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)

        h_recotop_vs_Wprime_mass_best_IsNeg = copy.deepcopy(h_recotop_vs_Wprime_mass_best_IsNeg)
        for value in h_recotop_vs_Wprime_mass_best_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_best_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('DetReco_best_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)

        h_criteria_quant = {'deltaR': ROOT.TH1F("DetReco_closest_deltaR", "DetReco_closest_deltaR;#DeltaR;Countings", 60, 0, 3),
                            'chimass': ROOT.TH1F("DetReco_chimass_chisquare", "DetReco_chimass_chisquare;#Chi^{2};Countings", 100, 0, 25),
                            'sublead': ROOT.TH1F("DetReco_sublead_subleading_pt", "DetReco_sublead_subleading_pt;subleading jet pt [GeV];Countings", nbins, nmin, nmax)
            }
        if MCReco:
            h_notmatch_criteria_quant = copy.deepcopy(h_criteria_quant)
            h_match_criteria_quant = copy.deepcopy(h_criteria_quant)
            for value in h_notmatch_criteria_quant.values():
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = insert_char_into_string(len('DetReco_'), 'notMCmatch_', old_title)
                new_name = insert_char_into_string(len('DetReco_'), 'notMCmatch_', old_name)
                value.SetTitle(new_title)
                value.SetName(new_name)
            for value in h_match_criteria_quant.values():
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = insert_char_into_string(len('DetReco_'), 'MCmatch_', old_title)
                new_name = insert_char_into_string(len('DetReco_'), 'MCmatch_', old_name)
                value.SetTitle(new_title)
                value.SetName(new_name)

        h_2dcriteria = {'dR_vs_chi': ROOT.TH2F("DetReco_deltaR_vs_chi", "DetReco_deltaR_vs_chi;#Chi^{2};#DeltaR", 100, 0, 25, 60, 0, 3),
                        'dR_vs_sublead': ROOT.TH2F("DetReco_deltaR_vs_sublead_pt", "DetReco_deltaR_vs_sublead_pt;subleading jet pt [GeV];#DeltaR", nbins, nmin, nmax, 60, 0, 3),
                        'chi_vs_sublead': ROOT.TH2F("DetReco_chi_vs_sublead_pt", "DetReco_chi_vs_sublead_pt;subleading jet pt [GeV];#Chi^{2}", nbins, nmin, nmax, 100, 0, 25),
        }
        
        if MCReco:
            h_notmatch_2dcriteria = copy.deepcopy(h_2dcriteria)
            h_match_2dcriteria = copy.deepcopy(h_2dcriteria)
            for value in h_notmatch_2dcriteria.values():
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = insert_char_into_string(len('DetReco_'), 'notMCmatch_', old_title)
                new_name = insert_char_into_string(len('DetReco_'), 'notMCmatch_', old_name)
                value.SetTitle(new_title)
                value.SetName(new_name)
            for value in h_match_2dcriteria.values():
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = insert_char_into_string(len('DetReco_'), 'MCmatch_', old_title)
                new_name = insert_char_into_string(len('DetReco_'), 'MCmatch_', old_name)
                value.SetTitle(new_title)
                value.SetName(new_name)
            
        h_Wprime_mass_sublead = {'all': ROOT.TH1F("DetReco_Lep_Wprime_mass", "DetReco_Lep_Wprime_mass;DetReco Lep W' mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'ele_all': ROOT.TH1F("DetReco_Ele_Wprime_mass", "DetReco_Ele_Wprime_mass;DetReco Ele W' mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'mu_all': ROOT.TH1F("DetReco_Mu_Wprime_mass", "DetReco_Mu_Wprime_mass;DetReco Mu W' mass [GeV];Countings", wnbins, wnmin, wnmax)
        }
        if BTagging:
            h_Wprime_mass.update({
                         'all_0btag': ROOT.TH1F("DetReco_0btag_Lep_Wprime_mass", "DetReco_0btag_Lep_Wprime_mass;DetReco 0btagged Lep W' mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'all_1btag': ROOT.TH1F("DetReco_1btag_Lep_Wprime_mass", "DetReco_1btag_Lep_Wprime_mass;DetReco 1btagged Lep W' mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'all_2btag': ROOT.TH1F("DetReco_2btag_Lep_Wprime_mass", "DetReco_2btag_Lep_Wprime_mass;DetReco 2btagged Lep W' mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'ele_all_0btag': ROOT.TH1F("DetReco_0btag_Ele_Wprime_mass", "DetReco_0btag_Ele_Wprime_mass;DetReco 0btagged Ele W' mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'ele_all_1btag': ROOT.TH1F("DetReco_1btag_Ele_Wprime_mass", "DetReco_1btag_Ele_Wprime_mass;DetReco 1btagged Ele W' mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'ele_all_2btag': ROOT.TH1F("DetReco_2btag_Ele_Wprime_mass", "DetReco_2btag_Ele_Wprime_mass;DetReco 2btagged Ele W' mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'mu_all_0btag': ROOT.TH1F("DetReco_0btag_Mu_Wprime_mass", "DetReco_0btag_Mu_Wprime_mass;DetReco 0btagged Mu W' mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'mu_all_1btag': ROOT.TH1F("DetReco_1btag_Mu_Wprime_mass", "DetReco_1btag_Mu_Wprime_mass;DetReco 1btagged Mu W' mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'mu_all_2btag': ROOT.TH1F("DetReco_2btag_Mu_Wprime_mass", "DetReco_2btag_Mu_Wprime_mass;DetReco 2btagged Mu W' mass [GeV];Countings", wnbins, wnmin, wnmax),
            })
        h_Wprime_mass_closest = copy.deepcopy(h_Wprime_mass_sublead)
        for value in h_Wprime_mass_closest.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            #new_title = 'closest_' + old_title
            #new_name = 'closest_' + old_name
            new_title = insert_char_into_string(len('DetReco_'), 'closest_', old_title)
            new_name = insert_char_into_string(len('DetReco_'), 'closest_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        h_Wprime_mass_best = copy.deepcopy(h_Wprime_mass_sublead)
        for value in h_Wprime_mass_best.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_'), 'best_', old_title)
            new_name = insert_char_into_string(len('DetReco_'), 'best_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        h_Wprime_mass_chi = copy.deepcopy(h_Wprime_mass_sublead)
        for value in h_Wprime_mass_chi.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_'), 'chimass_', old_title)
            new_name = insert_char_into_string(len('DetReco_'), 'chimass_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)
        for value in h_Wprime_mass_sublead.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_'), 'sublead_', old_title)
            new_name = insert_char_into_string(len('DetReco_'), 'sublead_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)

        h_Wprime_mass_best_IsNeg = copy.deepcopy(h_Wprime_mass_best_IsNeg)
        for value in h_Wprime_mass_best_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_best_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('DetReco_best_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)

        h_Wprime_mass_closest_IsNeg = copy.deepcopy(h_Wprime_mass_closest_IsNeg)
        for value in h_Wprime_mass_closest_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_closest_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('DetReco_closest_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)

        h_Wprime_mass_chi_IsNeg = copy.deepcopy(h_Wprime_mass_chi_IsNeg)
        for value in h_Wprime_mass_chi_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_chi_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('DetReco_chi_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)

        h_Wprime_mass_sublead_IsNeg = copy.deepcopy(h_Wprime_mass_sublead_IsNeg)
        for value in h_Wprime_mass_sublead_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_sublead_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('DetReco_sublead_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)

        '''
        h_Wprime_tmass_sublead = {'all': ROOT.TH1F("DetReco_Lep_Wprime_transverse_mass", "DetReco_Lep_Wprime_transverse_mass;DetReco Lep W' transverse mass [GeV];Countings", wnbins, wnmin, wnmax),
                          'ele_all': ROOT.TH1F("DetReco_Ele_Wprime_transverse_mass", "DetReco_Ele_Wprime_transverse_mass;DetReco Ele W' transverse mass [GeV];Countings", wnbins, wnmin, wnmax),
                          'mu_all': ROOT.TH1F("DetReco_Mu_Wprime_transverse_mass", "DetReco_Mu_Wprime_transverse_mass;DetReco Mu W' transverse mass [GeV];Countings", wnbins, wnmin, wnmax)
        }
        if BTagging:
            h_Wprime_tmass_sublead.update({
                         'all_0btag': ROOT.TH1F("DetReco_0btag_Lep_Wprime_transverse_mass", "DetReco_0btag_Lep_Wprime_transverse_mass;DetReco 0btagged Lep W' transverse mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'all_1btag': ROOT.TH1F("DetReco_1btag_Lep_transverse_Wprime_mass", "DetReco_1btag_Lep_Wprime_transverse_mass;DetReco 1btagged Lep W' transverse mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'all_2btag': ROOT.TH1F("DetReco_2btag_Lep_Wprime_transverse_mass", "DetReco_2btag_Lep_Wprime_transverse_mass;DetReco 2btagged Lep W' transverse mass [GeV];Countings", wnbins, wnmin, wnmax),
                          'ele_all_0btag': ROOT.TH1F("DetReco_0btag_Ele_Wprime_transverse_mass", "DetReco_0btag_Ele_Wprime_transverse_mass;DetReco 0btagged Ele W' transverse mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'ele_all_1btag': ROOT.TH1F("DetReco_1btag_Ele_Wprime_transverse_mass", "DetReco_1btag_Ele_Wprime_transverse_mass;DetReco 1btagged Ele W' transverse mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'ele_all_2btag': ROOT.TH1F("DetReco_2btag_Ele_Wprime_transverse_mass", "DetReco_2btag_Ele_Wprime_transverse_mass;DetReco 2btagged Ele W' transverse mass [GeV];Countings", wnbins, wnmin, wnmax),
                          'mu_all_0btag': ROOT.TH1F("DetReco_0btag_Mu_Wprime_transverse_mass", "DetReco_0btag_Mu_Wprime_transverse_mass;DetReco 0btagged Mu W' transverse mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'mu_all_1btag': ROOT.TH1F("DetReco_1btag_Mu_Wprime_transverse_mass", "DetReco_1btag_Mu_Wprime_transverse_mass;DetReco 1btagged Mu W' transverse mass [GeV];Countings", wnbins, wnmin, wnmax),
                         'mu_all_2btag': ROOT.TH1F("DetReco_2btag_Mu_Wprime_transverse_mass", "DetReco_2btag_Mu_Wprime_transverse_mass;DetReco 2btagged Mu W' transverse mass [GeV];Countings", wnbins, wnmin, wnmax),
            })
        h_Wprime_tmass_closest = copy.deepcopy(h_Wprime_tmass_sublead)
        for value in h_Wprime_tmass_closest.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = 'closest_' + old_title
            new_name = 'closest_' + old_name
            value.SetTitle(new_title)
            value.SetName(new_name)
        h_Wprime_tmass_chi = copy.deepcopy(h_Wprime_tmass_sublead)
        for value in h_Wprime_tmass_chi.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = 'chimass_' + old_title
            new_name = 'chimass_' + old_name
            value.SetTitle(new_title)
            value.SetName(new_name)
        for value in h_Wprime_tmass_sublead.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = 'sublead_' + old_title
            new_name = 'sublead_' + old_name
            value.SetTitle(new_title)
            value.SetName(new_name)
        '''
        h_met_q = {'pt': ROOT.TH1F("DetReco_MET_pt", "DetReco_MET_pt;MET pt [GeV];Countings", nbins, nmin, nmax),
                   'Et': ROOT.TH1F("DetReco_MET_Et", "DetReco_MET_Et;MET Et [GeV];Countings", wnbins, wnmin, wnmax),
                   'phi': ROOT.TH1F("DetReco_MET_phi", "DetReco_MET_phi;MET phi;Countings", 50, 0, 4),
        }
        if BTagging:
            h_met_q.update({
                'pt_0btag': ROOT.TH1F("DetReco_0btag_MET_pt", "DetReco_0btag_MET_pt;0btagged MET pt [GeV];Countings", nbins, nmin, nmax),
                'Et_0btag': ROOT.TH1F("DetReco_0btag_MET_Et", "DetReco_0btag_MET_Et;0btagged MET Et [GeV];Countings", wnbins, wnmin, wnmax),
                'phi_0btag': ROOT.TH1F("DetReco_0btag_MET_phi", "DetReco_0btag_MET_phi;0btagged MET phi;Countings", 50, 0, 4),
                'pt_1btag': ROOT.TH1F("DetReco_1btag_MET_pt", "DetReco_1btag_MET_pt;1btagged MET pt [GeV];Countings", nbins, nmin, nmax),
                'Et_1btag': ROOT.TH1F("DetReco_1btag_MET_Et", "DetReco_1btag_MET_Et;1btagged MET Et [GeV];Countings", wnbins, wnmin, wnmax),
                'phi_1btag': ROOT.TH1F("DetReco_1btag_MET_phi", "DetReco_1btag_MET_phi;1btagged MET phi;Countings", 50, 0, 4),
                'pt_2btag': ROOT.TH1F("DetReco_2btag_MET_pt", "DetReco_2btag_MET_pt;2btagged MET pt [GeV];Countings", nbins, nmin, nmax),
                'Et_2btag': ROOT.TH1F("DetReco_2btag_MET_Et", "DetReco_2btag_MET_Et;2btagged MET Et [GeV];Countings", wnbins, wnmin, wnmax),
                'phi_2btag': ROOT.TH1F("DetReco_2btag_MET_phi", "DetReco_2btag_MET_phi;2btagged MET phi;Countings", 50, 0, 4),
            })

        h_met_q_IsNeg = copy.deepcopy(h_met_q_IsNeg)
        for value in h_met_q_IsNeg.values():
            old_title = value.GetTitle()
            old_name = value.GetName()
            new_title = insert_char_into_string(len('DetReco_sublead_'), 'IsNeg_', old_title)
            new_name = insert_char_into_string(len('DetReco_sublead_'), 'IsNeg_', old_name)
            value.SetTitle(new_title)
            value.SetName(new_name)

        #histo cut_and_count
        h_countings = ROOT.TH1F("DetReco_countings", "DetReco_countings", 9, 0, 9)
        h_eff_benchmark = ROOT.TH1F("DetReco_bmeff", "DetReco_bmeff", 9, 0, 9)

        for k in range(9):
            t = k + 1
            h_eff_benchmark.GetXaxis().SetBinLabel(t, str(naeff[k]))
            h_countings.GetXaxis().SetBinLabel(t, str(naeff[k]))

    #preselection
    badflag = 0
    badevt = 0
    PreSelEvt = 0
    HLTriggered = 0
    LepTriggered = 0
    JetTriggered = 0
    MCEvents = 0
    m2bjetev = 0
    nmctruth_ev = 0
    sublead_ev = 0
    closest_ev = 0
    chimass_ev = 0
    best_ev = 0
    nentries = tree.GetEntries()
    
    if Debug:
        nentries = 5000

    print 'n entries: %i' %(nentries)
   
    for i in xrange(0, nentries):
        last = False

        if i == (nentries-1):
            last = True
            
        isEvent = True
        event = Event(tree,i)
        electrons = Collection(event, "Electron")
        muons = Collection(event, "Muon")
        jets = Collection(event, "Jet")
        fatjets = Collection(event, "FatJet")
        genfatjets = Collection(event, "GenJetAK8")
        genpart = Collection(event, "GenPart")
        PV = Object(event, "PV")
        met = Object(event, "MET")
        HLT = Object(event, "HLT")
        Flag = Object(event, 'Flag')
        #it will be an ele or a muon, use isEle and isMu to recover lepton flavour
        lepton = None
        lepton_p4 = None
        mclepton = None
        mclepton_p4 = None
        MET = {'metPx': met.pt*ROOT.TMath.Cos(met.phi),
               'metPy': met.pt*ROOT.TMath.Sin(met.phi)
           }

        #Selection booleans
        #isEleHLT, isMuHLT, isHadHLT, noHLT = trig_map(HLT)
        isPreSel = False
        isHadHLT = False
        isLepHLT = False
        isHLT = False
        isLepSel = False
        isJetSel = False

        if last:
            print 'all object extracted'

        #GenPart spectrum reco
        if MCReco:
            GenWprime_p4 = ROOT.TLorentzVector()
            Wprime = flav_filter(genpart, 34)
            
            if len(Wprime)==0 :            
                promptparts = genpart_filter(genpart, 0, 6, 5)
                promptparts_p4 = []
                for promptpart in promptparts:
                    p4 = ROOT.TLorentzVector()
                    p4.SetPtEtaPhiM(promptpart.pt, promptpart.eta, promptpart.phi, promptpart.mass)
                    promptparts_p4.append(p4)
                for promptpart in promptparts_p4:
                    GenWprime_p4 += promptpart
                    
            elif not len(Wprime)==0 :
                GenWprime_p4.SetPtEtaPhiM(Wprime[0].pt, Wprime[0].eta, Wprime[0].phi, Wprime[0].mass)
               
            h_mcWprime_mass_unHLT['gen'].Fill(GenWprime_p4.M())
        
        #RecoPart spectrum reco
        if not pass_MET(Flag):
            badflag += 1
            continue

        goodEvt, isMu, isEle = presel(PV, muons, electrons, jets)
        
        if goodEvt and isMu and isEle:
            #print str(goodEvt) + ' ' + str(isMu) + ' ' + str(isEle)
            print 'presel algo not properly working here'
            continue
        
        if not goodEvt:
            badevt += 1
            continue
        
        isPreSel = True
        PreSelEvt += 1

        goodleptons = None

        #HLTriggering + mclepton finding
        if isMu:        
            goodleptons = get_Mu(muons)
            if HLTrig and (HLT.Mu50 or HLT.TkMu50 or HLT.PFHT800 or HLT.PFHT900):
                isHLT = True
                if (HLT.Mu50 or HLT.TkMu50):
                    isLepHLT = True
                if (HLT.PFHT800 or HLT.PFHT900):
                    isHadHLT = True
            if MCReco:
                mctfound = False
                for muon in goodleptons:
                    if (muon.genPartFlav == 1 or muon.genPartFlav == 15) and not mctfound:
                        mclepton = muon
                        mctfound = True
                        if mclepton.genPartIdx == -1:
                            print 'MCTruth reconstruction not properly working - lepton step'
                            continue
    
        if isEle:
            goodleptons = get_Ele(electrons)
            if HLTrig and (HLT.Ele115_CaloIdVT_GsfTrkIdT or HLT.PFHT800 or HLT.PFHT900):
                isHLT = True
                if (HLT.Ele115_CaloIdVT_GsfTrkIdT):
                    isLepHLT = True
                if (HLT.PFHT800 or HLT.PFHT900):
                    isHadHLT = True
            if MCReco:
                mctfound = False
                for electron in goodleptons:
                    if (electron.genPartFlav == 1 or electron.genPartFlav == 15) and not mctfound:
                        mclepton = electron
                        mctfound = True
                        if mclepton.genPartIdx == -1:
                            print 'MCTruth reconstruction not properly working - lepton step'
                            continue
        
        #print 'HLTriggered'

        if MCReco and mctfound:
            MCEvents += 1

        recotop = TopUtilities()
        #MCtruth event reconstruction
        if MCReco and mclepton is not None:
            mctop_p4 = None
            IsmcNeg = False
            #QUI
            mctop_p4t = None
            mcpromptbjet_p4 = None
            mctopbjet_p4 = None
            mctopbjet_p4_pre = None
            mcpromptbjet_p4t = None
            bjetcheck = True
            bjets = bjet_filter(jets)
            nobjets = nobjet_filter(jets)

            mcfattop_p4 = None
            mcfattop_p4t = None
            mcpromptfatbjet_p4 = None
            mctopfatbjet_p4 = None
            mcpromptfatbjet_p4t = None

            if len(bjets)>2:
                bjetcheck = False
                m2bjetev += 1
        
            nmctruth_ev += 1
            mclepton_p4 = ROOT.TLorentzVector()
            mclepton_p4.SetPtEtaPhiM(mclepton.pt, mclepton.eta, mclepton.phi, mclepton.mass)
            
            MCWprime_p4 = ROOT.TLorentzVector()
            MCfatWprime_p4 = ROOT.TLorentzVector()
            
            topgot_ak4 = False
            Wpgot_ak4 = False
            topgot_ak8 = False
            Wpgot_ak8 = False

            bottjets = sameflav_filter(bjets, 5)
            abottjets = sameflav_filter(bjets, -5)
            
            samedR = []
            
            if len(bottjets)>1:
                for k in reversed(range(len(bottjets))):
                    for j in range(k):
                        samedR.append(deltaR(bottjets[k].eta, bottjets[k].phi, bottjets[j].eta, bottjets[j].phi))
                        
            if len(abottjets)>1:
                for k in reversed(range(len(abottjets))):
                    for j in range(k):
                        samedR.append(deltaR(abottjets[k].eta, abottjets[k].phi, abottjets[j].eta, abottjets[j].phi))
                        
            #AK4 RECO
            for bjet in bjets:
                bjet_p4 = ROOT.TLorentzVector()
                bjet_p4.SetPtEtaPhiM(bjet.pt, bjet.eta, bjet.phi, bjet.mass)

                if abs(bjet.partonFlavour)!=5:
                    print 'bfilter not properly working'
                    continue
                    
                blepflav = genpart[mclepton.genPartIdx].pdgId*bjet.partonFlavour
                    
                if bjet.hadronFlavour == 5:
                    if blepflav < 0 and not topgot_ak4:
                        mctopbjet_p4_pre = copy.deepcopy(bjet_p4)
                        if deltaR(bjet_p4.Eta(), bjet_p4.Phi(), mclepton_p4.Eta(), mclepton_p4.Phi()) < 0.4:
                            bjet_p4 -= mclepton_p4
                        mctopbjet_p4 = bjet_p4
                        mctop_p4, ismcNeg = recotop.top4Momentum(mclepton_p4, bjet_p4, MET['metPx'], MET['metPy'])
                        if mctop_p4 is None:
                            continue
                        mclepton_p4t = copy.deepcopy(mclepton_p4)
                        mclepton_p4t.SetPz(0.)
                        bjet_p4t = copy.deepcopy(bjet_p4)
                        bjet_p4t.SetPz(0.)
                        met_p4t = ROOT.TLorentzVector()
                        met_p4t.SetPtEtaPhiM(met.pt, 0., met.phi, 0)
                        mctop_p4t = mclepton_p4t + bjet_p4t + met_p4t
                        if mctop_p4t.Pz() !=0:
                            print 'p3'
                            mctop_p4t.SetPz(0.)
                        topgot_ak4 = True
                    elif blepflav > 0 and not Wpgot_ak4:
                        mcpromptbjet_p4 = bjet_p4
                        mcpromptbjet_p4t = copy.deepcopy(bjet_p4)
                        mcpromptbjet_p4t.SetPz(0.)
                        Wpgot_ak4 = True

            if topgot_ak4 and Wpgot_ak4:
                MCWprime_p4 = mctop_p4 + mcpromptbjet_p4
                MCWprime_p4t = mctop_p4t + mcpromptbjet_p4t
                if mass_cut_inf < mctop_p4.M() < mass_cut :
                    h_mcWprime_mass_unHLT['gen'].Fill(GenWprime_p4.M())
                    h_mcbjet_pt_unHLT['topbjet'].Fill(mctopbjet_p4.Pt())
                    h_mcbjet_pt_unHLT['Wbjet'].Fill(mcpromptbjet_p4.Pt())
                    h_mcbjet_pt_unHLT['top'].Fill(mctop_p4.Pt())
                    h_mcmet_q_unHLT['pt'].Fill(met.pt)
                    h_mcmet_q_unHLT['Et'].Fill(met.sumEt)
                    h_mcmet_q_unHLT['phi'].Fill(met.phi)
                    if isHLT:
                        mcdR = deltaR(mctopbjet_p4.Eta(), mctopbjet_p4.Phi(), mclepton_p4.Eta(), mclepton_p4.Phi())
                        h_mc_criteria_quant['deltaR'].Fill(mcdR)
                        h_mc_criteria_quant['chimass'].Fill(Chi_TopMass(mctop_p4.M()))
                        h_mc_criteria_quant['sublead'].Fill(mctopbjet_p4.Pt())
                        h_mc_2dcriteria['dR_vs_chi'].Fill(Chi_TopMass(mctop_p4.M()), mcdR)
                        h_mc_2dcriteria['dR_vs_sublead'].Fill(mcpromptbjet_p4.Pt(), mcdR)
                        h_mc_2dcriteria['chi_vs_sublead'].Fill(mcpromptbjet_p4.Pt(), Chi_TopMass(mctop_p4.M()))
                        h_mcWprime_mass['gen'].Fill(GenWprime_p4.M())
                        h_mcbjet_pt['topbjet'].Fill(mctopbjet_p4.Pt())
                        h_mcbjet_pt['Wbjet'].Fill(mcpromptbjet_p4.Pt())
                        h_mcbjet_pt['top'].Fill(mctop_p4.Pt())
                        h_mcrecotop_mass['top'].Fill(mctop_p4.M())
                        h_mcmet_q['pt'].Fill(met.pt)
                        h_mcmet_q['Et'].Fill(met.sumEt)
                        h_mcmet_q['phi'].Fill(met.phi)
                    if isLepHLT and LepHLTrig:
                        h_mcWprime_mass_lepHLT['gen'].Fill(GenWprime_p4.M())
                        h_mcbjet_pt_lepHLT['topbjet'].Fill(mctopbjet_p4.Pt())
                        h_mcbjet_pt_lepHLT['Wbjet'].Fill(mcpromptbjet_p4.Pt())
                        h_mcbjet_pt_lepHLT['top'].Fill(mctop_p4.Pt())
                        h_mcmet_q_lepHLT['pt'].Fill(met.pt)
                        h_mcmet_q_lepHLT['Et'].Fill(met.sumEt)
                        h_mcmet_q_lepHLT['phi'].Fill(met.phi)
                    if isHadHLT and HadHLTrig:
                        h_mcWprime_mass_hadHLT['gen'].Fill(GenWprime_p4.M())
                        h_mcbjet_pt_hadHLT['topbjet'].Fill(mctopbjet_p4.Pt())
                        h_mcbjet_pt_hadHLT['Wbjet'].Fill(mcpromptbjet_p4.Pt())
                        h_mcbjet_pt_hadHLT['top'].Fill(mctop_p4.Pt())
                        h_mcmet_q_hadHLT['pt'].Fill(met.pt)
                        h_mcmet_q_hadHLT['Et'].Fill(met.sumEt)
                        h_mcmet_q_hadHLT['phi'].Fill(met.phi)
                    for dR in samedR:
                        h_sameflav_bjet_deltaR.Fill(dR)
                    
                    h_mcWprime_mass_unHLT['all'].Fill(MCWprime_p4.M())
                    h_mcWprime_tmass_unHLT['all'].Fill(MCWprime_p4t.M())
                    if isEle:
                        h_mcWprime_mass_unHLT['ele_all'].Fill(MCWprime_p4.M())
                        h_mcWprime_tmass_unHLT['ele_all'].Fill(MCWprime_p4t.M())
                        h_mclepton_pt_unHLT['electron'].Fill(mclepton.pt)
                    elif isMu:
                        h_mcWprime_mass_unHLT['mu_all'].Fill(MCWprime_p4.M())
                        h_mcWprime_tmass_unHLT['mu_all'].Fill(MCWprime_p4t.M())
                        h_mclepton_pt_unHLT['muon'].Fill(mclepton.pt)

                    if isHLT:
                        h_mcrecotop_vs_mcWprime_mass.Fill(mctop_p4.M()/MCWprime_p4.M())
                        h_mcWprime_mass['all'].Fill(MCWprime_p4.M())
                        h_mcWprime_tmass['all'].Fill(MCWprime_p4t.M())
                        if isEle:
                            h_mcWprime_mass['ele_all'].Fill(MCWprime_p4.M())
                            h_mcWprime_tmass['ele_all'].Fill(MCWprime_p4t.M())
                            h_mclepton_pt['electron'].Fill(mclepton.pt)
                        elif isMu:
                            h_mcWprime_mass['mu_all'].Fill(MCWprime_p4.M())
                            h_mcWprime_tmass['mu_all'].Fill(MCWprime_p4t.M())
                            h_mclepton_pt['muon'].Fill(mclepton.pt)
                    if isLepHLT and LepHLTrig:
                        h_mcWprime_mass_lepHLT['all'].Fill(MCWprime_p4.M())
                        h_mcWprime_tmass_lepHLT['all'].Fill(MCWprime_p4t.M())
                        if isEle:
                            h_mcWprime_mass_lepHLT['ele_all'].Fill(MCWprime_p4.M())
                            h_mcWprime_tmass_lepHLT['ele_all'].Fill(MCWprime_p4t.M())
                            h_mclepton_pt_lepHLT['electron'].Fill(mclepton.pt)
                        elif isMu:
                            h_mcWprime_mass_lepHLT['mu_all'].Fill(MCWprime_p4.M())
                            h_mcWprime_tmass_lepHLT['mu_all'].Fill(MCWprime_p4t.M())
                            h_mclepton_pt_lepHLT['muon'].Fill(mclepton.pt)
                    if isHadHLT and HadHLTrig:
                        h_mcWprime_mass_hadHLT['all'].Fill(MCWprime_p4.M())
                        h_mcWprime_tmass_hadHLT['all'].Fill(MCWprime_p4t.M())
                        if isEle:
                            h_mcWprime_mass_hadHLT['ele_all'].Fill(MCWprime_p4.M())
                            h_mcWprime_tmass_hadHLT['ele_all'].Fill(MCWprime_p4t.M())
                            h_mclepton_pt_hadHLT['electron'].Fill(mclepton.pt)
                        elif isMu:
                            h_mcWprime_mass_hadHLT['mu_all'].Fill(MCWprime_p4.M())
                            h_mcWprime_tmass_hadHLT['mu_all'].Fill(MCWprime_p4t.M())
                            h_mclepton_pt_hadHLT['muon'].Fill(mclepton.pt)
                    
            #AK8 RECO
            if AK8Reco and isHLT:
                genfatbjets = bjet_filter(genfatjets)
                
                for genfatbjet in genfatbjets:
                    matched = False
                    index = -1
                    idx = 0
                    for fatjet in fatjets:
                        if matched:
                            continue
                        else:
                            index += 1
                            if deltaR(genfatbjet.eta, genfatbjet.phi, fatjet.eta, fatjet.phi) < 0.8:
                                matched = True
                    if index < 0:
                        continue
                            
                    fatbjet_p4 = ROOT.TLorentzVector()
                    if fatjets[idx].msoftdrop < 0:
                        fatbjet_p4.SetPtEtaPhiM(fatjets[idx].pt, fatjets[idx].eta, fatjets[idx].phi, fatjets[idx].mass)
                    else:
                        fatbjet_p4.SetPtEtaPhiM(fatjets[idx].pt, fatjets[idx].eta, fatjets[idx].phi, fatjets[idx].msoftdrop)
                
                    blepflav = genpart[mclepton.genPartIdx].pdgId*genfatbjet.partonFlavour                    
                    if genfatbjet.hadronFlavour == 5:
                        if blepflav < 0 and not topgot_ak8:
                            mcfattop_p4, isfatNeg = recotop.top4Momentum(mclepton_p4, fatbjet_p4, MET['metPx'], MET['metPy'])
                            if mcfattop_p4 is None:
                                continue
                            mclepton_p4t = copy.deepcopy(mclepton_p4)
                            mclepton_p4t.SetPz(0.)
                            mctopfatbjet_p4 = fatbjet_p4
                            fatbjet_p4t = copy.deepcopy(fatbjet_p4)
                            fatbjet_p4t.SetPz(0.)
                            met_p4t = ROOT.TLorentzVector()
                            met_p4t.SetPtEtaPhiM(met.pt, 0., met.phi, 0)
                            mcfattop_p4t = mclepton_p4t + fatbjet_p4t + met_p4t
                            if mcfattop_p4t.Pz() !=0:
                                print 'p3'
                                mcfattop_p4t.SetPz(0.)
                            topgot_ak8 = True
                        elif blepflav > 0 and not Wpgot_ak8:
                            mcpromptfatbjet_p4 = fatbjet_p4
                            mcpromptfatbjet_p4t = copy.deepcopy(fatbjet_p4)
                            mcpromptfatbjet_p4t.SetPz(0.)
                            Wpgot_ak8 = True
            
                if topgot_ak8 and Wpgot_ak8:
                    MCfatWprime_p4 = mcfattop_p4 + mcpromptfatbjet_p4
                    MCfatWprime_p4t = mcfattop_p4t + mcpromptfatbjet_p4t
                    if True:
                        h_mcfatbjet_pt['topbjet'].Fill(mctopfatbjet_p4.Pt())
                        h_mcfatbjet_pt['Wbjet'].Fill(mcpromptfatbjet_p4.Pt())
                        h_mcfatbjet_pt['top'].Fill(mcfattop_p4.Pt())
                        h_mcfatmet_q['pt'].Fill(met.pt)
                        h_mcfatmet_q['Et'].Fill(met.sumEt)
                        h_mcfatmet_q['phi'].Fill(met.phi)
                        
                        h_mcfatWprime_mass['all'].Fill(MCfatWprime_p4.M())
                        h_mcfatWprime_tmass['all'].Fill(MCfatWprime_p4t.M())
                        if isEle:
                            h_mcfatWprime_mass['ele_all'].Fill(MCfatWprime_p4.M())
                            h_mcfatWprime_tmass['ele_all'].Fill(MCfatWprime_p4t.M())
                            h_mcfatlepton_pt['electron'].Fill(mclepton.pt)
                        elif isMu:
                            h_mcfatWprime_mass['mu_all'].Fill(MCfatWprime_p4.M())
                            h_mcfatWprime_tmass['mu_all'].Fill(MCfatWprime_p4t.M())
                            h_mcfatlepton_pt['muon'].Fill(mclepton.pt)
                    
        if not DetReco:
            continue
        #LepTriggering
        if isHLT:
            HLTriggered += 1
        else:
            continue

        if len(goodleptons) > 0:
            isLepSel = True
            selleptons = list(filter(lambda x : x.miniPFRelIso_all < miniIso_cut, goodleptons))
            if len(selleptons) < 1:
                continue
            LepTriggered += 1
            sellepton = selleptons[0]
        else:
            continue

        #JetTriggering
        goodjets = get_Jet(jets, jet_ptcut)
        if len(goodjets) < 2:
            continue
        if len(goodjets) == 1:
            print "only 1 goodjet!"
       
        #Reconstruction with detected particles
        highptjets = get_Jet(goodjets, leadingjet_ptcut)
        if len(highptjets) < 1:
            continue
        else:
            JetTriggered += 1

        isJetSel = True
        closest_promptjet = None
        closest_jet_p4 = None
        closest_jet_p4_pre = None
        chi_promptjet = None
        chi_jet_p4 = None
        chi_jet_p4_pre = None
        sublead_promptjet = highptjets[0]
        sublead_jet_p4 = None
        sublead_jet_p4_pre = None
        best_promptjet = None
        best_jet_p4 = None
        DeltaR_nujet = 100.
        DeltaR_Idx = 0
        tm_chi = 1000.
        tm_Idx = 0
        mtop_p4 = None

        closestTrig = False
        chiTrig = False
        subleadTrig = False
        bestTrig = False

        for k in range(len(goodjets)):
            '''
            if abs(dPhi) < DeltaR_nujet:
                DeltaR_nujet = dPhi
                DeltaR_Idx = k
            '''

            mtop_p4, isdetrecoNeg = recotop.top4Momentum(sellepton.p4(), goodjets[k].p4(), MET['metPx'], MET['metPy'])
            if mtop_p4 is None:
                continue
            chi = Chi_TopMass(mtop_p4.M())
            if chi < tm_chi:
                tm_chi = chi
                tm_Idx = k
            
        #jet closest to MET p4
        closest_jet, detrecodR = closest(sellepton, goodjets)
        closest_jet_p4_pre = closest_jet.p4()
        if deltaR(closest_jet.eta, closest_jet.phi, sellepton.eta, sellepton.phi) < 0.4:
            closest_jet_p4 = closest_jet_p4_pre - sellepton.p4()
        else:
            closest_jet_p4 = closest_jet_p4_pre
        if closest_jet == goodjets[0]:
            if len(highptjets) > 1:
                closest_promptjet = highptjets[1]
            else:
                closest_promptjet = goodjets[1]
        else:
            closest_promptjet = highptjets[0]
        closest_recotop_p4, IsNeg_closest = recotop.top4Momentum(sellepton.p4(), closest_jet_p4, MET['metPx'], MET['metPy'])
            
        #jet reconstructing top with the least chi2 p4
        chi_jet_p4_pre = goodjets[tm_Idx].p4()
        if deltaR(chi_jet_p4_pre.Eta(), chi_jet_p4_pre.Phi(), sellepton.eta, sellepton.phi) < 0.4:
            chi_jet_p4 = chi_jet_p4_pre - sellepton.p4()
        else:
            chi_jet_p4 = chi_jet_p4_pre
        if tm_Idx == 0:
            if len(highptjets) > 1:
                chi_promptjet = highptjets[1]
            else:
                chi_promptjet = goodjets[1]
        else:
            chi_promptjet = highptjets[0]
        chi_recotop_p4, IsNeg_chi = recotop.top4Momentum(sellepton.p4(), chi_jet_p4, MET['metPx'], MET['metPy'])
        
        #subleading jet reconstruction
        if len(highptjets) > 1:
            sublead_jet_p4_pre = highptjets[1].p4()
        else:
            sublead_jet_p4_pre = goodjets[1].p4()
        if deltaR(sublead_jet_p4_pre.Eta(), sublead_jet_p4_pre.Phi(), sellepton.eta, sellepton.phi) < 0.4:
            sublead_jet_p4 = sublead_jet_p4_pre - sellepton.p4()
        else:
            sublead_jet_p4 = sublead_jet_p4_pre
        sublead_recotop_p4, IsNeg_sublead = recotop.top4Momentum(sellepton.p4(), sublead_jet_p4, MET['metPx'], MET['metPy'])

        if not (sublead_recotop_p4 is None):
            if mass_cut_inf < sublead_recotop_p4.M() < mass_cut:#sublead_Wprime_p4.M() > mass_cut:
                subleadTrig = True
     
        if not (closest_recotop_p4 is None):
            if mass_cut_inf < closest_recotop_p4.M() < mass_cut:#_Wprime_p4.M() > mass_cut:
                closestTrig = True

        if not (chi_recotop_p4 is None):
            if mass_cut_inf < chi_recotop_p4.M() < mass_cut:#_Wprime_p4.M() > mass_cut:
                chiTrig = True

        #best jet reconstruction
        BestFound = False
        best_recotop_p4 = None
        IsNeg_best = None
        if sublead_jet_p4_pre == closest_jet_p4_pre:
            best_jet_p4 = sublead_jet_p4
            best_promptjet = sublead_promptjet
            BestFound = True
        elif sublead_jet_p4_pre == chi_jet_p4_pre:
            best_jet_p4 = sublead_jet_p4
            best_promptjet = sublead_promptjet
            BestFound = True
        elif chi_jet_p4_pre == closest_jet_p4_pre:
            best_jet_p4 = chi_jet_p4
            best_promptjet = chi_promptjet
            BestFound = True

        if not BestFound:
            if subleadTrig:
                best_jet_p4 = sublead_jet_p4
                best_promptjet = sublead_promptjet
                BestFound = True
            elif chiTrig:
                best_jet_p4 = chi_jet_p4
                best_promptjet = chi_promptjet
                BestFound = True
            elif closestTrig:
                best_jet_p4 = closest_jet_p4
                best_promptjet = closest_promptjet
                BestFound = True

        if BestFound:
            best_recotop_p4, IsNeg_best = recotop.top4Momentum(sellepton.p4(), best_jet_p4, MET['metPx'], MET['metPy'])

        if not (best_recotop_p4 is None):
            if mass_cut_inf < best_recotop_p4.M() < mass_cut:#_Wprime_p4.M() > mass_cut:
                bestTrig = True

        #Wprime reco
        if closestTrig:
            closest_Wprime_p4 = closest_recotop_p4 + closest_promptjet.p4()
        if chiTrig:
            chi_Wprime_p4 = chi_recotop_p4 + chi_promptjet.p4()
        if subleadTrig:
            sublead_Wprime_p4 = sublead_recotop_p4 + sublead_promptjet.p4()
        best_Wprime_p4 = None
        if bestTrig:
            best_Wprime_p4 = best_recotop_p4 + best_promptjet.p4()

        if not (sublead_recotop_p4 is None):
            h_criteria_quant['sublead'].Fill(sublead_jet_p4.Pt())
            if not (closest_recotop_p4 is None):
                h_2dcriteria['dR_vs_sublead'].Fill(sublead_jet_p4.Pt(), detrecodR)
            if not (chi_recotop_p4 is None):
                h_2dcriteria['chi_vs_sublead'].Fill(sublead_jet_p4.Pt(), tm_chi)
        if not (closest_recotop_p4 is None):
            h_criteria_quant['deltaR'].Fill(detrecodR)
        if not (chi_recotop_p4 is None):
            h_criteria_quant['chimass'].Fill(tm_chi)
            if not (closest_recotop_p4 is None):
                h_2dcriteria['dR_vs_chi'].Fill(tm_chi, detrecodR)


        if MCReco:
            if not sublead_jet_p4_pre == mctopbjet_p4_pre:# and not (sublead_recotop_p4 is None):
                h_notmatch_criteria_quant['sublead'].Fill(sublead_jet_p4.Pt())
                if not closest_jet_p4_pre == mctopbjet_p4_pre:
                    h_notmatch_2dcriteria['dR_vs_sublead'].Fill(sublead_jet_p4.Pt(), detrecodR)
            else:
                h_match_criteria_quant['sublead'].Fill(sublead_jet_p4.Pt())
                if closest_jet_p4_pre == mctopbjet_p4_pre:
                    h_match_2dcriteria['dR_vs_sublead'].Fill(sublead_jet_p4.Pt(), detrecodR)

            if not closest_jet_p4_pre == mctopbjet_p4_pre:
                h_notmatch_criteria_quant['deltaR'].Fill(detrecodR)
                if not chi_jet_p4_pre == mctopbjet_p4_pre:
                    h_notmatch_2dcriteria['dR_vs_chi'].Fill(tm_chi, detrecodR)
            else:
                h_match_criteria_quant['deltaR'].Fill(detrecodR)
                if chi_jet_p4_pre == mctopbjet_p4_pre:
                    h_match_2dcriteria['dR_vs_chi'].Fill(tm_chi, detrecodR)
                    
            if not chi_jet_p4_pre == mctopbjet_p4_pre:
                h_notmatch_criteria_quant['chimass'].Fill(tm_chi)
                if not sublead_jet_p4_pre == mctopbjet_p4_pre:
                    h_notmatch_2dcriteria['chi_vs_sublead'].Fill(sublead_jet_p4.Pt(), tm_chi)
            else:
                h_match_criteria_quant['chimass'].Fill(tm_chi)
                if sublead_jet_p4_pre == mctopbjet_p4_pre:
                    h_match_2dcriteria['chi_vs_sublead'].Fill(sublead_jet_p4.Pt(), tm_chi)
                
        if subleadTrig:
            sublead_ev += 1
            h_recotop_vs_Wprime_mass_sublead['nobtag'].Fill(sublead_recotop_p4.M()/sublead_Wprime_p4.M())
            h_jet_pt_sublead['topbjet'].Fill(sublead_jet_p4.Pt())
            h_jet_pt_sublead['Wbjet'].Fill(sublead_promptjet.pt)
            h_jet_pt_sublead['top'].Fill(sublead_recotop_p4.Pt())
            h_recotop_mass_sublead['top'].Fill(sublead_recotop_p4.M())
            h_Wprime_mass_sublead['all'].Fill(sublead_Wprime_p4.M())
            if isEle:
                h_Wprime_mass_sublead['ele_all'].Fill(sublead_Wprime_p4.M())
            if isMu:
                h_Wprime_mass_sublead['mu_all'].Fill(sublead_Wprime_p4.M())

        if closestTrig:
            closest_ev += 1
            h_recotop_vs_Wprime_mass_closest['nobtag'].Fill(closest_recotop_p4.M()/closest_Wprime_p4.M())
            h_jet_pt_closest['topbjet'].Fill(closest_jet_p4.Pt())
            h_jet_pt_closest['Wbjet'].Fill(closest_promptjet.pt)
            h_jet_pt_closest['top'].Fill(closest_recotop_p4.Pt())
            h_recotop_mass_closest['top'].Fill(closest_recotop_p4.M())
            h_Wprime_mass_closest['all'].Fill(closest_Wprime_p4.M())
            if isEle:
                h_Wprime_mass_closest['ele_all'].Fill(closest_Wprime_p4.M())
            if isMu:
                h_Wprime_mass_closest['mu_all'].Fill(closest_Wprime_p4.M())

        if chiTrig:
            chimass_ev += 1
            h_recotop_vs_Wprime_mass_chi['nobtag'].Fill(chi_recotop_p4.M()/chi_Wprime_p4.M())
            h_jet_pt_chi['topbjet'].Fill(chi_jet_p4.Pt())
            h_jet_pt_chi['Wbjet'].Fill(chi_promptjet.pt)
            h_jet_pt_chi['top'].Fill(chi_recotop_p4.Pt())
            h_recotop_mass_chi['top'].Fill(chi_recotop_p4.M())
            h_Wprime_mass_chi['all'].Fill(chi_Wprime_p4.M())
            if isEle:
                h_Wprime_mass_chi['ele_all'].Fill(chi_Wprime_p4.M())
            if isMu:
                h_Wprime_mass_chi['mu_all'].Fill(chi_Wprime_p4.M())

        if bestTrig:
            best_ev += 1
            h_recotop_vs_Wprime_mass_best['nobtag'].Fill(best_recotop_p4.M()/best_Wprime_p4.M())
            h_jet_pt_best['topbjet'].Fill(best_jet_p4.Pt())
            h_jet_pt_best['Wbjet'].Fill(best_promptjet.pt)
            h_jet_pt_best['top'].Fill(best_recotop_p4.Pt())
            h_recotop_mass_best['top'].Fill(best_recotop_p4.M())
            h_Wprime_mass_best['all'].Fill(best_Wprime_p4.M())
            if isEle:
                h_Wprime_mass_best['ele_all'].Fill(best_Wprime_p4.M())
            if isMu:
                h_Wprime_mass_best['mu_all'].Fill(best_Wprime_p4.M())

        if subleadTrig or closestTrig or chiTrig:
            h_met_q['pt'].Fill(met.pt)
            h_met_q['Et'].Fill(met.sumEt)
            h_met_q['phi'].Fill(met.phi)
            if isEle:
                h_lepton_pt['electron'].Fill(sellepton.pt)
            elif isMu:
                h_lepton_pt['muon'].Fill(sellepton.pt)
        
        #cut_and_count efficiences
        '''
        h_efficiencies.Fill(isEvent, 1)
        h_efficiencies.Fill(isPreSel, 2)
        h_efficiencies.Fill(isHLT, 3)
        h_efficiencies.Fill(isLepSel, 4)
        h_efficiencies.Fill(isJetSel, 5)
        '''
        if (i%100) == 0:
            print i
    #efficiencies histos
    if HLTrig and MCReco:
        heff_mclepton_pt = {'electron': ROOT.TEfficiency(h_mclepton_pt['electron'], h_mclepton_pt_unHLT['electron']),
                            'muon': ROOT.TEfficiency(h_mclepton_pt['muon'], h_mclepton_pt_unHLT['muon'])
                        }
        heff_mclepton_pt['electron'].SetTitle("HLTEff_MC_Ele_pt;electron pt [GeV];#varepsilon")
        heff_mclepton_pt['electron'].SetName("HLTEff_MC_Ele_pt")
        heff_mclepton_pt['muon'].SetTitle("HLTEff_MC_Mu_pt;muon pt [GeV];#varepsilon")
        heff_mclepton_pt['muon'].SetName("HLTEff_MC_Mu_pt")
        for value in heff_mclepton_pt.values():
            value.SetLineColor(ROOT.kBlue)
        if LepHLTrig:
            heff_lep_mclepton_pt = copy.deepcopy(heff_mclepton_pt)
            for key, value in heff_lep_mclepton_pt.items():
                value.SetPassedHistogram(h_mclepton_pt_lepHLT[key], "")
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'lep' + old_title
                new_name = 'lep' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)
        if HadHLTrig:
            heff_had_mclepton_pt = copy.deepcopy(heff_mclepton_pt)
            for key, value in heff_had_mclepton_pt.items():
                value.SetPassedHistogram(h_mclepton_pt_hadHLT[key], "")
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'had' + old_title
                new_name = 'had' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)
            
        heff_mcbjet_pt = {'Wbjet': ROOT.TEfficiency(h_mcbjet_pt['Wbjet'], h_mcbjet_pt_unHLT['Wbjet']),
                          'topbjet': ROOT.TEfficiency(h_mcbjet_pt['topbjet'], h_mcbjet_pt_unHLT['topbjet']),
                          'top': ROOT.TEfficiency(h_mcbjet_pt['top'], h_mcbjet_pt_unHLT['top']),
                      }
        heff_mcbjet_pt['Wbjet'].SetTitle("HLTEff_MC_Wbjet_pt;prompt bjet pt [GeV];#varepsilon")
        heff_mcbjet_pt['Wbjet'].SetName("HLTEff_MC_Wbjet_pt")
        heff_mcbjet_pt['topbjet'].SetTitle("HLTEff_MC_topbjet_pt;top bjet pt [GeV];#varepsilon")
        heff_mcbjet_pt['topbjet'].SetName("HLTEff_MC_topbjet_pt")
        heff_mcbjet_pt['top'].SetTitle("HLTEff_MC_recotop_pt;top pt [GeV];#varepsilon")
        heff_mcbjet_pt['top'].SetName("HLTEff_MC_top_pt")
        for value in heff_mcbjet_pt.values():
            value.SetLineColor(ROOT.kBlue)
        if LepHLTrig:
            heff_lep_mcbjet_pt = copy.deepcopy(heff_mcbjet_pt)
            for key, value in heff_lep_mcbjet_pt.items():
                value.SetPassedHistogram(h_mcbjet_pt_lepHLT[key], "")
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'lep' + old_title
                new_name = 'lep' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)
        if HadHLTrig:
                heff_had_mcbjet_pt = copy.deepcopy(heff_mcbjet_pt)
                for key, value in heff_had_mcbjet_pt.items():
                    value.SetPassedHistogram(h_mcbjet_pt_hadHLT[key], "")
                    old_title = value.GetTitle()
                    old_name = value.GetName()
                    new_title = 'had' + old_title
                    new_name = 'had' + old_name
                    value.SetTitle(new_title)
                    value.SetName(new_name)
        
        heff_mcWprime_mass = {'gen': ROOT.TEfficiency(h_mcWprime_mass['gen'], h_mcWprime_mass_unHLT['gen']),
                              'all': ROOT.TEfficiency(h_mcWprime_mass['all'], h_mcWprime_mass_unHLT['all']),
                              'ele_all': ROOT.TEfficiency(h_mcWprime_mass['ele_all'], h_mcWprime_mass_unHLT['ele_all']),
                              'mu_all': ROOT.TEfficiency(h_mcWprime_mass['mu_all'], h_mcWprime_mass_unHLT['mu_all']),
                          }
        heff_mcWprime_mass['gen'].SetTitle("HLTEff_MC_GenPart_Wprime_mass;GenPart W' mass [GeV];#varepsilon")
        heff_mcWprime_mass['gen'].SetName("HLTEff_MC_GenPart_Wprime_mass")
        heff_mcWprime_mass['all'].SetTitle("HLTEff_MC_Lep_Wprime_mass;Lep MCReco W' mass [GeV];#varepsilon")
        heff_mcWprime_mass['all'].SetName("HLTEff_MC_Lep_Wprime_mass")
        heff_mcWprime_mass['ele_all'].SetTitle("HLTEff_MC_Ele_Wprime_mass;Ele MCReco W' mass [GeV];#varepsilon")
        heff_mcWprime_mass['ele_all'].SetName("HLTEff_MC_Ele_Wprime_mass")
        heff_mcWprime_mass['mu_all'].SetTitle("HLTEff_MC_Mu_Wprime_mass;Mu MCReco  W' mass [GeV];#varepsilon")
        heff_mcWprime_mass['mu_all'].SetName("HLTEff_MC_Mu_Wprime_mass")
        for value in heff_mcWprime_mass.values():
            value.SetLineColor(ROOT.kBlue)
        if LepHLTrig:
            heff_lep_mcWprime_mass = copy.deepcopy(heff_mcWprime_mass)
            for key, value in heff_lep_mcWprime_mass.items():
                value.SetPassedHistogram(h_mcWprime_mass_lepHLT[key], "")
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'lep' + old_title
                new_name = 'lep' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)
        if HadHLTrig:
            heff_had_mcWprime_mass = copy.deepcopy(heff_mcWprime_mass)
            for key, value in heff_had_mcWprime_mass.items():
                value.SetPassedHistogram(h_mcWprime_mass_hadHLT[key], "")
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'had' + old_title
                new_name = 'had' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)
        
        heff_mcWprime_tmass = {'all': ROOT.TEfficiency(h_mcWprime_tmass['all'], h_mcWprime_tmass_unHLT['all']),
                               'ele_all': ROOT.TEfficiency(h_mcWprime_tmass['ele_all'], h_mcWprime_tmass_unHLT['ele_all']),
                               'mu_all': ROOT.TEfficiency(h_mcWprime_tmass['mu_all'], h_mcWprime_tmass_unHLT['mu_all']),
                           }
        heff_mcWprime_tmass['all'].SetTitle("HLTEff_MC_Lep_Wprime_transverse_mass;Lep MCReco W' transverse mass [GeV];#varepsilon")
        heff_mcWprime_tmass['all'].SetName("HLTEff_MC_Lep_Wprime_transverse_mass")
        heff_mcWprime_tmass['ele_all'].SetTitle("HLTEff_MC_Ele_Wprime_transverse_mass;Ele MCReco W' transverse mass [GeV];#varepsilon")
        heff_mcWprime_tmass['ele_all'].SetName("HLTEff_MC_Ele_Wprime_transverse_mass")
        heff_mcWprime_tmass['mu_all'].SetTitle("HLTEff_MC_Mu_Wprime_transverse_mass;Mu MCReco W' transverse mass [GeV];#varepsilon")
        heff_mcWprime_tmass['mu_all'].SetName("HLTEff_MC_Mu_Wprime_transverse_mass")
        for value in heff_mcWprime_tmass.values():
            value.SetLineColor(ROOT.kBlue)
        if LepHLTrig:
            heff_lep_mcWprime_tmass = copy.deepcopy(heff_mcWprime_tmass)
            for key, value in heff_lep_mcWprime_tmass.items():
                value.SetPassedHistogram(h_mcWprime_tmass_lepHLT[key], "")
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'lep' + old_title
                new_name = 'lep' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)
        if HadHLTrig:
            heff_had_mcWprime_tmass = copy.deepcopy(heff_mcWprime_tmass)
            for key, value in heff_had_mcWprime_tmass.items():
                value.SetPassedHistogram(h_mcWprime_tmass_hadHLT[key], "")
                old_title = value.GetTitle()
                old_name = value.GetName()
                new_title = 'had' + old_title
                new_name = 'had' + old_name
                value.SetTitle(new_title)
                value.SetName(new_name)

    if DetReco:
        h_countings.SetBinContent(1, nentries)
        h_countings.SetBinContent(2, PreSelEvt)
        h_countings.SetBinContent(3, HLTriggered)
        h_countings.SetBinContent(4, LepTriggered)
        h_countings.SetBinContent(5, JetTriggered)
        h_countings.SetBinContent(6, sublead_ev)
        h_countings.SetBinContent(7, chimass_ev)
        h_countings.SetBinContent(8, closest_ev)
        h_countings.SetBinContent(9, best_ev)

        for k in range(9):
            k = k + 1
            h_eff_benchmark.SetBinContent(k, nentries)

        h_efficiencies = ROOT.TEfficiency(h_countings, h_eff_benchmark)
        h_efficiencies.SetName("DetReco_efficiencies")
        h_efficiencies.SetTitle("DetReco_efficiencies;;#varepsilon")
        h_efficiencies.SetLineColor(ROOT.kBlue)
        h_efficiencies_gae = GetTGAEfromTE(h_efficiencies, naeff)

    '''    
    if DetReco and MCReco and HLTrig:
        hmceff_Wprime_mass_sublead = {'all': ROOT.TEfficiency(),
                                      'ele_all': ROOT.TEfficiency(),
                                      'mu_all': ROOT.TEfficiency(),
        }
        
        hmceff_Wprime_mass_sublead['all'].SetPassedHistogram(h_Wprime_mass_sublead['all'], "f")
        hmceff_Wprime_mass_sublead['all'].SetTotalHistogram(h_mcWprime_mass['all'], "f")
        hmceff_Wprime_mass_sublead['ele_all'].SetPassedHistogram(h_Wprime_mass_sublead['ele_all'], "f")
        hmceff_Wprime_mass_sublead['ele_all'].SetTotalHistogram(h_mcWprime_mass['ele_all'], "f")
        hmceff_Wprime_mass_sublead['mu_all'].SetPassedHistogram(h_Wprime_mass_sublead['mu_all'], "f")
        hmceff_Wprime_mass_sublead['mu_all'].SetTotalHistogram(h_mcWprime_mass['mu_all'], "f")
        hmceff_Wprime_mass_sublead['all'].SetTitle("MCEff_sublead_Lep_Wprime_mass;Lep DetReco W' mass [GeV];#varepsilon")
        hmceff_Wprime_mass_sublead['all'].SetName("MCEff_sublead_Lep_Wprime_mass")
        hmceff_Wprime_mass_sublead['ele_all'].SetTitle("MCEff_sublead_Ele_Wprime_mass;Ele DetReco W' mass [GeV];#varepsilon")
        hmceff_Wprime_mass_sublead['ele_all'].SetName("MCEff_sublead_Ele_Wprime_mass")
        hmceff_Wprime_mass_sublead['mu_all'].SetTitle("MCEff_sublead_Mu_Wprime_mass;Mu DetReco  W' mass [GeV];#varepsilon")
        hmceff_Wprime_mass_sublead['mu_all'].SetName("MCEff_sublead_Mu_Wprime_mass")

        for value in hmceff_Wprime_mass_sublead.values():
            value.SetLineColor(ROOT.kBlue)
        hmceff_Wprime_mass_sublead_gae = {}
        for key, value in hmceff_Wprime_mass_sublead.items():
            value.SetConfidenceLevel(0.01)
            tgae = GetTGAEfromTE(value)
            new_item = {key: tgae}
            hmceff_Wprime_mass_sublead_gae.update(new_item)
                
        hmceff_Wprime_mass_closest = {'all': ROOT.TEfficiency(),#h_Wprime_mass_closest['all'], h_mcWprime_mass['all']),
                                      'ele_all': ROOT.TEfficiency(),#h_Wprime_mass_closest['all'], h_mcWprime_mass['ele_all']),
                                      'mu_all': ROOT.TEfficiency(),#h_Wprime_mass_closest['mu_all'], h_mcWprime_mass['mu_all']),
        }
        
        hmceff_Wprime_mass_closest['all'].SetPassedHistogram(h_Wprime_mass_closest['all'], "f")
        hmceff_Wprime_mass_closest['all'].SetTotalHistogram(h_mcWprime_mass['all'], "f")
        hmceff_Wprime_mass_closest['ele_all'].SetPassedHistogram(h_Wprime_mass_closest['ele_all'], "f")
        hmceff_Wprime_mass_closest['ele_all'].SetTotalHistogram(h_mcWprime_mass['ele_all'], "f")
        hmceff_Wprime_mass_closest['mu_all'].SetPassedHistogram(h_Wprime_mass_closest['mu_all'], "f")
        hmceff_Wprime_mass_closest['mu_all'].SetTotalHistogram(h_mcWprime_mass['mu_all'], "f")
        hmceff_Wprime_mass_closest['all'].SetTitle("MCEff_closest_Lep_Wprime_mass;Lep DetReco W' mass [GeV];#varepsilon")
        hmceff_Wprime_mass_closest['all'].SetName("MCEff_closest_Lep_Wprime_mass")
        hmceff_Wprime_mass_closest['ele_all'].SetTitle("MCEff_closest_Ele_Wprime_mass;Ele DetReco W' mass [GeV];#varepsilon")
        hmceff_Wprime_mass_closest['ele_all'].SetName("MCEff_closest_Ele_Wprime_mass")
        hmceff_Wprime_mass_closest['mu_all'].SetTitle("MCEff_closest_Mu_Wprime_mass;Mu DetReco  W' mass [GeV];#varepsilon")
        hmceff_Wprime_mass_closest['mu_all'].SetName("MCEff_closest_Mu_Wprime_mass")

        for value in hmceff_Wprime_mass_closest.values():
            value.SetLineColor(ROOT.kBlue)
        hmceff_Wprime_mass_closest_gae = {}
        for key, value in hmceff_Wprime_mass_closest.items():
            value.SetConfidenceLevel(0.01)
            tgae = GetTGAEfromTE(value)
            new_item = {key: tgae}
            hmceff_Wprime_mass_closest_gae.update(new_item)

        hmceff_Wprime_mass_chi = {'all': ROOT.TEfficiency(),#h_Wprime_mass_chi['all'], h_mcWprime_mass['all']),
                                      'ele_all': ROOT.TEfficiency(),#h_Wprime_mass_chi['all'], h_mcWprime_mass['ele_all']),
                                      'mu_all': ROOT.TEfficiency(),#h_Wprime_mass_chi['mu_all'], h_mcWprime_mass['mu_all']),
        }
        hmceff_Wprime_mass_chi['all'].SetPassedHistogram(h_Wprime_mass_chi['all'], "f")
        hmceff_Wprime_mass_chi['all'].SetTotalHistogram(h_mcWprime_mass['all'], "f")
        hmceff_Wprime_mass_chi['ele_all'].SetPassedHistogram(h_Wprime_mass_chi['ele_all'], "f")
        hmceff_Wprime_mass_chi['ele_all'].SetTotalHistogram(h_mcWprime_mass['ele_all'], "f")
        hmceff_Wprime_mass_chi['mu_all'].SetPassedHistogram(h_Wprime_mass_chi['mu_all'], "f")
        hmceff_Wprime_mass_chi['mu_all'].SetTotalHistogram(h_mcWprime_mass['mu_all'], "f")
        hmceff_Wprime_mass_chi['all'].SetTitle("MCEff_chi_Lep_Wprime_mass;Lep DetReco W' mass [GeV];#varepsilon")
        hmceff_Wprime_mass_chi['all'].SetName("MCEff_chi_Lep_Wprime_mass")
        hmceff_Wprime_mass_chi['ele_all'].SetTitle("MCEff_chi_Ele_Wprime_mass;Ele DetReco W' mass [GeV];#varepsilon")
        hmceff_Wprime_mass_chi['ele_all'].SetName("MCEff_chi_Ele_Wprime_mass")
        hmceff_Wprime_mass_chi['mu_all'].SetTitle("MCEff_chi_Mu_Wprime_mass;Mu DetReco  W' mass [GeV];#varepsilon")
        hmceff_Wprime_mass_chi['mu_all'].SetName("MCEff_chi_Mu_Wprime_mass")

        for value in hmceff_Wprime_mass_chi.values():
            value.SetLineColor(ROOT.kBlue)
        hmceff_Wprime_mass_chi_gae = {}
        for key, value in hmceff_Wprime_mass_chi.items():
            value.SetConfidenceLevel(0.01)
            tgae = GetTGAEfromTE(value)
            new_item = {key: tgae}
            hmceff_Wprime_mass_chi_gae.update(new_item)
    '''

    #effhistos printing and saving
    if HLTrig and MCReco:
        for value in heff_mclepton_pt.values():
            print_hist(inpfile, subfold, value, 'AP')
            save_hist(inpfile, subfold, value, 'AP')
        for value in heff_mcbjet_pt.values():
            print_hist(inpfile, subfold, value, 'AP')
            save_hist(inpfile, subfold, value, 'AP')
        for value in heff_mcWprime_mass.values():
            print_hist(inpfile, subfold, value, 'AP')
            save_hist(inpfile, subfold, value, 'AP')
        for value in heff_mcWprime_tmass.values():
            print_hist(inpfile, subfold, value, 'AP')
            save_hist(inpfile, subfold, value, 'AP')

        if LepHLTrig:
            for value in heff_lep_mclepton_pt.values():
                print_hist(inpfile, subfold, value, 'AP')
                save_hist(inpfile, subfold, value, 'AP')
            for value in heff_lep_mcbjet_pt.values():
                print_hist(inpfile, subfold, value, 'AP')
                save_hist(inpfile, subfold, value, 'AP')
            for value in heff_lep_mcWprime_mass.values():
                print_hist(inpfile, subfold, value, 'AP')
                save_hist(inpfile, subfold, value, 'AP')
            for value in heff_lep_mcWprime_tmass.values():
                print_hist(inpfile, subfold, value, 'AP')
                save_hist(inpfile, subfold, value, 'AP')
        
        if HadHLTrig:
            for value in heff_had_mclepton_pt.values():
                print_hist(inpfile, subfold, value, 'AP')
                save_hist(inpfile, subfold, value, 'AP')
            for value in heff_had_mcbjet_pt.values():
                print_hist(inpfile, subfold, value, 'AP')
                save_hist(inpfile, subfold, value, 'AP')
            for value in heff_had_mcWprime_mass.values():
                print_hist(inpfile, subfold, value, 'AP')
                save_hist(inpfile, subfold, value, 'AP')
            for value in heff_had_mcWprime_tmass.values():
                print_hist(inpfile, subfold, value, 'AP')
                save_hist(inpfile, subfold, value, 'AP')
        '''
        if DetReco:
            for value in hmceff_Wprime_mass_sublead_gae.values():
               print_hist(inpfile, value)
               save_hist(inpfile, value)
            for value in hmceff_Wprime_mass_closest_gae.values():
               print_hist(inpfile, value)
               save_hist(inpfile, value)
            for value in hmceff_Wprime_mass_chi_gae.values():
               print_hist(inpfile, value)
               save_hist(inpfile, value)
         '''   
    #histo printing and saving
    if MCReco:
        for value in h_mclepton_pt_unHLT.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_mcbjet_pt_unHLT.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_mcWprime_mass_unHLT.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_mcWprime_tmass_unHLT.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_mcmet_q_unHLT.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)

        if HLTrig:
            for value in h_mc_criteria_quant.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mc_criteria_quant_IsNeg.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mc_2dcriteria.values():
                print_hist(inpfile, subfold, value, "COLZ")
                save_hist(inpfile, subfold, value, "COLZ")
            for value in h_mc_2dcriteria_IsNeg.values():
                print_hist(inpfile, subfold, value, "COLZ")
                save_hist(inpfile, subfold, value, "COLZ")
            for value in h_mclepton_pt.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcbjet_pt.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcWprime_mass.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcWprime_mass_IsNeg.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcWprime_tmass.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcmet_q.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcmet_q_IsNeg.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)

            print_hist(inpfile, subfold, h_mcrecotop_mass['top'], "HIST0")
            save_hist(inpfile, subfold, h_mcrecotop_mass['top'], "HIST0")
            for value in h_mcrecotop_mass_IsNeg.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
        
        if LepHLTrig:
            for value in h_mclepton_pt_lepHLT.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcbjet_pt_lepHLT.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcWprime_mass_lepHLT.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcWprime_tmass_lepHLT.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcmet_q_lepHLT.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)

        if HadHLTrig:
            for value in h_mclepton_pt_hadHLT.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcbjet_pt_hadHLT.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcWprime_mass_hadHLT.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcWprime_tmass_hadHLT.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcmet_q_hadHLT.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)

        if AK8Reco:
            for value in h_mcfatlepton_pt.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcfatbjet_pt.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcfatWprime_mass.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_mcfatWprime_tmass.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_fatmet_q.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
                
        print_hist(inpfile, subfold, h_sameflav_bjet_deltaR)
        save_hist(inpfile, subfold, h_sameflav_bjet_deltaR)
        print_hist(inpfile, subfold, h_mcrecotop_vs_mcWprime_mass)
        save_hist(inpfile, subfold, h_mcrecotop_vs_mcWprime_mass)
        for value in h_mcmcrecotop_vs_mcWprime_mass_IsNeg.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
    if DetReco:
        for value in h_recotop_vs_Wprime_mass_sublead.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_recotop_vs_Wprime_mass_closest.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_recotop_vs_Wprime_mass_chi.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_recotop_vs_Wprime_mass_best.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_recotop_vs_Wprime_mass_sublead_IsNeg.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_recotop_vs_Wprime_mass_closest_IsNeg.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_recotop_vs_Wprime_mass_chi_IsNeg.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_recotop_vs_Wprime_mass_best_IsNeg.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)

        for value in h_criteria_quant.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_2dcriteria.values():
            print_hist(inpfile, subfold, value, "COLZ")
            save_hist(inpfile, subfold, value, "COLZ")
        for value in h_lepton_pt.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_jet_pt_sublead.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_jet_pt_closest.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_jet_pt_chi.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_jet_pt_best.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_Wprime_mass_sublead.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_Wprime_mass_closest.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_Wprime_mass_best.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        for value in h_Wprime_mass_chi.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)
        if MCReco:
            for value in h_notmatch_criteria_quant.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_match_criteria_quant.values():
                print_hist(inpfile, subfold, value)
                save_hist(inpfile, subfold, value)
            for value in h_notmatch_2dcriteria.values():
                print_hist(inpfile, subfold, value, "COLZ")
                save_hist(inpfile, subfold, value, "COLZ")
            for value in h_match_2dcriteria.values():
                print_hist(inpfile, subfold, value, "COLZ")
                save_hist(inpfile, subfold, value, "COLZ")

        '''
        for value in h_Wprime_tmass_sublead.values():
            print_hist(inpfile, value)
            save_hist(inpfile, value)
        for value in h_Wprime_tmass_closest.values():
            print_hist(inpfile, value)
            save_hist(inpfile, value)
        for value in h_Wprime_tmass_chi.values():
            print_hist(inpfile, value)
            save_hist(inpfile, value)
        '''
        for value in h_met_q.values():
            print_hist(inpfile, subfold, value)
            save_hist(inpfile, subfold, value)

        print_hist(inpfile, subfold, h_countings, "HIST0")
        save_hist(inpfile, subfold, h_countings, "HIST0")
        print_hist(inpfile, subfold, h_efficiencies_gae, "AP")
        save_hist(inpfile, subfold, h_efficiencies_gae, "AP")

        print_hist(inpfile, subfold, h_recotop_mass_sublead['top'], "HIST0")
        save_hist(inpfile, subfold, h_recotop_mass_sublead['top'], "HIST0")
        print_hist(inpfile, subfold, h_recotop_mass_closest['top'], "HIST0")
        save_hist(inpfile, subfold, h_recotop_mass_closest['top'], "HIST0")
        print_hist(inpfile, subfold, h_recotop_mass_chi['top'], "HIST0")
        save_hist(inpfile, subfold, h_recotop_mass_chi['top'], "HIST0")
        print_hist(inpfile, subfold, h_recotop_mass_best['top'], "HIST0")
        save_hist(inpfile, subfold, h_recotop_mass_best['top'], "HIST0")
    
    print 'Total events: %d   ||   Bad MET flag events %d   ||   Bad events %d   ||   MC Events %d    ||   HLTriggered %d   ||   LepTriggered %d   ||   JetTriggered %d   ||' %(tree.GetEntries(), badflag, badevt, MCEvents, HLTriggered, LepTriggered, JetTriggered)

