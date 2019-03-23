MainIcon = 'app.ico'
MainWindowTitle = 'Удавчик'

AutosaveFile = 'autosave.dat'
QuicksaveFile = 'quicksave.dat'
NoAutosave = False

MinSpeed = 100
AccInterval = 2000 * 60
Accelerator = 0.9

BoxWidth = 20
BoxHeight = 20

DIFF_VERY_EASY = 1
DIFF_EASY = 2
DIFF_NORMAL = 3
DIFF_HARD = 4
DIFF_VERY_HARD = 5

Difficultys = {
    DIFF_VERY_EASY: {
        'InitialSpeed': 1000,
        'Freeze': True,
        'Barriers': 1,
        'EngName': 'Very Easy',
        'RuName': 'Очень Легкая'
    },
    DIFF_EASY: {
        'InitialSpeed': 800,
        'Freeze': True,
        'Barriers': 2,
        'EngName': 'Easy',
        'RuName': 'Легкая'
    },
    DIFF_NORMAL: {
        'InitialSpeed': 650,
        'Freeze': True,
        'Barriers': 4,
        'EngName': 'Normal',
        'RuName': 'Нормальная'
    },
    DIFF_HARD: {
        'InitialSpeed': 500,
        'Freeze': True,
        'Barriers': 6,
        'EngName': 'Hard',
        'RuName': 'Тяжелая'
    },
    DIFF_VERY_HARD: {
        'InitialSpeed': 1000,
        'Freeze': False,
        'Barriers': 2,
        'EngName': 'Very Hard',
        'RuName': 'Очень Тяжелая'
    }
}

FIELD_TYPE_NONE = 0
FIELD_TYPE_EATS1 = 1
FIELD_TYPE_EATS2 = 2
FIELD_TYPE_EATS3 = 3
FIELD_TYPE_EATS4 = 4
FIELD_TYPE_EATS5 = 5
FIELD_TYPE_HEAD = 6
FIELD_TYPE_BODY = 7
FIELD_TYPE_HOLE = 8
FIELD_TYPE_ROCK = 9

FIELD_GROUP_EMPTY = 'empty'
FIELD_GROUP_BOA = 'boa'
FIELD_GROUP_EATS = 'eats'
FIELD_GROUP_BARRIER = 'barrier'

AreaTypes = {
    FIELD_GROUP_EMPTY: (FIELD_TYPE_NONE,),
    FIELD_GROUP_BOA: (FIELD_TYPE_HEAD, FIELD_TYPE_BODY),
    FIELD_GROUP_EATS: (FIELD_TYPE_EATS1, FIELD_TYPE_EATS2, FIELD_TYPE_EATS3, FIELD_TYPE_EATS4, FIELD_TYPE_EATS5),
    FIELD_GROUP_BARRIER: (FIELD_TYPE_HOLE, FIELD_TYPE_ROCK)
}

DeathTypes = AreaTypes[FIELD_GROUP_BOA] + AreaTypes[FIELD_GROUP_BARRIER]

ARRANGE_HELIX = 0
ARRANGE_ZIGZAG = 1
ArrangeTypes = (ARRANGE_HELIX, ARRANGE_ZIGZAG)

Colors = {
    FIELD_TYPE_NONE: '#ece9d8',
    FIELD_TYPE_EATS1: '#ee7600',
    FIELD_TYPE_EATS2: '#ffff00',
    FIELD_TYPE_EATS3: '#cd1076',
    FIELD_TYPE_EATS4: '#0000cd',
    FIELD_TYPE_EATS5: '#cd0000',
    FIELD_TYPE_HEAD: '#008b00',
    FIELD_TYPE_BODY: ('#7fff00', '#ff1493'),
    FIELD_TYPE_HOLE: '#171717',
    FIELD_TYPE_ROCK: '#5e6965'
}

EatsRaiseInterval = 15

WIN_CODE = 0
LOSE_CODE = 1

SpWin_GradColor_1 = '#ff0000'
SpWin_GradColor_2 = '#0000ff'
SpLose_GradColor_1 = '#8b0000'
SpLose_GradColor_2 = '#ff0000'

SP_ALG_RANDOM = 0
SP_ALG_ALONG_BODY = 1