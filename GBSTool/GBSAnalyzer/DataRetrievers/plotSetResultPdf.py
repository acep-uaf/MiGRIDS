
#imports
import os
import pickle
import matplotlib.pyplot as plt

def plotSetResultPdf(projectSetDir, runs, legTxt,timeStep):

    os.chdir(projectSetDir)

    # load generator overloading
    infile = open('genOverLoadingPdf.pkl','rb')
    gol = pickle.load(infile)
    infile.close()
    plt.figure(figsize=(10, 8))
    for run in runs:
        plt.plot(gol[run][1][:-1], gol[run][0]*timeStep/3600)

    plt.legend(legTxt)
    plt.ylabel('Time generators spent overloaded [hr]')
    plt.xlabel('Overload value [kW]')

    os.chdir('figs')
    runsTxt = str(runs[0])
    for run in runs[1:]:
        runsTxt = runsTxt + '_' + str(run)
    plt.savefig('genOverloadingRuns' + runsTxt + '.png')

    os.chdir(projectSetDir)
    # load eess overloading
    infile = open('eessOverLoadingPdf.pkl','rb')
    eol = pickle.load(infile)
    infile.close()
    plt.figure(figsize=(10, 8))
    for run in runs:
        plt.plot(eol[run][1][:-1], eol[run][0]*timeStep/3600)

    plt.legend(legTxt)
    plt.ylabel('Time GBS spent overloaded [hr]')
    plt.xlabel('Overload value [kW]')

    os.chdir('figs')
    runsTxt = str(runs[0])
    for run in runs[1:]:
        runsTxt = runsTxt + '_' + str(run)
    plt.savefig('eessOverloadingRuns' + runsTxt + '.png')


