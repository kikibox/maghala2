<?php
/**
 * Plugin Name: Navar TJ ads - hide from article lists
 * Description: Keeps the Tajikistan ad posts (categories tajikistan-ads-tg / tajikistan-ads-ru) out of the home page post list, feeds, date/author/tag archives and the related-articles lists, while the posts stay public, indexable and in the sitemap.
 * Version: 1.0
 */
if (!defined('ABSPATH')) { exit; }

function navar_tj_ads_term_ids() {
    static $ids = null;
    if ($ids !== null) { return $ids; }
    $ids = array();
    foreach (array('tajikistan-ads-tg', 'tajikistan-ads-ru') as $slug) {
        $t = get_term_by('slug', $slug, 'category');
        if ($t && !is_wp_error($t)) { $ids[] = (int) $t->term_id; }
    }
    return $ids;
}

add_action('pre_get_posts', function ($q) {
    if (is_admin() || !$q->is_main_query()) { return; }
    // Own category archive stays reachable; everything else hides the ad posts.
    if ($q->is_category() || $q->is_single() || $q->is_page() || $q->is_search()) { return; }
    $ids = navar_tj_ads_term_ids();
    if ($ids) { $q->set('category__not_in', array_merge((array) $q->get('category__not_in'), $ids)); }
});

// Secondary article lists (theme "latest/related articles" blocks that run WP_Query with post_type=post).
add_action('pre_get_posts', function ($q) {
    if (is_admin() || $q->is_main_query()) { return; }
    if ($q->get('navar_include_tj_ads') || $q->get('cat') || $q->get('category_name') || $q->get('category__in') || $q->get('p') || $q->get('name') || $q->get('pagename')) { return; }
    $pt = $q->get('post_type');
    if ($pt !== 'post' && $pt !== '' && $pt !== null) { return; }
    $ids = navar_tj_ads_term_ids();
    if ($ids) { $q->set('category__not_in', array_merge((array) $q->get('category__not_in'), $ids)); }
});
