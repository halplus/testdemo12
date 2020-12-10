import joblib
import numpy as np
import time



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
RFPort = joblib.load('RFPort.model')
RFFlow = joblib.load('RFFlow.model')

while 1==1:
    time.sleep(5)
    print('clf start')
    with open('portdataMusic.txt', 'r') as f:
        lines = f.read().splitlines()
        last_line = lines[-40:-1]
        numpyS = np.array(last_line)
        buildingXwithWidows = getBelowData_forbuildingX(numpyS, windowsOfSize)
        listOfX = numpyOfSta2ListOfX(buildingXwithWidows)
        # print((listOfX[0]))
        if len(listOfX[0]) == 5 * windowsOfSize:
            for singleArray in listOfX:
                for i in range(len(listOfX[0]) - 1, 0, -1):
                    if i % 5 != 1:
                        if singleArray[i] - singleArray[i - 5] >= 0:
                            singleArray[i] = singleArray[i] - singleArray[i - 5]
        # print((listOfX[0]))

        # print((listOfX[0]))
        if len(listOfX[0]) == 6 * windowsOfSize:
            for singleArray in listOfX:
                for i in range(len(listOfX[0]) - 1, 0, -1):
                    if i % 6 != 0:
                        if singleArray[i] - singleArray[i - 6] >= 0:
                            singleArray[i] = singleArray[i] - singleArray[i - 6]
        # print((listOfX[0]))

        predictList = RFPort.predict(listOfX)
        foundApp = []
        for single in predictList:
            apptype = backToReslutWithOne(single)
            if apptype not in foundApp:
                print('found application:', ApplicationList[apptype])
                foundApp.append(apptype)
    print('clf end')

    time.sleep(5)

    with open('flowdataMusic.txt', 'r') as f:
        lines = f.read().splitlines()
        last_line = lines[-45:-5]
        numpyS = np.array(last_line)
        buildingXwithWidows = getBelowData_forbuildingX(numpyS, windowsOfSize)
        listOfX = numpyOfSta2ListOfX(buildingXwithWidows)
        # print((listOfX[0]))
        if len(listOfX[0]) == 5 * windowsOfSize:
            for singleArray in listOfX:
                for i in range(len(listOfX[0]) - 1, 2, -1):
                    if i % 5 != 1:
                        if singleArray[i] - singleArray[i - 5] >= 0:
                            singleArray[i] = singleArray[i] - singleArray[i - 5]
        # print((listOfX[0]))

        # print((listOfX[0]))
        if len(listOfX[0]) == 6 * windowsOfSize:
            for singleArray in listOfX:
                for i in range(len(listOfX[0]) - 1, 2, -1):
                    if i % 6 != 0:
                        if singleArray[i] - singleArray[i - 6] >= 0:
                            singleArray[i] = singleArray[i] - singleArray[i - 6]
        # print((listOfX[0]))

        predictList = RFFlow.predict(listOfX)
        foundApp = []
        for single in predictList:
            apptype = backToReslutWithOne(single)
            if apptype not in foundApp:
                print('found application:', ApplicationList[apptype])
                foundApp.append(apptype)
    print('clf end')
