# coding=utf-8
import fot.featuretype
import fot.qgisapp
from fot.rules.dataset.singlelayer import UniqueAttributeValue
from fot.rules.dataset.singlelayer import AttributeRule
from fot.repository import Repository
from fot.reporter import Reporter

from fot.rules import RuleExecutor

rules = []
rules.append(
    AttributeRule(
        fot.featuretype.VANDLOEBSMIDTE_BRUDT,
        attributename='vandloebstype',
        isvalidfunction=lambda val: val in [u'XXAlmindelig', u'Gennem sø', u'Rørlagt']
        # validvalues=[u'XXAlmindelig', u'Gennem sø', u'Rørlagt'] #[u'Almindelig', u'Gennem sø', u'Rørlagt']
    )
)

rules.append(
    UniqueAttributeValue(
        feature_type=fot.featuretype.BYGNING,
        attributename='bygning_id',
        filter='bygning_id IS NOT NULL'
    )
)

with fot.qgisapp.QgisStandaloneApp(True) as app:
    print "App initialised"
    reporter = Reporter("dummyfilename")
    before = Repository(u'/Volumes/Macintosh HD/Users/asger/Code/qgis-GeoDanmarkCheck/testdata/mapped_fot4.sqlite')
    after = Repository(u'/Volumes/Macintosh HD/Users/asger/Code/qgis-GeoDanmarkCheck/testdata/fot5.sqlite')
    exe = RuleExecutor(before, after)
    exe.execute(rules, reporter, None)


    # from fot.geomutils import FeatureIndex
    # feats = after.read(fot.featuretype.BYGNING)
    # ix = FeatureIndex(feats, usespatialindex=True)
    # result = ix.geometryintersects( feats[0] )
    # print result

