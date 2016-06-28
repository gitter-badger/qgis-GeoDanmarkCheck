# coding=utf-8
import featuretype
import qgisapp
from rules.dataset.singlelayer import UniqueAttributeValue
from rules.dataset.singlelayer import AttributeRule
from GeoDanmarkChecker.fot.repository import Repository
from reporter import Reporter

from rules import RuleExecutor

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
    before = Repository(u'/Volumes/Macintosh HD/Users/asger/Code/qgis-GeoDanmarkCheck/testdata/fot5.sqlite')
    after = Repository(u'/Volumes/Macintosh HD/Users/asger/Code/qgis-GeoDanmarkCheck/testdata/fot5.sqlite')
    exe = RuleExecutor(before, after)
    exe.execute(rules, reporter, None)

