<?php
/**
 * Plugin Name: Navar Sidebar Language Filter
 * Description: Prevents mixed-language sidebar posts and fixes return to Persian from translated articles.
 * Version: 1.1.0
 * Author: Navar Abyari
 */
if (!defined('ABSPATH')) exit;
function navar_sidebar_lang_normalize($value) {
    $value = strtolower(sanitize_key((string) $value));
    $map = array('iran'=>'fa-IR','fa'=>'fa-IR','fa-ir'=>'fa-IR','persian'=>'fa-IR','iraq'=>'ar-IQ','iq'=>'ar-IQ','ar'=>'ar-IQ','ar-iq'=>'ar-IQ','arabic'=>'ar-IQ','tajikistan'=>'tg-TJ','tj'=>'tg-TJ','tg'=>'tg-TJ','tg-tj'=>'tg-TJ','tajik'=>'tg-TJ');
    return isset($map[$value]) ? $map[$value] : '';
}
function navar_sidebar_current_language() {
    if (isset($_GET['navar_lang'])) { $v=navar_sidebar_lang_normalize(wp_unslash($_GET['navar_lang'])); if ($v) return $v; }
    $id=absint(get_queried_object_id());
    if ($id) { $v=(string)get_post_meta($id,'_navar_translation_language',true); if ($v==='ar-IQ'||$v==='tg-TJ') return $v; if ($id>=502015&&$id<=502320) return (($id-502015)%2===0)?'ar-IQ':'tg-TJ'; }
    $path=isset($_SERVER['REQUEST_URI'])?wp_parse_url(wp_unslash($_SERVER['REQUEST_URI']),PHP_URL_PATH):'';
    if (is_string($path)) { if (preg_match('#^/iq(?:/|$)#i',$path)) return 'ar-IQ'; if (preg_match('#^/tj(?:/|$)#i',$path)) return 'tg-TJ'; }
    return 'fa-IR';
}
function navar_sidebar_language_clause($language) {
    if ($language==='ar-IQ'||$language==='tg-TJ') return array('key'=>'_navar_translation_language','value'=>$language,'compare'=>'=');
    return array('relation'=>'OR',array('key'=>'_navar_translation_language','compare'=>'NOT EXISTS'),array('key'=>'_navar_translation_language','value'=>'','compare'=>'='));
}
function navar_sidebar_apply_language_filter($query) {
    if (is_admin()||!($query instanceof WP_Query)||$query->is_main_query()||$query->get('navar_allow_mixed_languages')) return;
    $type=$query->get('post_type'); if ($type&&$type!=='post'&&$type!=='any'&&$type!==array('post')) return;
    $clause=navar_sidebar_language_clause(navar_sidebar_current_language()); $existing=$query->get('meta_query');
    $query->set('meta_query',is_array($existing)&&$existing?array('relation'=>'AND',$existing,$clause):array($clause));
}
add_action('pre_get_posts','navar_sidebar_apply_language_filter',999);
add_filter('widget_posts_args',function($args){$clause=navar_sidebar_language_clause(navar_sidebar_current_language());$existing=isset($args['meta_query'])&&is_array($args['meta_query'])?$args['meta_query']:array();$args['meta_query']=$existing?array('relation'=>'AND',$existing,$clause):array($clause);$args['suppress_filters']=false;return $args;},999);
function navar_sidebar_persian_source_id($post_id) {
    $post_id=absint($post_id); if (!$post_id) return 0; $language=(string)get_post_meta($post_id,'_navar_translation_language',true);
    if ($language!=='ar-IQ'&&$language!=='tg-TJ'&&!($post_id>=502015&&$post_id<=502320)) return 0;
    return absint(get_post_meta($post_id,'_navar_translation_source_id',true));
}
add_action('template_redirect',function(){
    if (!is_singular('post')||!isset($_GET['navar_lang'])||navar_sidebar_lang_normalize(wp_unslash($_GET['navar_lang']))!=='fa-IR') return;
    $source=navar_sidebar_persian_source_id(get_queried_object_id()); if (!$source||get_post_status($source)!=='publish') return;
    wp_safe_redirect(add_query_arg('navar_lang','iran',get_permalink($source)),302,'Navar Persian Return Fix'); exit;
},0);
add_action('wp_footer',function(){
    if (!is_singular('post')) return; $source=navar_sidebar_persian_source_id(get_queried_object_id()); if (!$source||get_post_status($source)!=='publish') return;
    $destination=add_query_arg('navar_lang','iran',get_permalink($source)); ?>
<script id="navar-persian-return-fix-v110">(()=>{const destination=<?php echo wp_json_encode($destination,JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE); ?>,selector='a,button,[role="button"]',isPersian=el=>{const text=(el.textContent||'').replace(/\s+/g,' ').trim(),attrs=[el.getAttribute('data-lang'),el.getAttribute('data-language'),el.getAttribute('hreflang'),el.getAttribute('title'),el.getAttribute('aria-label')].filter(Boolean).join(' ');return /فارسی|ایران/.test(text+' '+attrs)||/(^|\s)FA($|\s)/i.test(text+' '+attrs)},patch=root=>{if(!root.querySelectorAll)return;for(const el of root.querySelectorAll(selector)){if(!isPersian(el))continue;if(el.tagName==='A')el.href=destination;el.dataset.navarPersianTarget=destination}};patch(document);new MutationObserver(cs=>cs.forEach(c=>c.addedNodes.forEach(n=>n.nodeType===1&&patch(n)))).observe(document.documentElement,{childList:true,subtree:true});document.addEventListener('click',event=>{const el=event.target.closest(selector);if(!el||!isPersian(el))return;event.preventDefault();event.stopImmediatePropagation();window.location.assign(destination)},true)})();</script>
<?php },9999);
