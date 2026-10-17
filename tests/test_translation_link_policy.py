import ast
import importlib.util
import pathlib
import sys
import unittest
from unittest.mock import patch
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'automation'))
import translation_link_policy as lp
import article_link_policy as ap

SITE = ap.SITE
FA = SITE + '/fa-quinoa/'
EN = SITE + '/en-quinoa/'
AR = SITE + '/ar-quinoa/'

def page(url, lang, alternates=None, **overrides):
    body = '<html lang="'+lang+'"><head><title>Quinoa irrigation</title><link rel="canonical" href="'+url+'">'
    for language, target in (alternates or {}).items():
        body += '<link rel="alternate" hreflang="'+language+'" href="'+target+'">'
    body += '</head><body>Quinoa irrigation</body></html>'
    return {'status':200,'url':url,'headers':{'Content-Type':'text/html'},'body':body,**overrides}

def body(url): return '<p>Read <a href="'+url+'">Quinoa irrigation guide</a>.</p>'

class TranslationLinkTests(unittest.TestCase):
    def resolve(self, data, source=FA, lang='en-US', **kw):
        return lp.localize_links(body(source), lang, fetcher=lambda u:data[u], **kw)
    def test_exact_reciprocal_sibling(self):
        data={FA:page(FA,'fa-IR',{'en-US':EN}),EN:page(EN,'en-US',{'fa-IR':FA})}
        result=self.resolve(data)
        self.assertEqual(result,body(EN))
    def test_already_same_language(self):
        self.assertEqual(self.resolve({EN:page(EN,'en-US')},EN),body(EN))
    def test_missing_sibling_rejected(self):
        with self.assertRaises(lp.LinkPolicyError):self.resolve({FA:page(FA,'fa-IR')})
    def test_nonreciprocal_rejected(self):
        with self.assertRaises(lp.LinkPolicyError):self.resolve({FA:page(FA,'fa-IR',{'en-US':EN}),EN:page(EN,'en-US')})
    def test_wrong_language_rejected(self):
        with self.assertRaises(lp.LinkPolicyError):self.resolve({FA:page(FA,'fa-IR',{'en-US':EN}),EN:page(EN,'ar-IQ',{'fa-IR':FA})})
    def test_redirect_rejected(self):
        with self.assertRaises(lp.LinkPolicyError):self.resolve({FA:page(FA,'fa-IR',status=301)})
    def test_bad_canonical_rejected(self):
        wrong=page(EN,'en-US');wrong['body']=wrong['body'].replace('href="'+EN+'"','href="'+FA+'"')
        with self.assertRaises(lp.LinkPolicyError):self.resolve({EN:wrong},EN)
    def test_noindex_rejected(self):
        with self.assertRaises(lp.LinkPolicyError):self.resolve({EN:page(EN,'en-US',headers={'Content-Type':'text/html','X-Robots-Tag':'noindex'})},EN)
    def test_technical_object_rejected(self):
        with self.assertRaises(lp.LinkPolicyError):lp.localize_links(body(SITE+'/acf-field/p1/'),'en-US',fetcher=lambda u:None)
    def test_query_and_fragment_destinations_rejected(self):
        for suffix in ('?x=1','#detail'):
            with self.subTest(suffix=suffix),self.assertRaises(lp.LinkPolicyError):self.resolve({},EN+suffix)
    def test_external_links_unchanged(self):
        b=body(EN)+'<a href="https://example.org/research">Study</a><a href="#details">Contents</a>'
        self.assertEqual(lp.localize_links(b,'en-US',fetcher=lambda u:page(u,'en-US')),b)
    def test_mislabelled_anchor_rejected(self):
        with self.assertRaises(lp.LinkPolicyError):
            lp.localize_links(body(EN).replace('Quinoa irrigation guide','Asparagus planting'), 'en-US', fetcher=lambda u:page(u,'en-US'))
    def test_generic_anchor_rejected(self):
        with self.assertRaises(lp.LinkPolicyError):
            lp.localize_links(body(EN).replace('Quinoa irrigation guide','Related article'), 'en-US', fetcher=lambda u:page(u,'en-US'))
    def test_duplicate_destinations_rejected(self):
        with self.assertRaises(lp.LinkPolicyError):lp.localize_links(body(EN)*2,'en-US',fetcher=lambda u:page(u,'en-US'))
    def test_hex_anchor_rejected(self):
        with self.assertRaises(lp.LinkPolicyError):lp.localize_links(body(EN).replace('Quinoa irrigation guide','D985D8A7D984D8A7'),'en-US',fetcher=lambda u:page(u,'en-US'))
    def test_long_article_requires_several_unique_links(self):
        with self.assertRaises(lp.LinkPolicyError):lp.localize_links('<p>'+('irrigation '*1000)+'</p>'+body(EN),'en-US',fetcher=lambda u:page(u,'en-US'))
    def test_length_proportional_count(self):
        self.assertEqual(lp.count_bounds('word '*150),(1,1)); self.assertEqual(lp.count_bounds('word '*600),(2,3)); self.assertEqual(lp.count_bounds('word '*1200),(3,6))
    def test_caffeine_mistranslation_blocked(self):
        with self.assertRaises(lp.LinkPolicyError):lp.validate_crop('آبیاری اسپرس','Coffee irrigation','Coffee cultivation','en-US')
    def test_source_sainfoin_coffee_contradiction_blocked(self):
        with self.assertRaises(lp.LinkPolicyError): lp.validate_crop('آبیاری اسپرس','آبیاری اسپرس','اسپرس (Coffea arabica)','fa-IR')
    def test_muskmelon_pumpkin_contradiction_blocked(self):
        with self.assertRaises(lp.LinkPolicyError): lp.validate_crop('آبیاری طالبی','آبیاری طالبی','طالبی (Pumpkin)','fa-IR')
    def test_safflower_understory_contradiction_blocked(self):
        with self.assertRaises(lp.LinkPolicyError): lp.validate_crop('آبیاری گلرنگ','آبیاری گلرنگ','گلرنگ (Grazing or Understory cropping)','fa-IR')
    def test_valid_crop_identity(self):
        lp.validate_crop('آبیاری کینوا','Quinoa irrigation','Quinoa cultivation','en-US')
    def test_persian_crop_selection_not_generic_overlap(self):
        links=[{'url':FA,'title':'نکات عملی آبیاری جو','post_type':'post'},{'url':EN,'title':'آبیاری کینوا','post_type':'post'}]
        with patch.object(ap,'verified',return_value=True):
            self.assertEqual([x['url'] for x in ap.select_links({'title':'نکات عملی آبیاری کینوا'},links)],[EN])
    def test_persian_sql_builder_rejects_unsafe_links(self):
        import article_content_queue as q
        with self.assertRaises(lp.LinkPolicyError):
            q.sql_for({'title':'مقاله'}, {'title':'مقاله','html':'<p>متن بدون لینک</p>'}, [])

    def test_original_sql_builder_uses_gate(self):
        p=ROOT/'automation/translate_generated_articles.py';tree=ast.parse(p.read_text())
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='build_sql')
        self.assertTrue(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='prepare_translation_html' for n in ast.walk(fn)))
    def test_cached_artifacts_use_gate(self):
        p=ROOT/'automation/translate_generated_articles.py';text=p.read_text()
        self.assertIn('cleaned_html = prepare_translation_html(item, translated, lang)',text)
        self.assertIn('cleaned = base.prepare_translation_html(item, translated, LANG)',(ROOT/'automation/translate_russian_articles.py').read_text())

if __name__ == '__main__': unittest.main()
