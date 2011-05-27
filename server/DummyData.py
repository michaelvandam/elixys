#!/usr/bin/python26

# Dummy sequence metadata
def GetDefaultSequenceMetadata():
    return {"name":"FAC synthesis",
        "time":"8:00",
        "date":"05/01/2012",
        "comment":"Routine FAC synthesis",
        "id":1,
        "creator":"devel",
        "operations":17}

# Dummy sequence components
def GetDefaultSequenceComponents():
    return [{"componenttype":"CASSETTE",
        "name":"Cassette 1",
        "id":1,
        "reactor":1,
        "validationerror":False,
        "available":True,
        "reagents":[1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10]},
        {"componenttype":"CASSETTE",
        "name":"Cassette 2",
        "id":2,
        "reactor":2,
        "validationerror":False,
        "available":True,
        "reagents":[11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20]},
        {"componenttype":"CASSETTE",
       "name":"Cassette 3",
       "id":3,
       "reactor":3,
        "validationerror":False,
        "available":False,
        "reagents":[21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30]},
        {"componenttype":"ADD",
        "name":"Add F-18",
        "id":4,
        "reactor":1,
        "validationerror":False,
        "reagent":"1"},
        {"componenttype":"EVAPORATE",
        "name":"Evaporate",
        "id":5,
        "reactor":1,
        "validationerror":False,
        "duration":"00:05.00",
        "evaporationtemperature":"165.0",
        "finaltemperature":"35.0",
        "stirspeed":"500"},
        {"componenttype":"TRANSFER",
        "name":"Transfer",
        "id":6,
        "reactor":1,
        "validationerror":False,
        "target":"3"},
        {"componenttype":"ELUTE",
        "name":"Elute",
        "id":7,
        "reactor":1,
        "validationerror":False,
        "reagent":12,
        "target":2},
        {"componenttype":"REACT",
        "name":"React",
        "id":8,
        "reactor":1,
        "validationerror":False,
        "position":1,
        "duration":"00:04.30",
        "reactiontemperature":"165.0",
        "finaltemperature":"35.0",
        "stirspeed":"500"},
        {"componenttype":"PROMPT",
        "name":"Prompt",
        "id":9,
        "reactor":0,
        "validationerror":False,
        "message":"Please take a sample for analysis"},
        {"componenttype":"INSTALL",
        "name":"Install",
        "id":10,
        "reactor":1,
        "validationerror":False,
        "message":"Take a radiation measurement"},
        {"componenttype":"COMMENT",
        "name":"Comment",
        "id":11,
        "reactor":0,
        "validationerror":False,
        "comment":"Bromination and cytosine coupling"},
        {"componenttype":"ACTIVITY",
        "name":"Activity",
        "id":12,
        "reactor":1,
        "validationerror":False}]

# Dummy sequence reagents
def GetDefaultSequenceReagents():
    return [{"available":True,
        "reagentid":1,
        "componentid":1,
        "position":"1",
        "name":"F-18",
        "description":"18F-/K222/K2CO3"},
        {"available":True,
        "reagentid":2,
        "componentid":1,
        "position":"2",
        "name":"MeCN1",
        "description":"Acetonitrile"},
        {"available":True,
        "reagentid":3,
        "componentid":1,
        "position":"3",
        "name":"MeCN2",
        "description":"Acetonitrile"},
        {"available":True,
        "reagentid":4,
        "componentid":1,
        "position":"4",
        "name":"MeCN3",
        "description":"Acetonitrile"},
        {"available":True,
        "reagentid":5,
        "componentid":1,
        "position":"5",
        "name":"H2O1",
        "description":"Water"},
        {"available":True,
        "reagentid":6,
        "componentid":1,
        "position":"6",
        "name":"H2O2",
        "description":"Water"},
        {"available":True,
        "reagentid":7,
        "componentid":1,
        "position":"7",
        "name":"HBr",
        "description":"Hydrobromic acid"},
        {"available":False,
        "reagentid":8,
        "componentid":1,
        "position":"8",
        "name":"",
        "description":""},
        {"available":True,
        "reagentid":9,
        "componentid":1,
        "position":"A",
        "name":"QMA",
        "description":"QMA column"},
        {"available":True,
        "reagentid":10,
        "componentid":1,
        "position":"B",
        "name":"Seppak1",
        "description":"Sep-Pak"},
        {"available":True,
        "reagentid":11,
        "componentid":2,
        "position":"1",
        "name":"C6H12O6",
        "description":"Sugar (yum!)"},
        {"available":True,
        "reagentid":12,
        "componentid":2,
        "position":"2",
        "name":"HCl",
        "description":"Hydrochloric acid"},
        {"available":False,
        "reagentid":13,
        "componentid":2,
        "position":"3",
        "name":"",
        "description":""},
        {"available":True,
        "reagentid":14,
        "componentid":2,
        "position":"4",
        "name":"H2",
        "description":"Hydrogen gas"},
        {"available":False,
        "reagentid":15,
        "componentid":2,
        "position":"5",
        "name":"",
        "description":""},
        {"avalilable":True,
        "reagentid":16,
        "componentid":2,
        "position":"6",
        "name":"KCl",
        "description":"Potassium chloride"},
        {"available":False,
        "reagentid":17,
        "componentid":2,
        "position":"7",
        "name":"",
        "description":""},
        {"available":True,
        "reagentid":18,
        "componentid":2,
        "position":"8",
        "name":"N2",
        "description":"Liquid nitrogen"},
        {"available":True,
        "reagentid":19,
        "componentid":2,
        "position":"A",
        "name":"Seppak2",
        "description":"Sep-Pak"},
        {"available":False,
        "reagentid":20,
        "componentid":2,
        "position":"B",
        "name":"",
        "description":""}]
