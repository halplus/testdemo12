from sklearn.externals import joblib
import numpy as np

def getBelowData_forbuildingX(originX, windows):
    singleList = []
    for i in range(0, originX.shape[0] - windows):
        singleList.append(originX[i:i + windows])
    return np.asarray(singleList)


def backToReslutWithOne(inputArray):
    new_oneitem_reslut = []
    for single in inputArray:
        new_oneitem_reslut.append(0)
    listVer = inputArray.tolist()
    one_Index = listVer.index(max(listVer))
    new_oneitem_reslut[one_Index] = 1
    return one_Index


def manyStr2intNumpy(inputArray):
    ans = []
    for single in inputArray:
        splited = single.split(',')
        results = list(map(int, splited))
        for singleInt in results:
            ans.append(singleInt)
    return np.asarray(ans)


def numpyOfSta2ListOfX(inputnumpy):
    listReturn = []
    inputnumpy.reshape(inputnumpy.shape[0] * inputnumpy.shape[1], 1)
    ans = []
    for single in inputnumpy:
        ans.append(manyStr2intNumpy(single))
    return ans


ApplicationList = ['Web', 'Youtube', 'Email', 'FacebookAudio', 'Chat']
windowsOfSize = 15
RF = joblib.load('RF.model')

while 1==1:
    sleep(5)
    with open('portdataMusic.txt', 'r') as f:
        lines = f.read().splitlines()
        last_line = lines[-40:-1]
        numpyS = np.array(last_line)
        buildingXwithWidows = getBelowData_forbuildingX(numpyS, windowsOfSize)
        listOfX = numpyOfSta2ListOfX(buildingXwithWidows)
        predictList = RF.predict(listOfX)
        foundApp = []
        for single in predictList:
            print(single)
            apptype = backToReslutWithOne(single)
            if apptype not in foundApp:
                print('found application:', ApplicationList[apptype])
                foundApp.append(apptype)

