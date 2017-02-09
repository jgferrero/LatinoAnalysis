#
#
#      |     ___ \  
#      |        ) | 
#      |       __/  
#     _____| _____| 
#                                
#
#
#
# electron id: https://twiki.cern.ch/twiki/bin/view/CMS/EgammaIDRecipesRun2
#
#


from LatinoAnalysis.Gardener.gardening import TreeCloner
import numpy
import ROOT
import math
import sys
import optparse
import re
import warnings
import os.path
from collections import OrderedDict
from array import array;

class L2SelFiller(TreeCloner):
    def __init__(self):
       pass

    def help(self):
        return '''Apply id/iso and filter lepton collection'''

    def addOptions(self,parser):
        description = self.help()
        group = optparse.OptionGroup(parser,self.label, description)
        group.add_option('-k', '--kind',  dest='kind',  help='Kind of lepton identification to be applied [default is loose leptons]',  default='2')
        group.add_option('-c', '--cmssw', dest='cmssw', help='cmssw version (naming convention may change)', default='763', type='string')
        group.add_option('-s', '--selection', dest='selection', help='apply some selections, like pt cuts', default=0)
        # new feature introduced for Full2016 (Jan 2017)
        group.add_option( '--idEleKind' , dest='idEleKind', help='kind of electron id', default=None) # e.g. "cut_WP_Tight80X"
        parser.add_option_group(group)
        return group

    def checkOptions(self,opts):
        if not (hasattr(opts,'kind')):
          self.kind = 1
        else :    
          self.kind   = 1.0 * float(opts.kind)
        print " kind of electron id = ", self.kind

        self.cmssw = opts.cmssw
        print " cmssw = ", self.cmssw

        self.selection = opts.selection
        print " selection = ", self.selection
        
        self.idEleKind = opts.idEleKind
        print " idEleKind = ", self.idEleKind
        

    def changeOrder(self, vectorname, vector, goodleptonslist) :
        # vector is already linked to the otree branch
        # vector name is the "name" of that vector to be modified
        
        #for i in range( len(getattr(self.otree, vectorname)) ) :
          #pass
          #print " --> before ", vectorname, "[", i, "] = ", getattr(self.otree, vectorname)[i]

        # take vector and clone vector
        # equivalent of: temp_vector = itree."vector"
        temp_vector = getattr(self.itree, vectorname)
        # remix the order of vector picking from the clone
        for i in range( len(goodleptonslist) ) :
          #print " --> [", i, " :: ", len(goodleptonslist) ,"] :::>> ", len(temp_vector), " --> ", goodleptonslist[i]      
          # otree."vectorname"[i] = temp_vector[goodleptonslist[i]] <--- that is the "itree" in the correct position
          # setattr(self.otree, vector + "[" + str(i) + "]", temp_vector[ goodleptonslist[i] ])
          vector.push_back ( temp_vector[ goodleptonslist[i] ] )
          #vector.push_back ( 10000. )
        # set the default value for the remaining
        for i in range( len(temp_vector) - len(goodleptonslist) ) :
          vector.push_back ( -9999. )
          
        #for i in range( len(getattr(self.otree, vectorname)) ) :
          #pass
          #print " --> after[ " , len(goodleptonslist), "] ", vectorname, "[", i, "] = ", getattr(self.otree, vectorname)[i]
        
    def jetIsLepton(self, jetEta, jetPhi, lepEta, lepPhi) :
        #dR = ROOT.TMath.Sqrt( ROOT.TMath.Power(lepEta - jetEta, 2) + ROOT.TMath.Power(ROOT.TMath.Abs(ROOT.TMath.Abs(lepPhi - jetPhi)-ROOT.TMath.Pi())-ROOT.TMath.Pi(), 2) )
        dPhi = ROOT.TMath.Abs(lepPhi - jetPhi)
        if dPhi > ROOT.TMath.Pi() :
          dPhi = 2*ROOT.TMath.Pi() - dPhi
        dR2 = (lepEta - jetEta) * (lepEta - jetEta) + dPhi * dPhi
        dR2Max = 0.3*0.3
        if (self.kind == 5 or self.kind == 6) :
            dR2Max = 0.4*0.4
        if dR2 < dR2Max:
            return True
        else:
            return False

    def isAcloseToB(self, a_Eta, a_Phi, b_Eta, b_Phi, drmax) :
        dPhi = ROOT.TMath.Abs(b_Phi - a_Phi)
        if dPhi > ROOT.TMath.Pi() :
          dPhi = 2*ROOT.TMath.Pi() - dPhi
        dR2 = (b_Eta - a_Eta) * (b_Eta - a_Eta) + dPhi * dPhi
        if dR2 < (drmax*drmax):
            return True
        else:
            return False
  




    def isLooseLepton(self, ilepton) :
       
       # denominator of fakes definition
      
       isThisALooseLepton = 0
       
       if self.itree.std_vector_lepton_pt[ilepton] > 0 :
            
           ###########
           # electron
           
           # id definition
           if self.cmssw == '763' :               
           
             if (
                abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 
                and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5
                and self.itree.std_vector_lepton_trackIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.2 
                and self.itree.std_vector_electron_ecalPFClusterIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.45
                and self.itree.std_vector_electron_hcalPFClusterIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.25 
                and 
                 ((
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.479) 
                 and    (abs(self.itree.std_vector_electron_dEtaIn[ilepton]) < 0.01               and
                         abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.04               and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.011              and
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.08               and
                         self.itree.std_vector_electron_ooEmooP[ilepton] < 0.01               and 
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<=2  and
                         self.itree.std_vector_lepton_d0[ilepton]      < 0.1                and
                         abs(self.itree.std_vector_lepton_dz[ilepton])< 0.373              and
                         self.itree.std_vector_electron_passConversionVeto[ilepton] )
                 )
                 or 
                 (
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) > 1.479 and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5)
                 and    (abs(self.itree.std_vector_electron_dEtaIn[ilepton]) < 0.01               and
                         abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.08               and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.031              and
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.08               and
                         self.itree.std_vector_electron_ooEmooP[ilepton] < 0.01               and
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<=1  and
                         self.itree.std_vector_lepton_d0[ilepton]      < 0.2                and
                         abs(self.itree.std_vector_lepton_dz[ilepton])< 0.602              and
                         self.itree.std_vector_electron_passConversionVeto[ilepton] )
                 ))
                ) : 
                  isThisALooseLepton = 1
                  
           elif self.cmssw == 'Full2016' :                 
             # HLT safe
             #
             if abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5:
                if self.itree.std_vector_lepton_eleIdHLT[ilepton] :
                    isThisALooseLepton = 1

                  
           elif self.cmssw == 'ICHEP2016' or self.cmssw == 'Rereco2016' :  # temp fix for Rereco so it doesn't crash on 74X variables               
             #
             # see https://indico.cern.ch/event/491507/contributions/2192817/attachments/1285452/1911768/EGM_HLTsafeCuts_31May16.pdf
             #
             if (
                abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 
                and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5
                and self.itree.std_vector_lepton_trackIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.08                
                and
                ((
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.479) 
                 and    (
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.060        and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.011   and
                         abs(self.itree.std_vector_electron_dEtaSeedCalo[ilepton])  < 0.004         and
                         abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.020                and
                         abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.013               and 
                         (self.itree.std_vector_electron_ecalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.165)/self.itree.std_vector_lepton_pt[ilepton] < 0.160   and
                         (self.itree.std_vector_electron_hcalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.060)/self.itree.std_vector_lepton_pt[ilepton] < 0.120   and
                         abs(self.itree.std_vector_lepton_d0[ilepton])< 0.1                  and
                         abs(self.itree.std_vector_lepton_dz[ilepton])< 0.373                 and
                         self.itree.std_vector_electron_passConversionVeto[ilepton]           and
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<1
                         )
                 )
                 or 
                 (
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) > 1.479 and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5)
                 and    (
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.060            and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.031       and
                         abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.013                   and 
                         (self.itree.std_vector_electron_ecalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.132)/self.itree.std_vector_lepton_pt[ilepton] < 0.120   and
                         (self.itree.std_vector_electron_hcalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.131)/self.itree.std_vector_lepton_pt[ilepton] < 0.120   and
                         abs(self.itree.std_vector_electron_gsfnormalizedchi2[ilepton]) < 3       and
                         abs(self.itree.std_vector_lepton_d0[ilepton])< 0.2               and
                         abs(self.itree.std_vector_lepton_dz[ilepton])< 0.602              and
                         self.itree.std_vector_electron_passConversionVeto[ilepton]        and
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<1 
                         )
                 ))
                ) : 
                  isThisALooseLepton = 1
                  
           else : # 74X cmssw release
             if (
                abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 
                and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5
                and 
                 ((
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.479) 
                 and    (abs(self.itree.std_vector_electron_dEtaIn[ilepton]) < 0.01               and
                         abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.04               and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.011              and
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.08               and
                         self.itree.std_vector_electron_ooEmooP[ilepton] < 0.01               and 
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<=2  and
                         self.itree.std_vector_electron_d0[ilepton]      < 0.1                and
                         abs(self.itree.std_vector_electron_dz[ilepton])< 0.373              and
                         self.itree.std_vector_electron_passConversionVeto[ilepton] )
                 )
                 or 
                 (
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) > 1.479 and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5)
                 and    (abs(self.itree.std_vector_electron_dEtaIn[ilepton]) < 0.01               and
                         abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.08               and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.031              and
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.08               and
                         self.itree.std_vector_electron_ooEmooP[ilepton] < 0.01               and
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<=1  and
                         self.itree.std_vector_electron_d0[ilepton]      < 0.2                and
                         abs(self.itree.std_vector_electron_dz[ilepton])< 0.602              and
                         self.itree.std_vector_electron_passConversionVeto[ilepton] )
                 ))
                ) : 
                  isThisALooseLepton = 1 
           
           ###########
           # muon
           dxy = float(0.01)
           if (self.itree.std_vector_lepton_pt[ilepton] > 20):
               dxy = float(0.02)
           
           muonIso = float(0.0)
           
           if ( (self.itree.std_vector_lepton_photonIso[ilepton] +
                self.itree.std_vector_lepton_neutralHadronIso[ilepton] -
                0.5 * self.itree.std_vector_lepton_sumPUPt[ilepton]) > 0
                ) :
               muonIso = (self.itree.std_vector_lepton_photonIso[ilepton] +
                          self.itree.std_vector_lepton_neutralHadronIso[ilepton] -
                          0.5 * self.itree.std_vector_lepton_sumPUPt[ilepton])
           else:
               muonIso = 0
           
           if self.cmssw == '763' :               
             if ( self.itree.std_vector_lepton_isMediumMuon[ilepton] == 1 
                  and (self.itree.std_vector_lepton_chargedHadronIso[ilepton] + muonIso) / self.itree.std_vector_lepton_pt[ilepton] < 0.4
                  and abs(self.itree.std_vector_lepton_flavour[ilepton]) == 13
                  and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4
                  and abs(self.itree.std_vector_lepton_d0[ilepton]) < dxy          # formerly std_vector_lepton_BestTrackdxy
                  and abs(self.itree.std_vector_lepton_dz[ilepton]) < 0.1          # formerly std_vector_lepton_BestTrackdz
                  and self.itree.std_vector_lepton_trackIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.4
                  ) :
               isThisALooseLepton = 1.0
               
           elif self.cmssw == 'ICHEP2016' or self.cmssw == 'Rereco2016' or self.cmssw == 'Full2016':               
             if ( self.itree.std_vector_lepton_isTightMuon[ilepton] == 1 
                  and (self.itree.std_vector_lepton_chargedHadronIso[ilepton] + muonIso) / self.itree.std_vector_lepton_pt[ilepton] < 0.4
                  and abs(self.itree.std_vector_lepton_flavour[ilepton]) == 13
                  and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4
                  and abs(self.itree.std_vector_lepton_d0[ilepton]) < dxy          # formerly std_vector_lepton_BestTrackdxy
                  and abs(self.itree.std_vector_lepton_dz[ilepton]) < 0.1          # formerly std_vector_lepton_BestTrackdz
                  and self.itree.std_vector_lepton_trackIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.4
                  ) :
               isThisALooseLepton = 1.0               
           else : 
             if ( self.itree.std_vector_lepton_isMediumMuon[ilepton] == 1 
                  and (self.itree.std_vector_lepton_chargedHadronIso[ilepton] + muonIso) / self.itree.std_vector_lepton_pt[ilepton] < 0.4
                  and abs(self.itree.std_vector_lepton_flavour[ilepton]) == 13
                  and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4
                  and abs(self.itree.std_vector_lepton_BestTrackdxy[ilepton]) < dxy
                  and abs(self.itree.std_vector_lepton_BestTrackdz[ilepton]) < 0.1 
                  ) :
               isThisALooseLepton = 1.0
           
       return isThisALooseLepton
      



    def isTightLepton(self, ilepton) :

       isThisATightLepton = 0

       if self.itree.std_vector_lepton_pt[ilepton] > 0 :
       
           ###########
           # electron
           
           if self.cmssw == '763' :
             # id definition
             if ( self.itree.std_vector_lepton_eleIdTight[ilepton] == 1
                  and abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 
                  and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5
                  and self.itree.std_vector_lepton_trackIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.2 
                  and self.itree.std_vector_electron_ecalPFClusterIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.45
                  and self.itree.std_vector_electron_hcalPFClusterIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.25 
                 ) :
               isThisATightLepton = 1
               
           elif self.cmssw == 'Full2016' :                 
              if abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5:               
                 if self.idEleKind == 'cut_WP_Tight80X':
                     #Tight cut WP + HLT + triple charge + missing hits veto + d0 and dz recommendation               
                    if ( self.itree.std_vector_lepton_eleIdTight[ilepton] and self.itree.std_vector_lepton_eleIdHLT[ilepton]
                        and self.itree.std_vector_electron_tripleChargeAgreement[ilepton] 
                        and self.itree.std_vector_electron_expectedMissingInnerHits[ilepton] < 1 
                        and abs(self.itree.std_vector_lepton_d0[ilepton]) < ( 0.05 + 0.05*(abs(self.itree.std_vector_lepton_eta[ilepton]) > 1.479) )
                        and abs(self.itree.std_vector_lepton_dz[ilepton]) < ( 0.1  + 0.1 *(abs(self.itree.std_vector_lepton_eta[ilepton]) > 1.479) ) 
                       ):
                            isThisATightLepton = 1
                 else :
                    if self.itree.std_vector_lepton_eleIdMvaWp80[ilepton] :
                        isThisATightLepton = 1
                    
           elif self.cmssw == 'ICHEP2016' :               
             #
             # see https://indico.cern.ch/event/491507/contributions/2192817/attachments/1285452/1911768/EGM_HLTsafeCuts_31May16.pdf
             #
             if (
                abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 
                and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5
                and self.itree.std_vector_lepton_trackIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.08                
                and
                ((
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.479) 
                 and    (
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.060        and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.011   and
                         abs(self.itree.std_vector_electron_dEtaSeedCalo[ilepton])  < 0.004         and
                         abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.020                and
                         abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.013               and 
                         (self.itree.std_vector_electron_ecalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.165)/self.itree.std_vector_lepton_pt[ilepton] < 0.160   and
                         (self.itree.std_vector_electron_hcalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.060)/self.itree.std_vector_lepton_pt[ilepton] < 0.120   and
                         abs(self.itree.std_vector_lepton_d0[ilepton])      < 0.1                  and
                         abs(self.itree.std_vector_lepton_dz[ilepton])< 0.373                 and
                         self.itree.std_vector_electron_passConversionVeto[ilepton]           and
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<1  
                         )
                 )
                 or 
                 (
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) > 1.479 and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5)
                 and    (
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.060            and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.031       and
                         abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.013                   and 
                         (self.itree.std_vector_electron_ecalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.132)/self.itree.std_vector_lepton_pt[ilepton] < 0.120   and
                         (self.itree.std_vector_electron_hcalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.131)/self.itree.std_vector_lepton_pt[ilepton] < 0.120   and
                         abs(self.itree.std_vector_electron_gsfnormalizedchi2[ilepton]) < 3       and
                         abs(self.itree.std_vector_lepton_d0[ilepton])      < 0.2               and
                         abs(self.itree.std_vector_lepton_dz[ilepton])< 0.602              and
                         self.itree.std_vector_electron_passConversionVeto[ilepton]        and
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<1 
                         )
                 ))
                 
                 
                 and
                 
                ((
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.479) 
                 and    (
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.0597       and
                         abs(self.itree.std_vector_electron_dEtaIn[ilepton])         < 0.00926      and
                         abs(self.itree.std_vector_electron_dPhiIn[ilepton])         < 0.0336       and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.0101  and
                         abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.012               and 
                         abs(self.itree.std_vector_lepton_d0[ilepton])      < 0.1                   and
                         abs(self.itree.std_vector_lepton_dz[ilepton])< 0.373                       and
                         self.itree.std_vector_electron_passConversionVeto[ilepton]                 and
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<1        and
                         (self.itree.std_vector_lepton_chargedHadronIso[ilepton] \
                           +max(self.itree.std_vector_lepton_neutralHadronIso[ilepton] +  \
                                self.itree.std_vector_lepton_photonIso[ilepton] -  \
                                self.itree.jetRho*self.itree.std_vector_electron_effectiveArea[ilepton],0))/self.itree.std_vector_lepton_pt[ilepton]   <  0.0354
                         )
                 )
                 or 
                 (
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) > 1.479 and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5)
                 and    (
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.0615           and
                         abs(self.itree.std_vector_electron_dEtaIn[ilepton])         < 0.00724          and
                         abs(self.itree.std_vector_electron_dPhiIn[ilepton])         < 0.0918           and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]   < 0.0279       and
                         abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.00999                 and 
                         abs(self.itree.std_vector_lepton_d0[ilepton])      < 0.2                       and
                         abs(self.itree.std_vector_lepton_dz[ilepton])< 0.602                           and
                         self.itree.std_vector_electron_passConversionVeto[ilepton]                     and
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<1             and
                         (self.itree.std_vector_lepton_chargedHadronIso[ilepton] \
                           +max(self.itree.std_vector_lepton_neutralHadronIso[ilepton] +  \
                                self.itree.std_vector_lepton_photonIso[ilepton] -  \
                                self.itree.jetRho*self.itree.std_vector_electron_effectiveArea[ilepton],0))/self.itree.std_vector_lepton_pt[ilepton]   <  0.0646
                         )
                 ))
                 
                ) : 
                  isThisATightLepton = 1

           elif self.cmssw == 'Rereco2016' :               
             #
             # Tight + HLT + d0 and dz recommendation
             #
             if (
                abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 
                and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5
                and self.itree.std_vector_lepton_trackIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.08   # Needs to be updated to std_vector_lepton_trackIso03            
                and
                ((
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.479) 
                 and    (
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.0414        and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.00998   and
                         abs(self.itree.std_vector_electron_dEtaIn[ilepton])  < 0.00308         and  # Needs to be updated  
                         abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.020                and
                         abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.0129               and 
                         (self.itree.std_vector_electron_ecalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.165)/self.itree.std_vector_lepton_pt[ilepton] < 0.160   and
                         (self.itree.std_vector_electron_hcalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.060)/self.itree.std_vector_lepton_pt[ilepton] < 0.120   and
                         abs(self.itree.std_vector_lepton_d0[ilepton])      < 0.05                  and
                         abs(self.itree.std_vector_lepton_dz[ilepton]) < 0.10                 and
                         self.itree.std_vector_electron_passConversionVeto[ilepton]           and
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<1   and
                         (self.itree.std_vector_lepton_chargedHadronIso[ilepton] \
                           +max(self.itree.std_vector_lepton_neutralHadronIso[ilepton] +  \
                                self.itree.std_vector_lepton_photonIso[ilepton] -  \
                                self.itree.jetRho*self.itree.std_vector_electron_effectiveArea[ilepton],0))/self.itree.std_vector_lepton_pt[ilepton]   <  0.0588
                         )
                 )
                 or 
                 (
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) > 1.479 and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5)
                 and    (
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.0641            and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.0292       and
                         abs(self.itree.std_vector_electron_dEtaIn[ilepton])  < 0.00605         and  # Needs to be updated 
                         abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.0394                and
                         abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.0129                   and 
                         (self.itree.std_vector_electron_ecalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.132)/self.itree.std_vector_lepton_pt[ilepton] < 0.120   and
                         (self.itree.std_vector_electron_hcalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.131)/self.itree.std_vector_lepton_pt[ilepton] < 0.120   and
                         abs(self.itree.std_vector_electron_gsfnormalizedchi2[ilepton]) < 3       and
                         abs(self.itree.std_vector_lepton_d0[ilepton])      < 0.1               and
                         abs(self.itree.std_vector_lepton_dz[ilepton]) < 0.20                   and
                         self.itree.std_vector_electron_passConversionVeto[ilepton]             and
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<1     and
                         (self.itree.std_vector_lepton_chargedHadronIso[ilepton] \
                           +max(self.itree.std_vector_lepton_neutralHadronIso[ilepton] +  \
                                self.itree.std_vector_lepton_photonIso[ilepton] -  \
                                self.itree.jetRho*self.itree.std_vector_electron_effectiveArea[ilepton],0))/self.itree.std_vector_lepton_pt[ilepton]   <  0.0571
                         )
                 ))                
                ) : 
                  isThisATightLepton = 1
                  
           else :
             # id definition
             if ( self.itree.std_vector_lepton_eleIdTight[ilepton] == 1
                  and abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 
                  and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5
                 ) :
               isThisATightLepton = 1
            
            
           
           ###########
           # muon
           dxy = float(0.01)
           if (self.itree.std_vector_lepton_pt[ilepton] > 20):
               dxy = float(0.02)
           
           muonIso = float(0.0)
           
           if ( (self.itree.std_vector_lepton_photonIso[ilepton] +
                self.itree.std_vector_lepton_neutralHadronIso[ilepton] -
                0.5 * self.itree.std_vector_lepton_sumPUPt[ilepton]) > 0
                ) :
               muonIso = (self.itree.std_vector_lepton_photonIso[ilepton] +
                          self.itree.std_vector_lepton_neutralHadronIso[ilepton] -
                          0.5 * self.itree.std_vector_lepton_sumPUPt[ilepton])
           else:
               muonIso = 0
           
           if self.cmssw == '763':
             if ( self.itree.std_vector_lepton_isMediumMuon[ilepton] == 1 
                and (self.itree.std_vector_lepton_chargedHadronIso[ilepton] + muonIso) / self.itree.std_vector_lepton_pt[ilepton] < 0.15
                and abs(self.itree.std_vector_lepton_flavour[ilepton]) == 13
                and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4
                and abs(self.itree.std_vector_lepton_d0[ilepton]) < dxy          # formerly std_vector_lepton_BestTrackdxy
                and abs(self.itree.std_vector_lepton_dz[ilepton]) < 0.1          # formerly std_vector_lepton_BestTrackdz
                and self.itree.std_vector_lepton_trackIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.4
                ) :
               isThisATightLepton = 1
               
           elif self.cmssw == 'ICHEP2016' or self.cmssw == 'Rereco2016' or self.cmssw == 'Full2016' :
             if ( self.itree.std_vector_lepton_isTightMuon[ilepton] == 1 
                and (self.itree.std_vector_lepton_chargedHadronIso[ilepton] + muonIso) / self.itree.std_vector_lepton_pt[ilepton] < 0.15
                and abs(self.itree.std_vector_lepton_flavour[ilepton]) == 13
                and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4
                and abs(self.itree.std_vector_lepton_d0[ilepton]) < dxy          # formerly std_vector_lepton_BestTrackdxy
                and abs(self.itree.std_vector_lepton_dz[ilepton]) < 0.1          # formerly std_vector_lepton_BestTrackdz
                and self.itree.std_vector_lepton_trackIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.4
                ) :
               isThisATightLepton = 1               
           else :
             if ( self.itree.std_vector_lepton_isMediumMuon[ilepton] == 1 
                and (self.itree.std_vector_lepton_chargedHadronIso[ilepton] + muonIso) / self.itree.std_vector_lepton_pt[ilepton] < 0.15
                and abs(self.itree.std_vector_lepton_flavour[ilepton]) == 13
                and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4
                and abs(self.itree.std_vector_lepton_BestTrackdxy[ilepton]) < dxy    
                and abs(self.itree.std_vector_lepton_BestTrackdz[ilepton]) < 0.1     
                ) :
               isThisATightLepton = 1
    
       return isThisATightLepton




    def isWgsLepton(self, ilepton) :

       isThisAWgsLepton = 0
       
       #
       # Wg* lepton definition
       #    - remove from isolation cone the lepton pt component
       #

       if self.itree.std_vector_lepton_pt[ilepton] > 0 :
        
           ###########
           # electron
           
           # id definition
           if self.cmssw == '763' :               
           
             if (
                abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 
                and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5
                and self.itree.std_vector_electron_hcalPFClusterIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.25 
                and 
                 ((
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.479) 
                 and    (abs(self.itree.std_vector_electron_dEtaIn[ilepton]) < 0.01               and
                         abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.04               and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.011              and
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.08               and
                         self.itree.std_vector_electron_ooEmooP[ilepton] < 0.01               and 
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<=2  and
                         self.itree.std_vector_lepton_d0[ilepton]      < 0.1                and
                         abs(self.itree.std_vector_lepton_dz[ilepton])< 0.373              and
                         self.itree.std_vector_electron_passConversionVeto[ilepton] )
                 )
                 or 
                 (
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) > 1.479 and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5)
                 and    (abs(self.itree.std_vector_electron_dEtaIn[ilepton]) < 0.01               and
                         abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.08               and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.031              and
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.08               and
                         self.itree.std_vector_electron_ooEmooP[ilepton] < 0.01               and
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<=1  and
                         self.itree.std_vector_lepton_d0[ilepton]      < 0.2                and
                         abs(self.itree.std_vector_lepton_dz[ilepton])< 0.602              and
                         self.itree.std_vector_electron_passConversionVeto[ilepton] )
                 ))
                ) : 
                  isThisAWgsLepton = 1

           elif self.cmssw == 'ICHEP2016' or self.cmssw == 'Rereco2016' or self.cmssw == 'Full2016' :               
             #
             # see https://indico.cern.ch/event/491507/contributions/2192817/attachments/1285452/1911768/EGM_HLTsafeCuts_31May16.pdf
             #
             if (
                abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 
                and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5
                and self.itree.std_vector_lepton_trackIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.08                
                and
                ((
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.479) 
                 and    (
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.060        and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.011   and
                         abs(self.itree.std_vector_electron_dEtaSeedCalo[ilepton])  < 0.004         and
                         abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.020                and
                         abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.013               and 
                         (self.itree.std_vector_electron_ecalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.165)/self.itree.std_vector_lepton_pt[ilepton] < 0.160   and
                         (self.itree.std_vector_electron_hcalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.060)/self.itree.std_vector_lepton_pt[ilepton] < 0.120   and
                         abs(self.itree.std_vector_lepton_d0[ilepton]) < 0.1                  and
                         abs(self.itree.std_vector_lepton_dz[ilepton])< 0.373                 and
                         self.itree.std_vector_electron_passConversionVeto[ilepton]           and
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<1  
                         )
                 )
                 or 
                 (
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) > 1.479 and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5)
                 and    (
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.060            and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.031       and
                         abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.013                   and 
                         (self.itree.std_vector_electron_ecalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.132)/self.itree.std_vector_lepton_pt[ilepton] < 0.120   and
                         (self.itree.std_vector_electron_hcalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.131)/self.itree.std_vector_lepton_pt[ilepton] < 0.120   and
                         abs(self.itree.std_vector_electron_gsfnormalizedchi2[ilepton]) < 3       and
                         abs(self.itree.std_vector_lepton_d0[ilepton]) < 0.2               and
                         abs(self.itree.std_vector_lepton_dz[ilepton])< 0.602              and
                         self.itree.std_vector_electron_passConversionVeto[ilepton]        and
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<1 
                         )
                 ))
                ) : 
                  isThisAWgsLepton = 1
                  
                  
           else : # 74X cmssw release
             if (
                abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 
                and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5
                and 
                 ((
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.479) 
                 and    (abs(self.itree.std_vector_electron_dEtaIn[ilepton]) < 0.01               and
                         abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.04               and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.011              and
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.08               and
                         self.itree.std_vector_electron_ooEmooP[ilepton] < 0.01               and 
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<=2  and
                         self.itree.std_vector_electron_d0[ilepton]      < 0.1                and
                         abs(self.itree.std_vector_electron_dz[ilepton])< 0.373              and
                         self.itree.std_vector_electron_passConversionVeto[ilepton] )
                 )
                 or 
                 (
                 (abs(self.itree.std_vector_lepton_eta[ilepton]) > 1.479 and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5)
                 and    (abs(self.itree.std_vector_electron_dEtaIn[ilepton]) < 0.01               and
                         abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.08               and
                         self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.031              and
                         self.itree.std_vector_electron_hOverE[ilepton]              < 0.08               and
                         self.itree.std_vector_electron_ooEmooP[ilepton] < 0.01               and
                         self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<=1  and
                         self.itree.std_vector_electron_d0[ilepton]      < 0.2                and
                         abs(self.itree.std_vector_electron_dz[ilepton])< 0.602              and
                         self.itree.std_vector_electron_passConversionVeto[ilepton] )
                 ))
                ) : 
                  isThisAWgsLepton = 1 

           
           ###########
           # muon
           dxy = float(0.01)
           if (self.itree.std_vector_lepton_pt[ilepton] > 20):
               dxy = float(0.02)
           
           muonIso = float(0.0)
           
           if ( (self.itree.std_vector_lepton_photonIso[ilepton] +
                self.itree.std_vector_lepton_neutralHadronIso[ilepton] -
                0.5 * self.itree.std_vector_lepton_sumPUPt[ilepton]) > 0
                ) :
               muonIso = (self.itree.std_vector_lepton_photonIso[ilepton] +
                          self.itree.std_vector_lepton_neutralHadronIso[ilepton] -
                          0.5 * self.itree.std_vector_lepton_sumPUPt[ilepton])
           else:
               muonIso = 0
    
           # isolation cone removal
           pt_to_be_removed_from_overlap = 0
    
           for jlepton in xrange(len(self.itree.std_vector_lepton_pt)) :
             if jlepton != ilepton :
               if self.itree.std_vector_lepton_pt[jlepton] > 0 :                 
                 if self.isAcloseToB(self.itree.std_vector_lepton_eta[jlepton], self.itree.std_vector_lepton_phi[jlepton],
                                     self.itree.std_vector_lepton_eta[ilepton], self.itree.std_vector_lepton_phi[ilepton],
                                     0.3) :
                   pt_to_be_removed_from_overlap += self.itree.std_vector_lepton_pt[jlepton]
          
           if self.cmssw == '763' :
             if ( self.itree.std_vector_lepton_isMediumMuon[ilepton] == 1 
                and (self.itree.std_vector_lepton_chargedHadronIso[ilepton] + muonIso - pt_to_be_removed_from_overlap) / self.itree.std_vector_lepton_pt[ilepton] < 0.15
                and abs(self.itree.std_vector_lepton_flavour[ilepton]) == 13
                and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4
                and abs(self.itree.std_vector_lepton_d0[ilepton]) < dxy          # formerly std_vector_lepton_BestTrackdxy
                and abs(self.itree.std_vector_lepton_dz[ilepton]) < 0.1          # formerly std_vector_lepton_BestTrackdz
                ) :
               isThisAWgsLepton = 1

           elif self.cmssw == 'ICHEP2016' or self.cmssw == 'Rereco2016' or self.cmssw == 'Full2016' :
             if ( self.itree.std_vector_lepton_isTightMuon[ilepton] == 1 
                and (self.itree.std_vector_lepton_chargedHadronIso[ilepton] + muonIso - pt_to_be_removed_from_overlap) / self.itree.std_vector_lepton_pt[ilepton] < 0.15
                and abs(self.itree.std_vector_lepton_flavour[ilepton]) == 13
                and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4
                and abs(self.itree.std_vector_lepton_d0[ilepton]) < dxy          # formerly std_vector_lepton_BestTrackdxy
                and abs(self.itree.std_vector_lepton_dz[ilepton]) < 0.1          # formerly std_vector_lepton_BestTrackdz
                ) :
               isThisAWgsLepton = 1
           else :
             if ( self.itree.std_vector_lepton_isMediumMuon[ilepton] == 1 
                and (self.itree.std_vector_lepton_chargedHadronIso[ilepton] + muonIso - pt_to_be_removed_from_overlap) / self.itree.std_vector_lepton_pt[ilepton] < 0.15
                and abs(self.itree.std_vector_lepton_flavour[ilepton]) == 13
                and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4
                and abs(self.itree.std_vector_lepton_BestTrackdxy[ilepton]) < dxy    
                and abs(self.itree.std_vector_lepton_BestTrackdz[ilepton]) < 0.1     
                ) :
               isThisAWgsLepton = 1
    
       return isThisAWgsLepton





    def isVeryLooseLepton(self, ilepton) :
       
       # denominator of fakes definition
       isThisAVeryLooseLepton = 0
       if self.itree.std_vector_lepton_pt[ilepton] > 0 :
            
            if self.cmssw == 'ICHEP2016' :
            
                ###########
                # electron        
                # id definition 
                if (
                    abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 
                    and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5
                    and
                    ((
                    (abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.479) 
                    and    (
                            self.itree.std_vector_electron_hOverE[ilepton]              < 0.060        and
                            self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.011   and
                            abs(self.itree.std_vector_electron_dEtaSeedCalo[ilepton])  < 0.004         and
                            abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.020                and
                            abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.013               and 
                            abs(self.itree.std_vector_lepton_d0[ilepton])< 0.5                  and
                            abs(self.itree.std_vector_lepton_dz[ilepton])< 1.                   and
                            self.itree.std_vector_electron_passConversionVeto[ilepton]           and
                            self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<1
                            )
                    )
                    or 
                    (
                    (abs(self.itree.std_vector_lepton_eta[ilepton]) > 1.479 and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5)
                    and    (
                            self.itree.std_vector_electron_hOverE[ilepton]              < 0.060            and
                            self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.031       and
                            abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.013                   and 
                            abs(self.itree.std_vector_electron_gsfnormalizedchi2[ilepton]) < 3       and
                            abs(self.itree.std_vector_lepton_d0[ilepton])< 0.5               and
                            abs(self.itree.std_vector_lepton_dz[ilepton])< 1.                and
                            self.itree.std_vector_electron_passConversionVeto[ilepton]        and
                            self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<1 
                            )
                    ))
                ) : 
                        isThisAVeryLooseLepton = 1
                        
            elif self.cmssw == 'Full2016' :                 
             # HLT safe
             #
             if abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5:
                if self.itree.std_vector_lepton_eleIdHLT[ilepton] :
                    isThisAVeryLooseLepton = 1
                    
            elif self.cmssw == 'Rereco2016' :               
             #
             # HLT + very loose d0 and dz cuts
             #
                if (
                    abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 
                    and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5
                    and self.itree.std_vector_lepton_trackIso[ilepton]/self.itree.std_vector_lepton_pt[ilepton] < 0.08                
                    and
                    ((
                    (abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.479) 
                    and    (
                            self.itree.std_vector_electron_hOverE[ilepton]              < 0.060        and
                            self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.011   and
                            abs(self.itree.std_vector_electron_dEtaIn[ilepton])  < 0.004         and
                            abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.020                and
                            abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.013               and 
                            (self.itree.std_vector_electron_ecalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.165)/self.itree.std_vector_lepton_pt[ilepton] < 0.160   and
                            (self.itree.std_vector_electron_hcalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.060)/self.itree.std_vector_lepton_pt[ilepton] < 0.120   and
                            abs(self.itree.std_vector_lepton_d0[ilepton])      < 0.5                  and
                            abs(self.itree.std_vector_lepton_dz[ilepton]) < 1.
                            )
                    )
                    or 
                    (
                    (abs(self.itree.std_vector_lepton_eta[ilepton]) > 1.479 and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5)
                    and    (
                            self.itree.std_vector_electron_hOverE[ilepton]              < 0.065            and
                            self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.031       and
                            abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.013                   and 
                            (self.itree.std_vector_electron_ecalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.132)/self.itree.std_vector_lepton_pt[ilepton] < 0.120   and
                            (self.itree.std_vector_electron_hcalPFClusterIso[ilepton] - self.itree.jetRhoCalo * 0.131)/self.itree.std_vector_lepton_pt[ilepton] < 0.120   and
                            abs(self.itree.std_vector_electron_gsfnormalizedchi2[ilepton]) < 3       and
                            abs(self.itree.std_vector_lepton_d0[ilepton])      < 0.5               and
                            abs(self.itree.std_vector_lepton_dz[ilepton]) < 1.
                            )
                    ))                
                  ) : 
                  isThisAVeryLooseLepton = 1
                  
            else:      
                if (
                        abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 
                        and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5
                        and 
                        ((
                        (abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.479) 
                        and    (abs(self.itree.std_vector_electron_dEtaIn[ilepton]) < 0.01               and
                                abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.04               and
                                self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.011              and
                                self.itree.std_vector_electron_hOverE[ilepton]              < 0.08               and
                                self.itree.std_vector_electron_ooEmooP[ilepton] < 0.01               and 
                                self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<=2  and
                                self.itree.std_vector_lepton_d0[ilepton]      < 0.5                and
                                abs(self.itree.std_vector_lepton_dz[ilepton])< 1.              and
                                self.itree.std_vector_electron_passConversionVeto[ilepton] )
                        )
                        or 
                        (
                        (abs(self.itree.std_vector_lepton_eta[ilepton]) > 1.479 and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.5)
                        and    (abs(self.itree.std_vector_electron_dEtaIn[ilepton]) < 0.01               and
                                abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.08               and
                                self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.031              and
                                self.itree.std_vector_electron_hOverE[ilepton]              < 0.08               and
                                self.itree.std_vector_electron_ooEmooP[ilepton] < 0.01               and
                                self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<=1  and
                                self.itree.std_vector_lepton_d0[ilepton]      < 0.5                and
                                abs(self.itree.std_vector_lepton_dz[ilepton])< 1.              and
                                self.itree.std_vector_electron_passConversionVeto[ilepton] )
                        ))
                    ) : 
                        isThisAVeryLooseLepton = 1
                
            ###########
            # muon        
            if self.cmssw == 'Rereco2016' : 
                if ( abs(self.itree.std_vector_lepton_flavour[ilepton]) == 13
                    and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4
                    and abs(self.itree.std_vector_lepton_d0[ilepton]) < 0.5          # formerly std_vector_lepton_BestTrackdxy
                    and abs(self.itree.std_vector_lepton_dz[ilepton]) < 1.          # formerly std_vector_lepton_BestTrackdz
                    and (self.itree.std_vector_lepton_chargedHadronIso[ilepton] \
                            +max(self.itree.std_vector_lepton_neutralHadronIso[ilepton] +  \
                                    self.itree.std_vector_lepton_photonIso[ilepton] -  \
                                    0.5 * self.itree.std_vector_lepton_sumPUPt[ilepton],0))/self.itree.std_vector_lepton_pt[ilepton]   <  1.0
                ) :
                    isThisAVeryLooseLepton = 1 
                    
            elif self.cmssw == 'Full2016' : 
                if ( abs(self.itree.std_vector_lepton_flavour[ilepton]) == 13
                    and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4
                    and self.itree.std_vector_lepton_isMediumMuon[ilepton] == 1
                    #and abs(self.itree.std_vector_lepton_d0[ilepton]) < 0.5          # formerly std_vector_lepton_BestTrackdxy
                    #and abs(self.itree.std_vector_lepton_dz[ilepton]) < 1.          # formerly std_vector_lepton_BestTrackdz
                    and (self.itree.std_vector_lepton_chargedHadronIso[ilepton] \
                            +max(self.itree.std_vector_lepton_neutralHadronIso[ilepton] +  \
                                    self.itree.std_vector_lepton_photonIso[ilepton] -  \
                                    0.5 * self.itree.std_vector_lepton_sumPUPt[ilepton],0))/self.itree.std_vector_lepton_pt[ilepton]   <  0.6
                ) :
                    isThisAVeryLooseLepton = 1 
                
            else:            
                if ( abs(self.itree.std_vector_lepton_flavour[ilepton]) == 13
                        and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4
                        and abs(self.itree.std_vector_lepton_d0[ilepton]) < 0.5          # formerly std_vector_lepton_BestTrackdxy
                        and abs(self.itree.std_vector_lepton_dz[ilepton]) < 1.          # formerly std_vector_lepton_BestTrackdz
                ) :
                    isThisAVeryLooseLepton = 1
           
       return isThisAVeryLooseLepton

    def passMultiIso(self, ilepton, MultiIsoCut) :
   
        IsoRadius = 0.2
        if (self.itree.std_vector_lepton_pt[ilepton]>=50. and self.itree.std_vector_lepton_pt[ilepton]<200.):
            IsoRadius = 10./self.itree.std_vector_lepton_pt[ilepton]
        elif self.itree.std_vector_lepton_pt[ilepton]>=200. :
            IsoRadius = 0.05
            
        EffArea = 1.;
        if abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 :
            if abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.000 :
                EffArea = 0.1752
            elif abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.479 :
                EffArea = 0.1862
            elif abs(self.itree.std_vector_lepton_eta[ilepton]) <= 2.000 :
                EffArea = 0.1411
            elif abs(self.itree.std_vector_lepton_eta[ilepton]) <= 2.200 :
                EffArea = 0.1534
            elif abs(self.itree.std_vector_lepton_eta[ilepton]) <= 2.300 :
                EffArea = 0.1903
            elif abs(self.itree.std_vector_lepton_eta[ilepton]) <= 2.400 :
                EffArea = 0.2243
            elif abs(self.itree.std_vector_lepton_eta[ilepton]) <= 2.500 :
                EffArea = 0.2687
        elif abs(self.itree.std_vector_lepton_flavour[ilepton]) == 13 :
            if abs(self.itree.std_vector_lepton_eta[ilepton]) <= 0.800 :
                EffArea = 0.0735
            elif abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.300 :
                EffArea = 0.0619
            elif abs(self.itree.std_vector_lepton_eta[ilepton]) <= 2.000 :
                EffArea = 0.0465
            elif abs(self.itree.std_vector_lepton_eta[ilepton]) <= 2.200 :
                EffArea = 0.0433
            elif abs(self.itree.std_vector_lepton_eta[ilepton]) <= 2.500 :
                EffArea = 0.0577
                   
        NeutralMiniIso = self.itree.std_vector_lepton_neutralHadronMiniIso[ilepton] + self.itree.std_vector_lepton_photonMiniIso[ilepton] - self.itree.jetRho*EffArea*(IsoRadius/0.3)*(IsoRadius/0.3)
        if NeutralMiniIso < 0. :
            NeutralMiniIso = 0.
        MiniIso = (self.itree.std_vector_lepton_chargedHadronMiniIso[ilepton] + NeutralMiniIso)/self.itree.std_vector_lepton_pt[ilepton]
           
        MinDR2 = 0.4*0.4
        closestJet = -1
        for iJet in xrange(len(self.itree.std_vector_jet_pt)) :
            dPhi = ROOT.TMath.Abs(self.itree.std_vector_lepton_phi[ilepton] - self.itree.std_vector_jet_phi[iJet])
            if dPhi > ROOT.TMath.Pi() :
                dPhi = 2*ROOT.TMath.Pi() - dPhi
            dR2 = (self.itree.std_vector_lepton_eta[ilepton] - self.itree.std_vector_jet_eta[iJet]) * (self.itree.std_vector_lepton_eta[ilepton] - self.itree.std_vector_jet_eta[iJet]) + dPhi * dPhi
            if dR2 < MinDR2:
                closestJet = iJet
                MinDR2 = dR2
           
        LepPtRatio = 1.
        LepPtRel = 10.
           
        if closestJet >= 0:
            vlep = TVector3()
            vlep.SetPtEtaPhi(self.itree.std_vector_lepton_pt[ilepton], self.itree.std_vector_lepton_eta[ilepton], self.itree.std_vector_lepton_phi[ilepton])
            vjet = TVector3()
            vjet.SetPtEtaPhi(self.itree.std_vector_jet_pt_raw[closestJet], self.itree.std_vector_jet_eta[closestJet], self.itree.std_vector_jet_phi[closestJet])
            jecL1L2L3Res = self.itree.std_vector_jet_pt[closestJet]/self.itree.std_vector_jet_pt_raw[closestJet]
            ###jecL2L3Res = self.itree.std_vector_jet_pt[closestJet]/self.itree.std_vector_jet_pt_L3Absolute[closestJet]
            jecL1 = self.itree.std_vector_jet_pt_L1[closestJet]/self.itree.std_vector_jet_pt_raw[closestJet]
            #vjet = vjet*(1./jecL1L2L3Res)
            vjet = vjet - vlep*(1./jecL1)
            vjet = vjet*jecL1L2L3Res
            ##vjet = vjet*jecL1 - vlep
            ##vjet = vjet*jecL1L2L3Res*1./jecL1
            ###vjet = vjet*jecL2L3Res
            vjet = vjet + vlep
            LepPtRatio = vlep.Pt()/vjet.Pt()
            vjet = vjet - vlep
            LepPtRel = vlep.Perp(vjet)
            
        if MultiIsoCut == 0:   
            if (MiniIso<0.25 and (LepPtRatio>0.67 or LepPtRel>4.4) ) :
                return True
        elif MultiIsoCut == 1:    
            if (MiniIso<0.20 and (LepPtRatio>0.69 or LepPtRel>6.0) ) :
                return True 
        elif MultiIsoCut == 2:    
            if (MiniIso<0.16 and (LepPtRatio>0.76 or LepPtRel>7.2) ) :
                return True 
        elif MultiIsoCut == 3:    
            if (MiniIso<0.12 and (LepPtRatio>0.80 or LepPtRel>7.2) ) :
                return True 
        else:
            if (MiniIso<0.09 and (LepPtRatio>0.84 or LepPtRel>7.2) ) :
                return True 

        return False
 

    def passRelIso(self, ilepton, IsolationCut) :

           neutralIsoCorrection = 0
           if abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 :
               neutralIsoCorrection = 0
           elif abs(self.itree.std_vector_lepton_flavour[ilepton]) == 13 :
                neutralIsoCorrection = 0.5 * self.itree.std_vector_lepton_sumPUPt[ilepton]
           else :
               return False

           neutralIso = (self.itree.std_vector_lepton_photonIso[ilepton] + 
                         self.itree.std_vector_lepton_neutralHadronIso[ilepton] -
                         neutralIsoCorrection)

           if neutralIso < 0. :
               neutralIso = 0.
           
           RelIso = (self.itree.std_vector_lepton_chargedHadronIso[ilepton] + neutralIso) / self.itree.std_vector_lepton_pt[ilepton]

           RelIsoCut = 0.12
           if IsolationCut == 0 :
               RelIsoCut = 0.4

           if RelIso < RelIsoCut :
               return True

           return False


    def isStopLepton(self, ilepton, IsolationCut) :
                      
        isThisAStopLepton = 0

        if self.itree.std_vector_lepton_pt[ilepton] > 0 :
            
            isIsolatedLepton = True
            if self.cmssw == 'ICHEP2016' :
               isIsolatedLepton = self.passMultiIso(ilepton, IsolationCut)
            elif self.cmssw == 'Rereco2016' :
                isIsolatedLepton = self.passRelIso(ilepton, IsolationCut)
            if isIsolatedLepton == False :
                return 0    

            ###########
            # electron    
            if (abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 ): 

                if self.cmssw == 'ICHEP2016' :
                    # id definition (tight cut-based  extra cuts: https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Spring15_selection_25ns)
                    if (abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4
                        and (abs(self.itree.std_vector_electron_scEta[ilepton])<=1.4442
                             or abs(self.itree.std_vector_electron_scEta[ilepton])>=1.566)
                        and
                        ((
                                (abs(self.itree.std_vector_electron_scEta[ilepton]) <= 1.479) 
                                and    (
                                    self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.0101  and
                                    abs(self.itree.std_vector_electron_dEtaIn[ilepton]) < 0.00926              and
                                    abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.0336               and
                                    self.itree.std_vector_electron_hOverE[ilepton]       < 0.0597              and
                                    abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.012               and 
                                    abs(self.itree.std_vector_lepton_d0[ilepton])< 0.050                       and # 0.0111
                                    abs(self.itree.std_vector_lepton_dz[ilepton])< 0.100                       and # 0.0466
                                    self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<1         and # <=2
                                    self.itree.std_vector_electron_passConversionVeto[ilepton]                 and
                                    abs(self.itree.std_vector_lepton_SIP3D[ilepton])<4.                            #not POG
                                    )
                                )
                         or 
                         (
                                (abs(self.itree.std_vector_electron_scEta[ilepton]) > 1.479)
                                and    (
                                    self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]    < 0.0279  and
                                    abs(self.itree.std_vector_electron_dEtaIn[ilepton]) < 0.00724              and
                                    abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.0918               and
                                    self.itree.std_vector_electron_hOverE[ilepton]       < 0.0615              and
                                    abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.00999             and 
                                    abs(self.itree.std_vector_lepton_d0[ilepton])< 0.050                       and # 0.0351
                                    abs(self.itree.std_vector_lepton_dz[ilepton])< 0.100                       and # 0.417
                                    self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<1         and # <=2
                                    self.itree.std_vector_electron_passConversionVeto[ilepton]                 and 
                                    abs(self.itree.std_vector_lepton_SIP3D[ilepton])<4.                            # not POG
                                    )
                                ))
                        ) : 
                        isThisAStopLepton = 1

                elif self.cmssw == 'Rereco2016' :

                    if self.kind == 5 :  
                        # id definition (tight cut-based plus extra cuts: https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Working_points_for_2016_data_for
                        # What about https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#HLT_safe_selection_for_2016_data ?
                        if (and abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4
                            and (abs(self.itree.std_vector_electron_scEta[ilepton])<=1.4442
                                 or abs(self.itree.std_vector_electron_scEta[ilepton])>=1.566)
                            and ((
                                    (abs(self.itree.std_vector_electron_scEta[ilepton]) <= 1.479)
                                    and (
                                        self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]   < 0.00998  and
                                        abs(self.itree.std_vector_electron_dEtaSeedCalo[ilepton]) < 0.00308        and # check this variable
                                        abs(self.itree.std_vector_electron_dPhiIn[ilepton])  < 0.0816              and
                                        self.itree.std_vector_electron_hOverE[ilepton]       < 0.0414              and
                                        abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.0129              and 
                                        self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]<1         and # <=1
                                        self.itree.std_vector_electron_passConversionVeto[ilepton]                 and
                                        ((abs(self.itree.std_vector_lepton_d0[ilepton])< 0.05                      and # not POG/0.05
                                          abs(self.itree.std_vector_lepton_dz[ilepton])< 0.10                      and # not POG/0.10         
                                          abs(self.itree.std_vector_lepton_SIP3D[ilepton])<4.                          # not POG
                                          ) or (IsolationCut == 0))
                                        )
                                    )
                                 or 
                                 (
                                    (abs(self.itree.std_vector_electron_scEta[ilepton]) > 1.479)
                                    and (
                                        self.itree.std_vector_electron_full5x5_sigmaIetaIeta[ilepton]   < 0.0292   and
                                        abs(self.itree.std_vector_electron_dEtaSeedCalo[ilepton]) < 0.00605        and # check this variable
                                        abs(self.itree.std_vector_electron_dPhiIn[ilepton]) < 0.0394               and
                                        self.itree.std_vector_electron_hOverE[ilepton]       < 0.0641              and
                                        abs(self.itree.std_vector_electron_ooEmooP[ilepton]) < 0.0129              and 
                                        self.itree.std_vector_electron_expectedMissingInnerHits[ilepton]< 1        and # <=1
                                        self.itree.std_vector_electron_passConversionVeto[ilepton]                 and 
                                        ((abs(self.itree.std_vector_lepton_d0[ilepton])< 0.05                      and # not POG/0.10
                                          abs(self.itree.std_vector_lepton_dz[ilepton])< 0.10                      and # not POG/0.20       
                                          abs(self.itree.std_vector_lepton_SIP3D[ilepton])<4.                          # not POG
                                          ) or (IsolationCut == 0))
                                        )
                                    ))
                            ) : 
                            isThisAStopLepton = 1
                       
                    elif self.kind == 6:
                        # https://twiki.cern.ch/twiki/bin/view/CMS/SUSLeptonSF#Electrons
                        if (abs(self.itree.std_vector_lepton_flavour[ilepton]) == 11 and
                            abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4 and
                            self.itree.std_vector_lepton_pt[ilepton] > 10.) :
                            MVACut = 999.                     
                            if abs(self.itree.std_vector_lepton_eta[ilepton]) <= 0.8 :
                                CutA =  0.77
                                CutB =  0.52
                                MVACut = min( CutA, max( CutB, CutA - ((CutA - CutB)/10.)*(self.itree.std_vector_lepton_pt[ilepton] - 15.) ))
                            elif abs(self.itree.std_vector_lepton_eta[ilepton]) <= 1.479 :
                                CutA =  0.56
                                CutB =  0.11
                                MVACut = min( CutA, max( CutB, CutA - ((CutA - CutB)/10.)*(self.itree.std_vector_lepton_pt[ilepton] - 15.) ))
                            elif abs(self.itree.std_vector_lepton_eta[ilepton]) <= 2.5 :
                                CutA =  0.48
                                CutB = -0.01
                                MVACut = min( CutA, max( CutB, CutA - ((CutA - CutB)/10.)*(self.itree.std_vector_lepton_pt[ilepton] - 15.) ))
                                if self.itree.std_vector_lepton_eleIdMvaValue[ilepton] > MVACut :
                                    if ((abs(self.itree.std_vector_lepton_d0[ilepton])< 0.05 and
                                         abs(self.itree.std_vector_lepton_dz[ilepton])< 0.10 and
                                         abs(self.itree.std_vector_lepton_SIP3D[ilepton])<4.                         
                                         ) or (IsolationCut == 0)) :
                                        isThisAStopLepton = 1
                                        
            ###########
            # muon
            elif ( abs(self.itree.std_vector_lepton_flavour[ilepton]) == 13  ) :

                if self.cmssw == 'ICHEP2016' : 
                    # https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2#Short_Term_Instructions_for_ICHE
                    if ( abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4        and
                         # It should be already a loose at this point
                         self.itree.std_vector_muon_NValidFractInTrk[ilepton]>0.8    and # Was it 0.49?
                         ((self.itree.std_vector_muon_NormChi2GTrk[ilepton]>0.       and # As asking isGlobalMuon?
                           self.itree.std_vector_muon_NormChi2GTrk[ilepton]<3.       and
                           self.itree.std_vector_muon_Chi2LocalPos[ilepton]<12.      and
                           self.itree.std_vector_muon_TrkKink[ilepton]<20.           and
                           self.itree.std_vector_muon_SegCompatibilty[ilepton]>0.303
                           )
                          or
                          (self.itree.std_vector_muon_SegCompatibilty[ilepton]>0.451
                           )
                          ) and
                         abs(self.itree.std_vector_lepton_d0[ilepton]) < 0.05        and  # not POG       
                         abs(self.itree.std_vector_lepton_dz[ilepton]) < 0.1         and  # not POG
                         abs(self.itree.std_vector_lepton_SIP3D[ilepton])<4.              # not POG 
                         ):
                        isThisAStopLepton = 1
                   
                elif self.cmssw == 'Rereco2016' : 
                    # https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2#Short_Term_Instructions_for_Mori
                    if ( abs(self.itree.std_vector_lepton_eta[ilepton]) < 2.4 ) :        
                        goodGlob = (self.itree.std_vector_muon_NormChi2GTrk[ilepton]>0.       and # As asking isGlobalMuon?
                                    self.itree.std_vector_muon_NormChi2GTrk[ilepton]<3.       and
                                    self.itree.std_vector_muon_Chi2LocalPos[ilepton]<12.      and
                                    self.itree.std_vector_muon_TrkKink[ilepton]<20.           and
                                    self.itree.std_vector_muon_SegCompatibilty[ilepton]>0.303)
                        validTrackerHitFractionCut = 0.8 # Run2016G and Run2016H (and MC)
                        if ( self.itree.run>271036 and self.itree.run<278820 ) : # Run2016B to Run2016F 
                            validTrackerHitFractionCut = 0.49 # SUSY decided to stay with 0.8 also for BCDEF
                        if ( self.itree.std_vector_muon_NValidFractInTrk[ilepton]>validTrackerHitFractionCut and 
                             (goodGlob or self.itree.std_vector_muon_SegCompatibilty[ilepton]>0.451) # POG
                             and ((abs(self.itree.std_vector_lepton_d0[ilepton])< 0.05        and    # not POG        
                                   abs(self.itree.std_vector_lepton_dz[ilepton])< 0.1         and    # not POG
                                   abs(self.itree.std_vector_lepton_SIP3D[ilepton])<4.               # not POG 
                                   ) or (IsolationCut == 0))
                             ):
                            isThisAStopLepton = 1

        return isThisAStopLepton

                    
                    
    def process(self,**kwargs):
        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        # does that work so easily and give new variable itree and otree?
        self.connect(tree,input)

        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 
        savedentries = 0

        #
        # create branches for otree, the ones that will be modified!
        # see: https://root.cern.ch/phpBB3/viewtopic.php?t=12507
        # this is the list of variables to be modified
        # either because leptons are filtered by id/iso, 
        # or because jets are filtered because they are actually leptons
        #
        self.namesOldBranchesToBeModifiedVector = []
        vectorsToChange = ['std_vector_lepton_','std_vector_electron_','std_vector_muon_','std_vector_jet_','std_vector_puppijet_']
        for b in self.itree.GetListOfBranches():
            branchName = b.GetName()
            for subString in vectorsToChange:
                if subString in branchName:
                    self.namesOldBranchesToBeModifiedVector.append(branchName)
        
        
        # new branches to be added as std_vector
        self.namesNewBranchesVector = ['std_vector_lepton_isLooseLepton', 'std_vector_lepton_isTightLepton', 'std_vector_lepton_isWgsLepton']        
        


        # and these variables NEED to be defined as functions in WWVar.C
        # e.g. mll, dphill, ...
        self.namesOldBranchesToBeModifiedSimpleVariable = [
           'mll',
           'dphill',
           'yll',
           'ptll',
           'pt1',
           'pt2',
           'mth',
           'mcoll',
           'channel',
           #'pfmet',
           'projpfmet',

           'drll',
           'dphilljet',
           'dphilljetjet',
           'dphilmet',
           'dphilmet1',
           'dphilmet2',
           'mtw1',
           'mtw2',
           
           'mjj',
           'detajj',
           'njet',
           
           'mllThird'
           
           ]

        self.namesOfSpecialSimpleVariable = [
           'metFilter',
           'dmZllRecoMuon'
        ]
        
        
        
        # jet variables with the structure "std_vector_jet_"NAME to be migrated to "jet"NAME"+number.
        # e.g. jetpt1, jeteta1, jetpt2, jeteta2, ...
        self.jetVariables = [
            'pt',
            'eta',
            'phi',
            'mass',
            #'mva',
            #'id',
            'tche'       
            # NChgQC, ChgptCut1, NHM, NNeutralptCut, PhM, bjpb, ... ?
            # jetRho ?
            ]
        
        self.jetVarList = []
        # maximum number of "single jet" variables to be saved
        maxnjets = 2 # 7 --> everything is available in form of std::vector -> these will be deprecated
        for jetVar in self.jetVariables:
          for i in xrange(maxnjets):
            self.jetVarList.append("jet"+jetVar+str(i+1))

        # clone the tree
        self.clone(output,self.namesOldBranchesToBeModifiedVector + self.namesOldBranchesToBeModifiedSimpleVariable + self.namesOfSpecialSimpleVariable + self.jetVarList + self.namesNewBranchesVector)


        self.oldBranchesToBeModifiedVector = {}
        for bname in self.namesOldBranchesToBeModifiedVector:
          bvector =  ROOT.std.vector(float) ()
          self.oldBranchesToBeModifiedVector[bname] = bvector

        # now actually connect the branches
        for bname, bvector in self.oldBranchesToBeModifiedVector.iteritems():
            #print " bname   = ", bname
            #print " bvector = ", bvector
            self.otree.Branch(bname,bvector)


        self.oldBranchesToBeModifiedSimpleVariable = {}
        for bname in self.namesOldBranchesToBeModifiedSimpleVariable:
          bvariable = numpy.ones(1, dtype=numpy.float32)
          self.oldBranchesToBeModifiedSimpleVariable[bname] = bvariable

        # now actually connect the branches
        for bname, bvariable in self.oldBranchesToBeModifiedSimpleVariable.iteritems():
            #print " bname   = ", bname
            #print " bvariable = ", bvariable
            self.otree.Branch(bname,bvariable,bname+'/F')


        self.oldBranchesToBeModifiedSpecialSimpleVariable = {}
        for bname in self.namesOfSpecialSimpleVariable:
          bvariable = numpy.ones(1, dtype=numpy.float32)
          self.oldBranchesToBeModifiedSpecialSimpleVariable[bname] = bvariable

        # now actually connect the branches
        for bname, bvariable in self.oldBranchesToBeModifiedSpecialSimpleVariable.iteritems():
            #print " bname   = ", bname
            #print " bvariable = ", bvariable
            self.otree.Branch(bname,bvariable,bname+'/F')


        self.jetVarDic = OrderedDict()
        for bname in self.jetVarList:
          bvariable = numpy.ones(1, dtype=numpy.float32)
          self.jetVarDic[bname] = bvariable

        # now actually connect the branches
        for bname, bvariable in self.jetVarDic.iteritems():
            #print " bname   = ", bname
            #print " bvariable = ", bvariable
            self.otree.Branch(bname,bvariable,bname+'/F')

        # keep loose leptons: copy in toto the list of leptons and variables
        #                     and change the name adding "loose" in it
        #self.looseLeptonVector = {}
        #looseLeptonCollections = ['std_vector_lepton_pt','std_vector_lepton_eta','std_vector_lepton_phi','std_vector_lepton_flavour']
        #for bname in looseLeptonCollections:
          #if bname in self.itree.GetListOfBranches():
            #bvector =  ROOT.std.vector(float) ()
            #self.looseLeptonVector[bname] = bvector
            #self.otree.Branch(bname.replace('lepton','looseLepton'), bvector)

        # new brances as std_vector
        self.newBranchesVector = {}
        for bname in self.namesNewBranchesVector:
          bvector =  ROOT.std.vector(float) ()
          self.newBranchesVector[bname] = bvector

        # now actually connect the branches
        for bname, bvector in self.newBranchesVector.iteritems():
          self.otree.Branch(bname,bvector)



        # input tree and output tree
        itree     = self.itree
        otree     = self.otree


        # change this part into correct path structure... 
        cmssw_base = os.getenv('CMSSW_BASE')
        try:
            ROOT.gROOT.LoadMacro(cmssw_base+'/src/LatinoAnalysis/Gardener/python/variables/WWVar.C+g')
        except RuntimeError:
            ROOT.gROOT.LoadMacro(cmssw_base+'/src/LatinoAnalysis/Gardener/python/variables/WWVar.C++g')


        #----------------------------------------------------------------------------------------------------
        print '- Starting eventloop'
        step = 5000

        # to be used later on in the code ...
        new_std_vector_jet_pt  = ROOT.std.vector(float) ()
        new_std_vector_jet_eta = ROOT.std.vector(float) ()

        new_std_vector_lepton_pt      = ROOT.std.vector(float) ()
        new_std_vector_lepton_eta     = ROOT.std.vector(float) ()
        new_std_vector_lepton_phi     = ROOT.std.vector(float) ()
        new_std_vector_lepton_flavour = ROOT.std.vector(float) ()

        #for i in xrange(2000):
        for i in xrange(nentries):

            itree.GetEntry(i)

            if i > 0 and i%step == 0.:
                print i,'events processed :: ', nentries

            # apply lepton id and isolation
            # and filter out unwanted leptons
            # putting pt of those leptons to -9999 GeV
            # and all other variables too set to the default -9999

            goodLeps = []
            goodLep1 = -1
            goodLep2 = -1
                        
            for iLep in xrange(len(itree.std_vector_lepton_pt)) :
              isGoodLepton = False
              
              #
              # analysis lepton definition
              #
              if self.kind == 1 :
 
                TightTag = self.isTightLepton(iLep)
                
                if TightTag == 1 :
                  isGoodLepton = True
              

              ##########################################
              # denominator of fakes definition
              if self.kind == 2 :
               
                LooseTag = self.isLooseLepton(iLep)
                
                if LooseTag == 1 :
                  isGoodLepton = True

              # denominator of fakes definition (end)
              ##########################################
 

              ##########################################
              # Wg* lepton definition
              #    - remove from isolation cone the lepton pt component
              #
              if self.kind == 3 :
               
                WgsTag = self.isWgsLepton(iLep)
                
                if WgsTag == 1 :
                  isGoodLepton = True

              ##########################################

              if self.kind == 4 :
               
                VeryLooseTag = self.isVeryLooseLepton(iLep)
                
                if VeryLooseTag == 1 :
                  isGoodLepton = True

              ##########################################

              if (self.kind == 5 or self.kind == 6):
               
                StopTag = self.isStopLepton(iLep, 4)
                
                if StopTag == 1 :
                  isGoodLepton = True
 
              # now check if we found 2 leptons        
                             
              if isGoodLepton :
                if goodLep1 < 0: 
                  goodLep1 = iLep
                elif goodLep2 < 0 :
                  goodLep2 = iLep
                goodLeps.append(iLep)
            
            
            #print " goodLep1 = ", goodLep1, 
            #print " goodLep2 = ", goodLep2
            
            # require at least 2 good leptons
            if goodLep1 >= 0 and goodLep2 >= 0 :
            
              # now filter the leptons list
              # [ x, - , - , x , x , x , - , - ]
              # [ x  x   x   x   -   -   -   - ]
              for bname, bvector in self.oldBranchesToBeModifiedVector.iteritems():
                bvector.clear()
             
              # prepare the new vectors removing unwanted positions
              for bname, bvector in self.oldBranchesToBeModifiedVector.iteritems():
                 if ("vector_lepton" in bname) or ("vector_electron" in bname) or ("vector_muon" in bname):
                     self.changeOrder( bname, bvector, goodLeps)            

              
              # fill the lepton id vectors
              maxNumLeptons = len(itree.std_vector_lepton_pt)
              for bname, bvector in self.newBranchesVector.iteritems():
                bvector.clear() 
                
                if bname == 'std_vector_lepton_isLooseLepton' :
                  for iLep in goodLeps :
                      if (self.kind == 5 or slf.kind == 6):
                          bvector.push_back (1)
                      else:
                          LooseTag = self.isLooseLepton(iLep)                   
                          bvector.push_back (LooseTag)
                  for remainingLep in range( maxNumLeptons - len(goodLeps) ) :
                      if (self.kind == 5 or self.kind == 6):
                          StopTagLoose = self.isStopLepton(len(goodLeps) + remainingLep, 0)
                          if StopTagLoose == 1:
                              bvector.push_back (1)
                          else:
                              bvector.push_back (-9999.)
                      else:
                          bvector.push_back ( -9999. )

                if bname == 'std_vector_lepton_isTightLepton' :
                  for iLep in goodLeps :
                      if (self.kind == 5 or self.kind == 6):
                          bvector.push_back (1) 
                      else:
                          TightTag = self.isTightLepton(iLep)
                          bvector.push_back (TightTag)
                  for remainingLep in range( maxNumLeptons - len(goodLeps) ) :
                     bvector.push_back ( -9999. )

                if bname == 'std_vector_lepton_isWgsLepton' :
                  for iLep in goodLeps :
                     WgsTag = self.isWgsLepton(iLep)
                     bvector.push_back (WgsTag)
                  for remainingLep in range( maxNumLeptons - len(goodLeps) ) :
                     bvector.push_back ( -9999. )


              # now the jets:  
              # - clean jets
              #   for leptons with pt > minLeptonPt (default 10 GeV)
              minLeptonPt = 10.
              
              goodJets = []
              for iJet in xrange(len(itree.std_vector_jet_pt)) :
                isLepton = False;
                for iLep in goodLeps :
                  if itree.std_vector_lepton_pt[iLep] < minLeptonPt:
                    break;
                  if self.jetIsLepton(itree.std_vector_jet_eta[iJet],itree.std_vector_jet_phi[iJet],itree.std_vector_lepton_eta[iLep],itree.std_vector_lepton_phi[iLep]) :
                    isLepton = True;
                if not isLepton:
                  goodJets.append(iJet)
              
              goodPuppiJets = []
              for iJet in xrange(len(itree.std_vector_puppijet_pt)) :
                  isLepton = False;
                  for iLep in goodLeps :
                      if itree.std_vector_lepton_pt[iLep] < minLeptonPt:
                          break;
                      if self.jetIsLepton(itree.std_vector_puppijet_eta[iJet],itree.std_vector_puppijet_phi[iJet],itree.std_vector_lepton_eta[iLep],itree.std_vector_lepton_phi[iLep]) :
                          isLepton = True;
                  if not isLepton:
                      goodPuppiJets.append(iJet)
                          
              for bname, bvector in self.oldBranchesToBeModifiedVector.iteritems():
                   if (("vector_jet" in bname) or (("vector_puppijet") in bname)) and not (("vector_lepton" in bname) or ("vector_electron" in bname) or ("vector_muon" in bname)):
                       if "vector_puppijet" in bname:
                           self.changeOrder( bname, bvector, goodPuppiJets)
                       else:
                           self.changeOrder( bname, bvector, goodJets)
                           
              #for bname, bvector in self.looseLeptonVector.iteritems():
                   #bvector.clear() 
                   ##print " boh = ",len(getattr(self.itree, bname))
                   #self.changeOrder( bname, bvector, xrange(len(getattr(self.itree, bname))) )

              #print "goodJets: ", goodJets
              #print "goodPuppiJets: ", goodPuppiJets

              pt1 = itree.std_vector_lepton_pt[goodLep1]
              pt2 = itree.std_vector_lepton_pt[goodLep2]
              eta1 = itree.std_vector_lepton_eta[goodLep1]
              eta2 = itree.std_vector_lepton_eta[goodLep2]             
              phi1 = itree.std_vector_lepton_phi[goodLep1]
              phi2 = itree.std_vector_lepton_phi[goodLep2]
              pid1 = itree.std_vector_lepton_flavour[goodLep1]
              pid2 = itree.std_vector_lepton_flavour[goodLep2]
              if self.cmssw == '763' or self.cmssw == 'ICHEP2016' or self.cmssw == 'Rereco2016' or self.cmssw == 'Full2016':
                met = itree.metPfType1      
                metphi = itree.metPfType1Phi
              else : 
                met = itree.pfType1Met          # formerly pfType1Met
                metphi = itree.pfType1Metphi    # formerly pfType1Metphi

              if len(goodJets) >=  2:
                jetpt1 = itree.std_vector_jet_pt[goodJets[0]]
                jetpt2 = itree.std_vector_jet_pt[goodJets[1]]
                jeteta1 = itree.std_vector_jet_eta[goodJets[0]]
                jeteta2 = itree.std_vector_jet_eta[goodJets[1]]
                jetphi1 = itree.std_vector_jet_phi[goodJets[0]]
                jetphi2 = itree.std_vector_jet_phi[goodJets[1]]
                jetmass1 = itree.std_vector_jet_mass[goodJets[0]]
                jetmass2 = itree.std_vector_jet_mass[goodJets[1]]
                WW = ROOT.WW(pt1, pt2, eta1, eta2, phi1, phi2, pid1, pid2, met, metphi, jetpt1, jetpt2, jeteta1, jeteta2, jetphi1, jetphi2, jetmass1, jetmass2)
              else:
                WW = ROOT.WW(pt1, pt2, eta1, eta2, phi1, phi2, pid1, pid2, met, metphi )
              
              
              # set the list of leptons into the object "WW"
              new_std_vector_lepton_pt.clear()
              new_std_vector_lepton_eta.clear()
              new_std_vector_lepton_phi.clear()
              new_std_vector_lepton_flavour.clear()

              for iGoodLep in goodLeps :
                new_std_vector_lepton_pt.push_back(itree.std_vector_lepton_pt[ iGoodLep ])
                new_std_vector_lepton_eta.push_back(itree.std_vector_lepton_eta[ iGoodLep ])
                new_std_vector_lepton_phi.push_back(itree.std_vector_lepton_phi[ iGoodLep ])
                new_std_vector_lepton_flavour.push_back(itree.std_vector_lepton_flavour[ iGoodLep ])
              
              WW.setLeptons(new_std_vector_lepton_pt, new_std_vector_lepton_eta, new_std_vector_lepton_phi, new_std_vector_lepton_flavour)

              # set the list of jets into the object "WW"
              new_std_vector_jet_pt.clear()
              new_std_vector_jet_eta.clear()
              for iGoodJet in goodJets :
                new_std_vector_jet_pt.push_back(itree.std_vector_jet_pt[ iGoodJet ])
                new_std_vector_jet_eta.push_back(itree.std_vector_jet_eta[ iGoodJet ])
              WW.setJets(new_std_vector_jet_pt, new_std_vector_jet_eta)
          
              # now fill the variables like "mll", "dphill", ...
              for bname, bvariable in self.oldBranchesToBeModifiedSimpleVariable.iteritems():
                bvariable[0] = getattr(WW, bname)()
                
              # refill the single jet variables
              counter = 0
              varCounter = 0
              for bname, bvariable in self.jetVarDic.iteritems():
                  bvariable[0] = (getattr(self.otree, 'std_vector_jet_'+self.jetVariables[varCounter]))[counter]
                  counter += 1
                  if counter == maxnjets:
                      varCounter += 1
                      counter = 0                    

              # met filters: "bool" (as weight)
              if self.cmssw == '763' or self.cmssw == 'ICHEP2016' or self.cmssw == 'Rereco2016' or self.cmssw == 'Full2016' :
                pass_met_filters = 1.
                #print " min =", min( 8 , len(itree.std_vector_trigger_special) )
                for metfilters in range( min( 8 , len(itree.std_vector_trigger_special) ) ) :
                  if itree.std_vector_trigger_special[metfilters] == 0. : pass_met_filters = 0.  
                  #print " i: ", i, " :: metfilters ", metfilters, " --> ", itree.std_vector_trigger_special[metfilters]
                self.oldBranchesToBeModifiedSpecialSimpleVariable['metFilter'][0] = pass_met_filters
                
              # closest loose di-muon mass to Z
              if self.cmssw == 'Full2016' :
                dmll = 9999.
                for i1 in xrange(len(itree.std_vector_lepton_pt)) :
                    for i2 in xrange(i1+1, len(itree.std_vector_lepton_pt)) :
                        if itree.std_vector_lepton_pt[i2] < 10. :
                            break
                            
                        # check opposite charge and same flavour muons
                        if abs(itree.std_vector_lepton_flavour[i1]) == 13. and itree.std_vector_lepton_flavour[i1] == -1. * itree.std_vector_lepton_flavour[i2] :
                            dmll_temp = abs( math.sqrt(2*itree.std_vector_lepton_pt[i1]*itree.std_vector_lepton_pt[i2]*(math.cosh(itree.std_vector_lepton_eta[i1]-itree.std_vector_lepton_eta[i2]) - math.cos(itree.std_vector_lepton_phi[i1]-itree.std_vector_lepton_phi[i2])) ) - 91.1876 )
                            if dmll_temp < dmll :
                                dmll = dmll_temp
                self.oldBranchesToBeModifiedSpecialSimpleVariable['dmZllRecoMuon'][0] = dmll

              # apply selections to reduce trees size:
              #   - self.selection
              #      1 = pt>18/8 for two leading leptons
              saveEvent = 1
              if self.selection == 1 :
                if new_std_vector_lepton_pt.at(0) > 18 and new_std_vector_lepton_pt.at(1) > 8 :
                  saveEvent = 1
                else :
                  saveEvent = 0
                  
              if saveEvent == 1: 
                otree.Fill()
                savedentries+=1


        self.disconnect()
        print '- Eventloop completed'
        print '   Saved: ', savedentries, ' events'


