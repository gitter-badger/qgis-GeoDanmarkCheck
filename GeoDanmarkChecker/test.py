# coding=utf-8
import fot.featuretype
import fot.qgisapp
from fot.rules.dataset.singlelayer import UniqueAttributeValue
from fot.rules.dataset.singlelayer import AttributeRule
from fot.rules.dualdataset.compareattributes import AttributesMustNotBeChanged
from fot.repository import Repository
from fot.reporter import Reporter
from fot.geomutils.featurematcher import PolygonMatcher, LineMatcher

from fot.rules import RuleExecutor

rules = []
if True:
    rules.append(
        AttributeRule(
            'Stream.vandloebstype',
            fot.featuretype.VANDLOEBSMIDTE_BRUDT,
            attributename='vandloebstype',
            isvalidfunction=lambda val: val in [u'XXAlmindelig', u'Gennem sø', u'Rørlagt']
            # validvalues=[u'XXAlmindelig', u'Gennem sø', u'Rørlagt'] #[u'Almindelig', u'Gennem sø', u'Rørlagt']
        )
    )

    rules.append(
        UniqueAttributeValue(
            'Building UUID unique',
            feature_type=fot.featuretype.BYGNING,
            attributename='bygning_id',
            filter='bygning_id IS NOT NULL'
        )
    )

    rules.append(
        AttributesMustNotBeChanged(
            'Unchanged building UUID',
            feature_type=fot.featuretype.BYGNING,
            unchangedattributes=['bygning_id'],
            featurematcher=PolygonMatcher(relativeareadeviation=0.5),
            #beforefilter='bygning_id IS NOT NULL'
        )
    )

vejmatchoptions = {'minimumintersectionlength': 1.0}  # Vi gider ikke høre om stykker kortere end 1 meter
rules.append(
    AttributesMustNotBeChanged(
        'Unchanged road attribs',
        feature_type=fot.featuretype.VEJMIDTE_BRUDT,
        unchangedattributes=['kommunekode', 'vejkode'],
        featurematcher=LineMatcher(**vejmatchoptions),
        beforefilter='bygning_id IS NOT NULL'
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

