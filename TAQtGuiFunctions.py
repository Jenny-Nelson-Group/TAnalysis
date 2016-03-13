###############################################################################
########### ALEXANDRE DE CASTRO MACIEL                              ###########
########### CODE WRITTEN FOR PYTHON 2.7                             ###########
########### NOVEMBER 2015 - IMPERIAL COLLEGE LONDON                 ###########
###############################################################################
import numpy as np
import os
import os.path
import glob
from time import gmtime, strftime
from scipy.optimize import curve_fit
import TAQtGui

def func(x,a,b): # LINEAR FUNCTION TO BE USED IN THE curve_fit CALLINGS
    return a+b*x

def calcVolAndCgeo(eps,A,L): # CALCULATE THE VOLUME AND CAPACITANCE OF A CELL
    eps0 = 8.854187817e-12 # F/m
    return A*L*1e-7, eps*eps0*A*1e-4/(L*1e-9) # Volume in cm3, Capacitance in F

def calcChargeDensity(charge): # CALCULATE DENSITY OF CHARGE
    e = 1.60217662e-19 # C
    d, o, volume, c = getConfTxt()
    n = charge / ( e * volume )
    return n # in cm-3

def readConfFile() :
    def_conf = {}
    with open('conf.txt','r') as f:
        for line in f:
            def_conf[line.split(' , ')[0]] = line.split(' , ')[1]

    return def_conf

def getConfTxt(): # READ THE CONF.TXT TO GET DATA THAT IS USED TOO OFTEN
    def_conf = readConfFile()
    vol, cap = calcVolAndCgeo(float(def_conf['def_eps']), float(def_conf['def_A']), float(def_conf['def_L']))
    return def_conf['def_dir'], def_conf['def_out'], vol, cap

def lookForFiles() :
    directory, output, volume, Cgeo = getConfTxt()

    isThereACalibrationFile = False
    for path in glob.glob(directory+'*'):
        path = windowsFilenamesSuck(path)
        if path.find('jsc_') > 0 :
            isThereACalibrationFile = True

    CEFiles = 0
    CEsuns = []
    for path in glob.glob(directory+'*'):
        path = windowsFilenamesSuck(path)
        if path.find('CE_') > 0 :
            CEFiles += 1
            CEsuns.append(float(path.split("_")[-1][:-9]))
    # COUNT THE NUMBER OF TPC FILES ARE PRESENT IN INPUT DIR
    TPCFiles = 0
    TPCsuns =  []
    for path in glob.glob(directory+'*'):
        path = windowsFilenamesSuck(path)
        if path.find('TPC_') > 0 :
            TPCFiles += 1
            TPCsuns.append(float(path.split("_")[-1][:-9]))
    # COUNT THE NUMBER OF TPV FILES ARE PRESENT IN INPUT DIR
    TPVFiles = 0
    TPVsuns = []
    for path in glob.glob(directory+'*'):
        path = windowsFilenamesSuck(path)
        if path.find('TPV_') > 0 :
            TPVFiles += 1
            TPVsuns.append(float(path.split("_")[-1][:-9]))
    return isThereACalibrationFile, CEFiles, CEsuns, TPCFiles, TPCsuns, TPVFiles, TPVsuns

def windowsFilenamesSuck(path):
    newpath = ''
    for i, letter in enumerate(path):
        if letter == '\\':
            newpath += '/'
        else :
            newpath += letter

    if newpath[-1] != '/' :
        newpath += '/'
    return newpath

def whatIsThis(this): # THIS FUNCTION IS TO RECOVER VECTORS FROM SUMMARY
    directory, output, volume, Cgeo = getConfTxt()
    thisIs = []
    if os.path.isfile(output+'Summary.txt'):
        with open(output+'Summary.txt','r') as f:
            for linenumber, line in enumerate(f):
                if linenumber == 3 :
                    if line.find(this) >= 0 :
                        thisIndex = line.replace('\n','').split(' , ').index(this)
                    else:
                        break
                if linenumber > 3 :
                    thisIs.append(float(line.split(',')[thisIndex]))

    return np.array(thisIs)

def getJscCal(self): # READ THE LIGHT LEVEL CALIBRATION FILE

    directory, output, volume, Cgeo = getConfTxt()
    for path in glob.glob(directory+'*'):
        if path.find("jsc_cal") > 0 :
            with open(path,'r') as f:
                suns,jsc,jsc_rev,voc,voc_rev,rev = [],[],[],[],[],0
                for linenumber,line in enumerate(f.readlines()):
                    if linenumber >= 21 :
                        if len(suns) > 0 and float(line.split()[0]) == suns[-1] :
                            rev=1
                        if rev :
                            jsc_rev.append(np.abs(float(line.split()[4])))
                            voc_rev.append(float(line.split()[5]))
                        else:
                            suns.append(float(line.split()[0]))
                            jsc.append(np.abs(float(line.split()[4])))
                            voc.append(float(line.split()[5]))
                jsc_rev=list(reversed(jsc_rev))
                voc_rev=list(reversed(voc_rev))

    initial_time = strftime("%Y-%m-%d %H:%M:%S",gmtime())
    with open(output+"Summary.txt",'w') as fit:
        fit.write('Data calculated at %s \n' % (initial_time))
        fit.write('Light Intensity , Jsc , Jsc rev , Voc , Voc rev\n')
        fit.write('Suns , mA , mA , V , V\n')
        fit.write('suns_LLC , jsc_LLC , jsc_rev_LLC , voc_LLC , voc_rev_LLC\n')
        fit.writelines('%0.2f , %e , %e , %e , %e\n' % (a,b,c,d,e)
                        for a,b,c,d,e in zip(suns,jsc,jsc_rev,voc,voc_rev))
    return

def workOnCEData(corrCE): # WORK ON CE DATA
    directory, output, volume, Cgeo = getConfTxt()
    for path in glob.glob(directory+'*'):
        i_dark = []
        if( path.find("CE_") > 0 and path.find("0.00") > 0 ):
            with open(path,'r') as f:
                for linenumber,line in enumerate(f.readlines()):
                    if( linenumber >= 4 ):
                        i_dark.append(float(line.split()[1]))

            break

    suns          = whatIsThis('suns_LLC')
    voc           = whatIsThis('voc_LLC')
    voc_rev       = whatIsThis('voc_rev_LLC')
    charge_ce     = np.zeros(len(suns))
    charge_ce_rev = np.zeros(len(suns))

    for path in glob.glob(directory+'*'):
        time_offset = 0.0
        t_ce        = []
        i_light     = []
        if( path.find("CE_") > 0 and path.find("0.00") < 0 ):
            with open(path,'r') as f:
                for linenumber,line in enumerate(f.readlines()):
                    if( linenumber == 1 ):
                        sun_ce=float(line.split()[3][:-1])
                    if( linenumber >= 4 ):
                        t_ce.append(float(line.split()[0])+time_offset)
                        i_light.append(float(line.split()[1]))

                t_ce,i_dark,i_light = np.array(t_ce),np.array(i_dark),np.array(i_light)
                if( len(i_dark) > 0 ):
                    i_corr = i_light-i_dark
                else:
                    i_dark = np.zeros(len(i_light))
                    i_corr = i_light

            i_abs = np.absolute(i_corr)
            if( i_corr[np.argmax(i_abs)] < 0 ):
                i_corr = -1.0*i_corr

            basesum,basecount = 0.0,0
            for i in range(len(t_ce)):
                if( t_ce[i] < 0 ):
                    basecount += 1
                    basesum   += i_corr[i]
                else:
                    break

            i_corr_b = i_corr-basesum/basecount

            charge = []
            charge.append(0.0)
            for j in range(i,len(t_ce)-1):
                base   = t_ce[j+1]-t_ce[j]
                height = i_corr_b[j+1]+i_corr_b[j]
                charge.append(charge[-1]+0.5*base*height/1000.0)

            for j,sun in enumerate(suns):
                if( sun == sun_ce ):
                    corr = 0.0
                    if corrCE : corr = voc[j]*Cgeo
                    charge_ce[j] = charge[-1] - corr
                    corr = 0.0
                    if corrCE : corr = voc_rev[j]*Cgeo
                    charge_ce_rev[j] = charge[-1] - corr

            out_file = output+"Q_CE for "+path.split("/")[-1]
            initial_time = strftime("%Y-%m-%d %H:%M:%S",gmtime())
            with open(out_file,'w') as fit:
                fit.write('Data calculated at %s \n' % (initial_time))
                fit.write('Time , Charge \n')
                fit.write('s , C \n')
                fit.write('Q_CE , %s \n' % path.split("/")[-1].split("_")[-1][:-4])
                fit.writelines('%e , %e \n' % (a,b) for a,b in zip(t_ce[i:],charge))

            out_file = output+"I_CE for "+path.split("/")[-1]
            with open(out_file,'w') as fit:
                fit.write('Data calculated at %s \n' % (initial_time))
                fit.write('Time , Current in Dark  , Current in Light , Current Corrected\n')
                fit.write('s , mA , mA , mA \n')
                fit.write('%s , Dark , Light , Corrected \n' % path.split("/")[-1].split("_")[-1][:-4])
                fit.writelines('%e , %e , %e , %e \n' % (a,b,c,d) for a,b,c,d in zip(t_ce,i_dark,i_light,i_corr_b))

    lines = []
    with open(output+"Summary.txt",'r') as f:
        for line in f:
            lines.append(line)
    with open(output+"Summary.txt",'w') as f:
        for linenumber, line in enumerate(lines):
            if linenumber == 0:
                f.write(line)
            if linenumber == 1:
                f.write(line[:-1]+" , Q , Q_rev, n , n_rev\n")
            if linenumber == 2:
                f.write(line[:-1]+" , C , C , cm-3 , cm-3\n")
            if linenumber == 3:
                f.write(line[:-1]+" , q_CE , q_rev_CE , n_CE , n_rev_CE\n")
            if linenumber > 3:
                f.write(line[:-1]+" , %e , %e , %e , %e\n" % (charge_ce[linenumber-4], charge_ce_rev[linenumber-4],
                        calcChargeDensity(charge_ce)[linenumber-4], calcChargeDensity(charge_ce_rev)[linenumber-4]))

    return

def workOnTPCData():
    directory, output, volume, Cgeo = getConfTxt()
    suns          = whatIsThis('suns_LLC')
    charge_tpc = np.zeros(len(suns))
    for path in glob.glob(directory+'*'):
        time_offset = 0.0
        t     = []
        i     = []
        if path.find("TPC_") > 0 :
            with open(path,'r') as f:
                for linenumber,line in enumerate(f.readlines()):
                    if linenumber == 1 :
                        sun_tpc = float(line.split()[3][:-1])
                    if linenumber >= 4 :
                        t.append(float(line.split()[0])+time_offset)
                        i.append(float(line.split()[1]))

                t,i = np.array(t),np.array(i)

            i_abs = np.absolute(i)
            if i[np.argmax(i_abs)] < 0 :
                i = -1.0*i

            basesum,basecount = 0.0,0
            for m in range(len(t)):
                if t[m] < 0 :
                    basecount += 1
                    basesum   += i[m]
                else:
                    break

            i_corr = i-basesum/basecount

            charge = []
            charge.append(0.0)
            for j in range(m,len(t)-1):
                base   = t[j+1]-t[j]
                height = i_corr[j+1]+i_corr[j]
                charge.append(charge[-1]+0.5*base*height/1000.0)

            for j, sun in enumerate(suns):
                if sun == sun_tpc :
                    charge_tpc[j]=charge[-1]

            global charge_min_sun
            charge_min_sun = -1.0
            if sun_tpc == 0.0 :
                charge_min_sun = charge[-1]
            initial_time = strftime("%Y-%m-%d %H:%M:%S",gmtime())
            out_file = output+"Q_TPC for "+path.split("/")[-1]
            with open(out_file,'w') as fit:
                fit.write('Data calculated at %s \n' % (initial_time))
                fit.write('Time , Charge \n')
                fit.write('s , C \n')
                fit.write('Q_TPC , %s \n' % path.split("/")[-1].split("_")[-1][:-4])
                fit.writelines('%e , %e \n' % (a,b) for a,b in zip(t[m:],charge))

            out_file = output+"I_TPC for "+path.split("/")[-1]
            with open(out_file,'w') as fit:
                fit.write('Data calculated at %s \n' % (initial_time))
                fit.write('Time , Current , Current Corrected\n')
                fit.write('s , mA , mA \n')
                fit.write('%s , Original , Baseline Corrected \n' % path.split("/")[-1].split("_")[-1][:-4])
                fit.writelines('%e , %e , %e \n' % (a,b,c) for a,b,c in zip(t,i,i_corr))

    out_file = output+"Summary.txt"
    lines = []
    with open(out_file,'r') as f:
        for line in f:
            lines.append(line)
    with open(out_file,'w') as f:
        for linenumber, line in enumerate(lines):
            if linenumber == 0:
                f.write(line)
            if linenumber == 1:
                f.write(line[:-1]+" , Q , n\n")
            if linenumber == 2:
                f.write(line[:-1]+" , C , cm-3\n")
            if linenumber == 3:
                f.write(line[:-1]+" , q_TPC , n_TPC\n")
            if linenumber > 3:
                f.write(line[:-1]+" , %e , %e\n" % (charge_tpc[linenumber-4],calcChargeDensity(charge_tpc)[linenumber-4]))

def workOnTPVData():
    directory, output, volume, Cgeo = getConfTxt()
    suns          = whatIsThis('suns_LLC')
    for path in glob.glob(directory+'*'):
        v_dark = []
        if path.find("TPV_") > 0 and path.find("0.00") > 0 :
            with open(path,'r') as f:
                for linenumber,line in enumerate(f.readlines()):
                    if( linenumber >= 4 ):
                        v_dark.append(float(line.split()[1]))

            break

    lifetime,v0 = np.zeros(len(suns)),np.zeros(len(suns))
    for path in glob.glob(directory+'*'):
        time_offset = 0.0
        t_tpv       = []
        v_light     = []
        if path.find("TPV_") > 0 and path.find("0.00") < 0 :
            with open(path,'r') as f:
                for linenumber,line in enumerate(f.readlines()):
                    if linenumber == 1 :
                        sun_tpv = float(line.split()[3][:-1])
                    if linenumber >= 4 :
                        t_tpv.append(float(line.split()[0])+time_offset)
                        v_light.append(float(line.split()[1]))

                t_tpv,v_dark,v_light = np.array(t_tpv),np.array(v_dark),np.array(v_light)
                if len(v_dark) > 0 :
                    v_corr = v_light-v_dark
                else:
                    v_dark = np.zeros(len(v_light))
                    v_corr = v_light

            v_abs = np.absolute(v_corr)
            if v_corr[np.argmax(v_abs)] < 0 :
                v_corr = -1.0*v_corr

            basesum,basecount = 0.0,0
            for m in range(len(t_tpv)):
                if t_tpv[m] < 0 :
                    basecount += 1
                    basesum   += v_corr[m]
                else:
                    break

            v_corr_b = v_corr-basesum/basecount

            for j in range(np.argmax(v_corr_b),len(v_corr_b)):
                if v_corr_b[j] < 1e-1 :
                    break

            t         = t_tpv[np.argmax(v_corr_b):j]
            logv      = np.log(v_corr_b[np.argmax(v_corr_b):j])
            popt,pcov = curve_fit(func,t,logv)
            fitv      = func(t,popt[0],popt[1])

            for j,sun in enumerate(suns):
                if( sun == sun_tpv ):
                    lifetime[j] = -1.0/popt[1]
                    v0[j]       = max(v_corr_b)

            initial_time = strftime("%Y-%m-%d %H:%M:%S",gmtime())
            out_file = output+"V_TPV for "+path.split("/")[-1]
            with open(out_file,'w') as fit:
                fit.write('Data calculated at %s\n' % (initial_time))
                fit.write('Time , Voltage , Voltage\n')
                fit.write('s , V , V\n')
                fit.write('%s , Original , Baseline Corrected\n' % path.split("/")[-1].split("_")[-1][:-4])
                fit.writelines('%e , %e , %e\n' % (a,b,c) for a,b,c in zip(t_tpv, v_corr, v_corr_b))

            out_file = output+"Fit_TPV for "+path.split("/")[-1]
            with open(out_file,'w') as fit:
                fit.write('Data calculated at %s\n' % (initial_time))
                fit.write('Time , Voltage , Voltage\n')
                fit.write('s , V , V\n')
                fit.write('%s , Exp , Fit\n' % path.split("/")[-1].split("_")[-1][:-4])
                fit.writelines('%e , %e , %e\n' % (a,b,c) for a,b,c in zip(t, logv, fitv))

    out_file = output+"Summary.txt"
    lines = []
    with open(out_file,'r') as f:
        for line in f:
            lines.append(line)
    with open(out_file,'w') as f:
        for linenumber, line in enumerate(lines):
            if linenumber == 0:
                f.write(line)
            if linenumber == 1:
                f.write(line[:-1]+" , Lifetime , DeltaV0\n")
            if linenumber == 2:
                f.write(line[:-1]+" , s , mV\n")
            if linenumber == 3:
                f.write(line[:-1]+" , tau , v0\n")
            if linenumber > 3:
                f.write(line[:-1]+" , %e , %e\n" % (lifetime[linenumber-4],v0[linenumber-4]))

def workOnDC(limits, whatCalc):
    directory, output, volume, Cgeo = getConfTxt()
    suns          = whatIsThis('suns_LLC')
    voc           = whatIsThis('voc_LLC')
    voc_rev       = whatIsThis('voc_rev_LLC')
    if whatCalc[1] : charge_ce     = whatIsThis('q_CE')
    if whatCalc[1] : charge_ce_rev = whatIsThis('q_rev_CE')
    if whatCalc[3] : charge_tpc    = whatIsThis('q_TPC')
    if whatCalc[5] : v0            = whatIsThis('v0')
    if whatCalc[5] : lifetime      = whatIsThis('tau')

    C = np.zeros(len(suns))
    charge_diffC = np.zeros(len(suns))
    charge_diffC_rev = np.zeros(len(suns))

    if whatCalc[1] and whatCalc[2] :
        if charge_min_sun > 0.0 :
            dq = charge_min_sun
        else:
            dq = charge_tpc[np.argmin(suns)]

        for i,dv in enumerate(v0):
            C[i] = 1000*dq/dv

    w0_i , w0_f  = limits[0][0], limits[0][1]
    w1_i , w1_f  = limits[1][0], limits[1][1]
    w2_i , w2_f  = limits[2][0], limits[2][1]
    w3_i , w3_f  = limits[3][0], limits[3][1]
    w4_i , w4_f  = limits[4][0], limits[4][1]
    w5_i , w5_f  = limits[5][0], limits[5][1]

    lambDC = 0
    lambDC_rev = 0
    lambCE = 0
    lambCE_rev = 0

    if whatCalc[1] and whatCalc[2] :
        lnC          = np.log(C[w0_i:w0_f])
        voc_fit      = np.array(voc[w0_i:w0_f])
        a            = np.log(C[np.argmin(suns)])
        b            = (lnC[-1]-lnC[0])/(voc_fit[-1]-voc_fit[0])
        popt,pcov    = curve_fit(func,voc_fit,lnC,p0=(a,b))
        lnC_fit      = func(voc_fit,popt[0],popt[1])
        charge_diffC = func(C,-np.exp(popt[0])/popt[1],1.0/popt[1])

        initial_time = strftime("%Y-%m-%d %H:%M:%S",gmtime())
        out_file = output+'Fit for DiffC.txt'
        with open(out_file,'w') as fit:
            fit.write('Data calculated at %s\n' % (initial_time))
            fit.write('Voc , lnC\n')
            fit.write('V , \n')
            fit.writelines('%e , %e\n' % (a,b) for a,b in zip(voc_fit, lnC_fit))

        lnC_rev      = np.log(C[w1_i:w1_f])
        voc_fit_rev  = np.array(voc_rev[w1_i:w1_f])
        a            = np.log(C[np.argmin(suns)])
        b            = (lnC_rev[-1]-lnC_rev[0])/(voc_fit_rev[-1]-voc_fit_rev[0])
        popt,pcov    = curve_fit(func,voc_fit_rev,lnC_rev,p0=(a,b))
        lnC_fit_rev  = func(voc_fit_rev,popt[0],popt[1])

        charge_diffC_rev = func(C,-np.exp(popt[0])/popt[1],1.0/popt[1])
        out_file = output+'Fit for DiffC rev.txt'
        with open(out_file,'w') as fit:
            fit.write('Data calculated at %s\n' % (initial_time))
            fit.write('Voc , lnC\n')
            fit.write('V , \n')
            fit.writelines('%e , %e\n' % (a,b) for a,b in zip(voc_fit_rev, lnC_fit_rev))

        popt,pcov   = curve_fit(func,np.log(calcChargeDensity(charge_diffC)[w2_i:w2_f]),np.log(lifetime[w2_i:w2_f]))
        logLT_fitdc = func(np.log(calcChargeDensity(charge_diffC)[w2_i:w2_f]),popt[0],popt[1])
        lambDC      = -popt[1]

        out_file = output+'Fit for logLT_fitdc.txt'
        with open(out_file,'w') as fit:
            fit.write('Data calculated at %s\n' % (initial_time))
            fit.write('Ln(n) , Ln(Lifetime)\n')
            fit.write(' , \n')
            fit.writelines('%e , %e\n' % (a,b) for a,b in zip(np.log(calcChargeDensity(charge_diffC)[w2_i:w2_f]), logLT_fitdc))

        popt,pcov   = curve_fit(func,np.log(calcChargeDensity(charge_diffC_rev)[w3_i:w3_f]),np.log(lifetime[w3_i:w3_f]))
        logLT_fitdc_rev = func(np.log(calcChargeDensity(charge_diffC_rev)[w3_i:w3_f]),popt[0],popt[1])
        lambDC_rev  = -popt[1]

        out_file = output+'Fit for logLT_fitdc_rev.txt'
        with open(out_file,'w') as fit:
            fit.write('Data calculated at %s\n' % (initial_time))
            fit.write('Ln(n) , Ln(Lifetime)\n')
            fit.write(' , \n')
            fit.writelines('%e , %e\n' % (a,b) for a,b in zip(np.log(calcChargeDensity(charge_diffC_rev)[w3_i:w3_f]), logLT_fitdc_rev))

    if whatCalc[0] and whatCalc[2] :
        popt,pcov   = curve_fit(func,np.log(calcChargeDensity(charge_ce)[w4_i:w4_f]),np.log(lifetime[w4_i:w4_f]))
        logLT_fitce = func(np.log(calcChargeDensity(charge_ce)[w4_i:w4_f]),popt[0],popt[1])
        lambCE      = -popt[1]

        out_file = output+'Fit for logLT_fitce.txt'
        with open(out_file,'w') as fit:
            fit.write('Data calculated at %s\n' % (initial_time))
            fit.write('Ln(n) , Ln(Lifetime)\n')
            fit.write(' , \n')
            fit.writelines('%e , %e\n' % (a,b) for a,b in zip(np.log(calcChargeDensity(charge_ce)[w4_i:w4_f]), logLT_fitce))

        popt,pcov   = curve_fit(func,np.log(calcChargeDensity(charge_ce_rev)[w5_i:w5_f]),np.log(lifetime[w5_i:w5_f]))
        logLT_fitce_rev = func(np.log(calcChargeDensity(charge_ce_rev)[w5_i:w5_f]),popt[0],popt[1])
        lambCE_rev  = -popt[1]

        out_file = output+'Fit for logLT_fitce_rev.txt'
        with open(out_file,'w') as fit:
            fit.write('Data calculated at %s\n' % (initial_time))
            fit.write('Ln(n) , Ln(Lifetime)\n')
            fit.write(' , \n')
            fit.writelines('%e , %e\n' % (a,b) for a,b in zip(np.log(calcChargeDensity(charge_ce_rev)[w5_i:w5_f]), logLT_fitce_rev))

    out_file = output+'Lambdas.txt'
    with open(out_file,'w') as fit:
        fit.write('lambDC , %e\n' % lambDC)
        fit.write('lambDC_rev , %e\n' % lambDC_rev)
        fit.write('lambCE , %e\n' % lambCE)
        fit.write('lambCE_rev , %e\n' % lambCE_rev)

    out_file = output+"Summary.txt"
    lines = []
    correct = 0
    with open(out_file,'r') as f:
        for linenumber, line in enumerate(f):
            if linenumber == 3 and line.find('DiffC') > 0 :correct = 1
            lines.append(line)

    with open(out_file,'w') as f:
        for linenumber, line in enumerate(lines):
            if correct and linenumber: line = str(','.join(line.split(',')[:-3])[:-1]+'\n')

            if linenumber == 0:
                f.write(line)
            if linenumber == 1:
                f.write(line[:-1]+" , Capacitance , Q , Q , n , n\n")
            if linenumber == 2:
                f.write(line[:-1]+" , F , C , C , cm-3 , cm-3\n")
            if linenumber == 3:
                f.write(line[:-1]+" , DiffC , Q_DiffC , Q_DiffC_rev , n_DiffC , n_DiffC_rev\n")
            if linenumber > 3:
                a = C[linenumber-4]
                b = charge_diffC[linenumber-4]
                c = charge_diffC_rev[linenumber-4]
                d = calcChargeDensity(charge_diffC)[linenumber-4]
                e = calcChargeDensity(charge_diffC_rev)[linenumber-4]
                f.write(line[:-1]+" , %e , %e , %e , %e , %e\n" % (a, b, c, d, e))

def doTheMagicWithOutputFiles(delete):
    directory, output, volume, Cgeo = getConfTxt()
    I_CE = []
    Q_CE = []
    I_TPC = []
    Q_TPC = []
    V_TPV = []
    Fit_TPV = []
    Fit_TPV_temp = []
    isThereAnyI_CE = False
    isThereAnyQ_CE = False
    isThereAnyI_TPC = False
    isThereAnyQ_TPC = False
    isThereAnyV_TPV = False
    isThereAnyFit_TPV = False
    for path in glob.glob(output+'*'):
        if path.find('I_CE') > 0 :
            with open(path,'r') as f:
                for lnb,line in enumerate(f.readlines()):
                    if isThereAnyI_CE == False and lnb < 3 :
                        I_CE.append(line)
                    if isThereAnyI_CE == False and lnb == 3 :
                        I_CE.append(' , Dark , '+line.split(' , ')[0]+' , '+line.split(' , ')[0]+' Corrected\n')
                    if isThereAnyI_CE == False and lnb > 3 :
                        I_CE.append(line)

                    if isThereAnyI_CE and lnb == 3 :
                        I_CE[lnb] = I_CE[lnb][:-1]+' , '+line.split(' , ')[0]+' , '+line.split(' , ')[0]+' Corrected\n'
                    if isThereAnyI_CE and lnb > 3 :
                        I_CE[lnb] = I_CE[lnb][:-1]+' , '+line.split(' , ')[2]+' , '+line.split(' , ')[3][:-1]+'\n'
                isThereAnyI_CE = True
            if delete == 'yes' : os.remove(path)
        if path.find('Q_CE') > 0 :
            with open(path,'r') as f:
                for lnb,line in enumerate(f.readlines()):
                    if isThereAnyQ_CE == False:
                        Q_CE.append(line)

                    if isThereAnyQ_CE and lnb >= 3 :
                        Q_CE[lnb] = Q_CE[lnb][:-1]+' , '+line.split(' , ')[1][:-1]+'\n'
                isThereAnyQ_CE = True
            if delete == 'yes' : os.remove(path)
        if path.find('I_TPC') > 0 :
            with open(path,'r') as f:
                for lnb,line in enumerate(f.readlines()):
                    if isThereAnyI_TPC == False and lnb < 3 :
                        I_TPC.append(line)
                    if isThereAnyI_TPC == False and lnb == 3 :
                        I_TPC.append(line.split(' , ')[0]+' Original , '+line.split(' , ')[0]+' Baseline Corrected\n')
                    if isThereAnyI_TPC == False and lnb > 3 :
                        I_TPC.append(line)

                    if isThereAnyI_TPC and lnb == 3 :
                        I_TPC[lnb] = I_TPC[lnb][:-1]+' , '+line.split(' , ')[0]+' Original , '+line.split(' , ')[0]+' Corrected\n'
                    if isThereAnyI_TPC and lnb > 3 :
                        I_TPC[lnb] = I_TPC[lnb][:-1]+' , '+line.split(' , ')[1]+' , '+line.split(' , ')[2][:-1]+'\n'
                isThereAnyI_TPC = True
            if delete == 'yes' : os.remove(path)
        if path.find('Q_TPC') > 0 :
            with open(path,'r') as f:
                for lnb,line in enumerate(f.readlines()):
                    if isThereAnyQ_TPC == False:
                        Q_TPC.append(line)

                    if isThereAnyQ_TPC and lnb >= 3 :
                        Q_TPC[lnb] = Q_TPC[lnb][:-1]+' , '+line.split(' , ')[1][:-1]+'\n'
                isThereAnyQ_TPC = True
            if delete == 'yes' : os.remove(path)
        if path.find('V_TPV') > 0 :
            with open(path,'r') as f:
                for lnb,line in enumerate(f.readlines()):
                    if isThereAnyV_TPV == False and lnb < 3 :
                        V_TPV.append(line)
                    if isThereAnyV_TPV == False and lnb == 3 :
                        V_TPV.append(line.split(' , ')[0]+' Original , '+line.split(' , ')[0]+' Baseline Corrected\n')
                    if isThereAnyV_TPV == False and lnb > 3 :
                        V_TPV.append(line)

                    if isThereAnyV_TPV and lnb == 3 :
                        V_TPV[lnb] = V_TPV[lnb][:-1]+' , '+line.split(' , ')[0]+' Original , '+line.split(' , ')[0]+' Corrected\n'
                    if isThereAnyI_TPC and lnb > 3 :
                        V_TPV[lnb] = V_TPV[lnb][:-1]+' , '+line.split(' , ')[1]+' , '+line.split(' , ')[2][:-1]+'\n'
                isThereAnyV_TPV = True
            if delete == 'yes' : os.remove(path)
        if path.find('Fit_TPV') > 0 :
            file_ = []
            with open(path,'r') as f:
                for lnb,line in enumerate(f.readlines()):
                    if lnb >= 3 : file_.append(line)
                Fit_TPV_temp.append(file_)
                isThereAnyFit_TPV = True
            if delete == 'yes' : os.remove(path)
    if isThereAnyFit_TPV :
        sizes = []
        for eachFile_ in Fit_TPV_temp : sizes.append(len(eachFile_))
        for i in range(len(Fit_TPV_temp[np.argmax(sizes)])) :
            for c, j in enumerate(Fit_TPV_temp):
                if i == 0 :
                    if c == 0 :
                        Fit_TPV.append(j[i].split(' , ')[0]+' , '+j[i].split(' , ')[0]+' Exp , '+j[i].split(' , ')[0]+' Fit\n')
                    else :
                        Fit_TPV[i] = Fit_TPV[i][:-1]+' , '+j[i].split(' , ')[0]+' , '+j[i].split(' , ')[0]+' Exp , '+j[i].split(' , ')[0]+' Fit\n'
                if i < len(j) and i > 0:
                    if c == 0 :
                        Fit_TPV.append(j[i])
                    else :
                        Fit_TPV[i] = Fit_TPV[i][:-1]+' , '+j[i]
                if i >= len(j) and i > 0:
                    if c == 0 :
                        Fit_TPV.append(' , ,\n')
                    else :
                        Fit_TPV[i] = Fit_TPV[i][:-1]+' , '+' , ,\n'

    with open(output+'Summary_ICE.txt', 'w') as f:
        f.writelines(I_CE)
    with open(output+'Summary_QCE.txt', 'w') as f:
        f.writelines(Q_CE)
    with open(output+'Summary_ITPC.txt', 'w') as f:
        f.writelines(I_TPC)
    with open(output+'Summary_QTPC.txt', 'w') as f:
        f.writelines(Q_TPC)
    with open(output+'Summary_VTPV.txt', 'w') as f:
        f.writelines(V_TPV)
    with open(output+'Summary_FitTPV.txt', 'w') as f:
        f.writelines(Fit_TPV)