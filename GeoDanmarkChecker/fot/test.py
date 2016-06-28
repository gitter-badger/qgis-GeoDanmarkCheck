# coding=utf-8
import qgisapp
from repository import Repository
from rules.singlefeature.attributerule import AttributeRule
from rules.layer.uniqueattributevalue import UniqueAttributeValue
import featuretype
from rules.executor import SingleRepoExecutor
from reporter import Reporter

rules = []
rules.append(
    AttributeRule(
        featuretype.VANDLOEBSMIDTE_BRUDT,
        attributename='vandloebstype',
        isvalidfunction=lambda val: val in [u'XXAlmindelig', u'Gennem sø', u'Rørlagt']
        # validvalues=[u'XXAlmindelig', u'Gennem sø', u'Rørlagt'] #[u'Almindelig', u'Gennem sø', u'Rørlagt']
    )
)

rules.append(
    UniqueAttributeValue(
        feature_type=featuretype.BYGNING,
        attributename='bygning_id',
        filter='bygning_id IS NOT NULL'
    )
)

with qgisapp.QgisStandaloneApp(True) as app:
    print "App initialised"
    reporter = Reporter("dummyfilename")
    rep = Repository(u'/Volumes/Macintosh HD/Users/asger/Code/qgis-GeoDanmarkCheck/testdata/fot5.sqlite')
    exe = SingleRepoExecutor(rep, rules, reporter, None)
    exe.execute()

