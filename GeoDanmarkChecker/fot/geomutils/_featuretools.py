def attributenames(f):
    [field.name() for field in f.fields()]

def changedattributes(f1, f2, checkattributes=None):
    attriblist = checkattributes if checkattributes else attributenames(f1)
    for attrib in attriblist:
        result = []
        try:
            if not f1[attrib] == f2[attrib]:
                message = u'Attribute {0} changed from {1} to {2}'.format(attrib, f1[attrib], f2[attrib])
        except KeyError as e:
            message = u'Attribute {0} not found'.format(attrib)
        if message:
            result.append((attrib, message))
