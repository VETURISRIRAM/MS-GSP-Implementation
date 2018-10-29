# MS-GSP Algorithm

import os
import re
from copy import deepcopy


def location():
    dataLocation = os.path.join("data", "input", "data.txt")
    parametersLocation = os.path.join("data", "input", "parameters.txt")
    return dataLocation, parametersLocation


def readFile(location):
    with open(location, 'r') as f:
        contents = f.read()
    return contents.split("\n")


def deleteNthItem(sequence, index):
    s_new = deepcopy(sequence)
    count = 0
    for sub_item_set in s_new:
        if len(sub_item_set) > (index - count):
            sub_item_set.remove(sub_item_set[index - count])
            break
        else:
            count += len(sub_item_set)

    s_new = list(filter(lambda x: not x == [], s_new))
    return s_new


def generateAllSubsets(sequence):
    #Just to get the count of items in sequence
    flattened = list(sum(sequence, []))
    subsets = []
    for index in range(len(flattened)):
        subsets.append(deleteNthItem(sequence, index))
    return subsets

def standardizeParametersContents(parametersContents):
    supDict = dict()
    for parameter in parametersContents:
        input = "SDC"
        if parameter.strip() != '':
            if "SDC" not in parameter:
                input = re.findall('MIS\((.*?)\)', parameter)[0]
            value = float(parameter.strip().split('=')[1])
            supDict[input] = value
    return supDict


def standardizeForL(sequence):
    # Dictionary to denote transactions and their items
    seqNums = {}
    # seqList stores the formatted items without spaces, etc
    seqList = []
    # Counter is used to denote the transaction count
    counter = 1

    for x in sequence:
        nums = []
        for i in range(0, len(x)):
            if x[i] == '{':
                nums.append(x[i + 1:i + 3])
                seqList.append(int(x[i + 1:i + 3]))
            elif x[i] == ',':
                nums.append(x[i + 2:i + 4])
                seqList.append(int(x[i + 2:i + 4]))

        seqNums[counter] = nums
        counter += 1

    return seqNums, seqList


def generateL(sequence, misContents):
    # Assumption that if MIS is not given for an item,
    # Its MIS is just count of 1
    # Thus, appended all items except the MIS items
    misKeys = []
    l = []

    # Keeping track of the MIS items
    for x in misContents:
        misKeys.append(x)  # misKeys = [80, 90]

    for x in sequence:
        # Append all other items except MIS items
        if x not in misKeys:
            if x not in l:
                l.append(x)
        else:

            # Calculate if they satisfy their MIS and then append
            percentage = misContents[x]
            itemPercentage = sequence.count(x) / len(misContents)
            if itemPercentage >= percentage:
                l.append(x)

    # Return the final L
    return l


def generate_multi_sequence_list(multi_sequences):
    # re.findall('{(.*?)}' returns list the stuff between all '{' and '}'.
    return [[[item.strip() for item in sequence.split(',')] for sequence in re.findall('{(.*?)}', sequenceLine)] for
            sequenceLine in multi_sequences]


def createL(M, min_support_dict, multi_sequence_list):
    L = []
    min_support = -1
    for item in M:
        formatted_item = [[item]]
        item_support = compute_support(formatted_item, multi_sequence_list)
        if min_support == -1:
            if item_support >= min_support_dict.get(item):
                L.append(item)
                min_support = min_support_dict.get(item)
        else:
            if item_support >= min_support:
                L.append(item)

    return L


# Returns the index(or -1) of an item group in the format [['70', '80']] equivalent <{70, 80}> in the sequenceList
def is_item_group_contained(item_group, sub_sequence_list):
    for index, sequence in enumerate(sub_sequence_list):
        if set(item_group).issubset(set(sequence)):
            return index
    return -1


# Returns a boolean based on whether an item in the format [['20'],['50'],['70', '80']] is contained in the sequenceList
# of the format [['20', '30'], ['50'],['50', '70', '80']]
def is_item_contained(item, sequence_list):
    index = 0
    for itemGroup in item:
        sub_index = is_item_group_contained(itemGroup, sequence_list[index:])
        index = index + sub_index + 1
        if sub_index == -1:
            return False
    return True


# Compute the support of an item with respect to a multiSequenceList. An item is in the format item = [['20', '30'],
# ['50'],['50', '70', '80']] or [['20']] for single item Multi sequenceList is the entire transaction data
# in the form [[['20', '30'],['50'],['50', '70', '80'], [['20', '30'],['50'],['50', '70', '80'] ...]
def compute_support(item, multi_sequence_list):
    max_count = len(multi_sequence_list)
    if not max_count:
        return 0
    return sum(is_item_contained(item, sequenceList) for sequenceList in multi_sequence_list) / max_count


def level2_candidate_gen(L, multiSequenceList, minimumSupportDict):
    C2 = []
    for index, item1 in enumerate(L):
        for item2 in L[index:]:
            C2.append([[item1], [item2]])
            if item1 != item2:
                C2.append([[item2], [item1]])
                C2.append([[item1, item2]])
    return C2


def removeSecondItem(S1):
    S1_new = deepcopy(S1)
    if len(S1_new[0]) == 1:
        del (S1_new[1][0])
    else:
        del (S1_new[0][1])
    S1_new = list(filter(lambda x: not x == [], S1_new))
    return S1_new

def removeSecondLastItem(S1):
    S1_new = deepcopy(S1)
    if len(S1_new[-1]) == 1:
        del (S1_new[-2][-1])
    else:
        del (S1_new[-1][-2])
    S1_new = list(filter(lambda x: not x == [], S1_new))
    return S1_new

def deleteLastItem(S2):
    S2New = deepcopy(S2)
    del (S2New[-1][-1])
    S2New = list(filter(lambda x: not x == [], S2New))
    return S2New

def deleteFirstItem(S2):
    S2New = deepcopy(S2)
    del (S2New[0][0])
    S2New = list(filter(lambda x: not x == [], S2New))
    return S2New


def checkForSubsets(sequence, previousF):
    sequenceList = generateAllSubsets(sequence)
    for Y in previousF:
        if not all(list(map(lambda x: is_item_contained(x, Y), sequenceList))):
            return False
    return True


def MS_candidate_gen(FK, minimumSupportDict):
    cNext = []
    candidateOneSequence = []
    candidateTwoSequence = []
    # print("MS Candidate Gen")
    joinList = []
    check1List = []
    for index, S1 in enumerate(FK):
        for S2 in FK[index:]:
            itemS1 = sum(S1, [])
            #min_mis_item = min(itemS1, key=lambda x: minimumSupportDict.get(x))

            # todo we are at dmtm book page 48 step 2 line 2.
            # print("S1 and S2 are:")
            # print("S1 : ",S1)
            # print("S2 : ",S2)
            # print("Min support dict : ", minimumSupportDict)

            # Check if MIS value of first item is lesser than all other items
            # check1 indicates True if above condition satisfies
            S1firstItemMisSup = minimumSupportDict[S1[0][0]]
            # print("S1 First item support is ",S1firstItemMisSup)
            flattenS1 = list(sum(S1, []))
            #check1 = all(list(map(lambda x: S1firstItemMisSup < minimumSupportDict[x], flattenS1[1:])))

            check1 = all(list(map(lambda x: S1firstItemMisSup < minimumSupportDict[x], flattenS1[1:])))

            # Check if MIS value of last item of S2 is lesser than all other items
            # check3 indicates True if above condition satisfies
            flattenS2 = list(sum(S2, []))
            S2LastItemSup = minimumSupportDict[S2[-1][-1]]
            check3 = all(list(map(lambda x: S2LastItemSup < minimumSupportDict[x], flattenS2[:-1])))

            # Page 48 Step 2 Line 1
            if check1:
                # print("Case 1")

                S1New = removeSecondItem(S1)
                S2New = deleteLastItem(S2)

                subsequenceCheck = S1New == S2New
                # if subsequenceCheck:
                #     print("Yay")
                # else:
                #     print("Nay")

                # Checking if MIS of last element of S2 is the greater than MIS of first itme of S1
                S2lastItemSup = minimumSupportDict[S2New[-1][-1]]
                if S2lastItemSup > S1firstItemMisSup:
                    check2 = True
                else:
                    check2 = False

                # Page 48 Step 2 Line 3
                if subsequenceCheck and check2:

                    # TODO Please fill in the "JOIN" step
                    toBeJoined = S1[-1]
                    toBeJoined.append(S2New[-1])
                    joinList.append(toBeJoined)

                    # Compute length of S1
                    length = len(S1)
                    # Compute size of S1
                    size = len(list(sum(S1, [])))


                    # Check if the last element if separate
                    # Page 48 Step 2 Line 7 (if condition)
                    if len(S2[-1]) == 1:
                        # {l} is S2[-1]
                        c1 = S1 + S2[-1]
                        # {l} is appended to candidate sequence 1
                        candidateOneSequence.append(c1)

                        # Compute length of S1
                        length = len(S1)
                        # Compute size of S1
                        size = len(list(sum(S1, [])))

                        # Page 48 Step 2 Line 10
                        if (length == 2 and size == 2) and float(list(sum(S2, []))[-1]) > float(list(sum(S1, []))[-1]):
                            c2 = S1
                            c2[-1].append(float(S2[-1][0]))
                            candidateTwoSequence.append(c2)

                    elif (((length == 2) and (size == 1)) and (float(list(sum(S2, []))[-1]) > float(list(sum(S1))[-1]))) or (length > 2):
                        c2 = S1
                        c2[-1].append(float(list(sum(S2, []))[-1]))
                        candidateTwoSequence.append(c2)

                # print("Candidate 1 sequence are ", candidateOneSequence)
                # print("Candidate 2 sequence are ", candidateTwoSequence)

            elif check3:
                # print("Case 2")

                S2New = removeSecondLastItem(S2)
                S1New = deleteFirstItem(S1)

                subsequenceCheck = S1New == S2New
                # if subsequenceCheck:
                #     print("Yay")
                # else:
                #     print("Nay")

                # Checking if MIS of last element of S2 is the greater than MIS of first itme of S1
                S2lastItemSup = minimumSupportDict[S2New[-1][-1]]
                if S2lastItemSup > S1firstItemMisSup:
                    check2 = True
                else:
                    check2 = False

                # Page 48 Step 2 Line 3
                if subsequenceCheck and check2:

                    # TODO Please fill in the "JOIN" step
                    toBeJoined = S1[-1]
                    toBeJoined.append(S2New[-1])
                    joinList.append(toBeJoined)

                    # Compute length of S1
                    length = len(S1)
                    # Compute size of S1
                    size = len(list(sum(S1, [])))

                    # Check if the last element if separate
                    # Page 48 Step 2 Line 7 (if condition)
                    if len(S2[-1]) == 1:
                        # {l} is S2[-1]
                        c1 = S1 + S2[-1]
                        # {l} is appended to candidate sequence 1
                        candidateOneSequence.append(c1)

                        # Compute length of S1
                        length = len(S1)
                        # Compute size of S1
                        size = len(list(sum(S1, [])))

                        # Page 48 Step 2 Line 10
                        if (length == 2 and size == 2) and float(list(sum(S2, []))[-1]) > float(
                                list(sum(S1, []))[-1]):
                            c2 = S1
                            c2[-1].append(float(S2[-1][0]))
                            candidateTwoSequence.append(c2)

                    elif (((length == 2) and (size == 1)) and (
                            float(list(sum(S2, []))[-1]) > float(list(sum(S1))[-1]))) or (length > 2):
                        c2 = S1
                        c2[-1].append(float(list(sum(S2, []))[-1]))
                        candidateTwoSequence.append(c2)

                # print("Candidate 1 sequence are ", candidateOneSequence)
                # print("Candidate 2 sequence are ", candidateTwoSequence)






            else:

                S1New =deleteNthItem(S1, 0)
                S2New =deleteNthItem(S2, -1)

                if S1New == S2New:
                    Sj = deepcopy(S1)
                    if len(S2[-1]) == 1:
                        Sj.append(S2[-1])
                    else:
                        Sj[-1].append(S2[-1][-1])
                    cNext.append(Sj)

    return list(filter(lambda x: checkForSubsets(x, FK), cNext))





# Function to generate Frequent 1 itmeset
def generateF1set(L, misDict, supportCount):
    F1set = []
    for x in L:
        if supportCount[x] >= misDict[x]:
            F1set.append(x)
    return F1set


#
# # Candidate 2 generation
# def generateCandidate2itemset(L, supportCount, minimumSupportDict, multiSequenceList):
#     sdc = supportCount['SDC']
#     c2 = []
#     maxCount = len(multiSequenceList)-1
#
#     for x in f1:
#         ind = f1.index(x)
#         toBeCheckedItems = f1[0:ind] + f1[ind+1:]
#         for item in toBeCheckedItems:
#             if float(supportCount[item]/maxCount)>=float(minimumSupportDict[x]):
#                 if abs((supportCount[x]-supportCount[item])/maxCount)<=sdc:
#                     c2.append([x, item])
#                     c2.append([[x], [item]])
#
#     return c2


def getFirstItemMis(candidate, minimumSupportDict):
    flattened_item_set = list(sum(candidate, []))
    return minimumSupportDict.get(flattened_item_set[0])


def filterF2(candidate, multiSequenceList):
    flattened_item_set = list(sum(candidate, []))
    min_val = compute_support([[(flattened_item_set[0])]], multiSequenceList)
    return all(list(map(lambda item :  compute_support([[item]], multiSequenceList) >= min_val, flattened_item_set[1:])))


def checkSDCConstraint(candidate, minimumSupportDict, multiSequenceList):
    flattened_item_set = set(sum(candidate, []))
    key = lambda item : compute_support([[item]], multiSequenceList)
    max_support_value = key(max(flattened_item_set, key=key))
    min_support_value = key(min(flattened_item_set, key=key))
    return (max_support_value - min_support_value) <= minimumSupportDict.get('SDC')


if __name__ == "__main__":
    # Read the files
    dataLocation, parametersLocation = location()

    dataContents = readFile(dataLocation)
    parametersContents = readFile(parametersLocation)
    outputFile = open(os.path.join("data", "input", "output.txt"), "w")
    minimumSupportDict = standardizeParametersContents(parametersContents)
    sortByMinimumSupport = lambda x: (minimumSupportDict.get(x, 1000), x)

    # print("The contents of data file are : {}\n".format(dataContents))
    # print("The contents of parameters are : {}\n".format(minimumSupportDict))

    # multiSequenceList : List of userData (each line of input file is a userData)
    # userData : List of transactions
    # transaction : List of items.
    multiSequenceList = generate_multi_sequence_list(dataContents)

    M = list(sorted(set(sum(sum(multiSequenceList, []), [])), key=sortByMinimumSupport))
    L = createL(M, minimumSupportDict, multiSequenceList)
    F1 = list(filter(lambda item: compute_support([[item]], multiSequenceList) > minimumSupportDict.get(item), L))
    k = 2

    # [print(item, compute_support([[item]], multiSequenceList), minimumSupportDict.get(item)) for item in M]
    # print("L Sequence generated is : {}\n".format(L))
    # print("F1 set is {}".format(F1))

    # [[item]] is the standard form of an item sequence. we use this format
    # so that [[50, 60]], [[50],[60,70],[90]] are all uniformly represented.
    # Fk is an array of such item sequences. so the third bracket.
    # F is the array of all such Fks. so the fourth bracket.
    F = [[[[x]] for x in F1]]
    while True:
        if k == 2:
            CK = level2_candidate_gen(L, multiSequenceList, minimumSupportDict)
        else:
            CK = MS_candidate_gen(F[k - 2], minimumSupportDict)
        CK = list(filter(lambda candidate: checkSDCConstraint(candidate, minimumSupportDict, multiSequenceList), CK))
        FK = list(filter(
            lambda candidate: compute_support(candidate, multiSequenceList) >= getFirstItemMis(candidate, minimumSupportDict),
            CK))
        if len(FK) == 0:
            break
        # print("F" + str(k) + " set is : ")
        # for sequence in FK:
        #     print(sequence)
        F.append(FK)
        k += 1
    for index, f in enumerate(F):
        outputFile.write("The number of length " + str(index + 1) + " sequential patterns is " + str(len(f)) + '\n')
        for itemGroup in f:
            itemString = str(itemGroup).replace("[", "{").replace("]", "}")[1:-1]
            print("Pattern:<" + itemString + ">:Count=" + str(int(compute_support(itemGroup, multiSequenceList) * len(multiSequenceList))) + '\n')
            outputFile.write("Pattern:<" + itemString + ">:Count=" + str(round(compute_support(itemGroup, multiSequenceList) * len(multiSequenceList))) + '\n')