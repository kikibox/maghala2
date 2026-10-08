<?php
/**
 * Plugin Name: Navar Tajikistan Ads (CPT)
 * Description: Custom post type "tajikistan" for Tajik (Cyrillic) advertising posts. Kept separate from articles (post) on purpose.
 * Version: 1.0.0
 * Author: AFP / navar-abyari.ir
 *
 * Install: upload to wp-content/plugins/navar-tajikistan-ads/navar-tajikistan-ads.php (or mu-plugins/) and activate.
 * Then: Settings → Permalinks → Save (flushes rewrite rules once; the plugin also flushes once automatically).
 * URL scheme: https://navar-abyari.ir/tajikistan/{latin-slug}/ ; archive: /tajikistan/
 */
if (!defined('ABSPATH')) { exit; }

add_action('init', function () {
    register_post_type('tajikistan', array(
        'labels' => array(
            'name'          => 'Эълонҳои Тоҷикистон',
            'singular_name' => 'Эълони Тоҷикистон',
            'add_new_item'  => 'Илова кардани эълон',
            'edit_item'     => 'Таҳрири эълон',
            'all_items'     => 'Ҳамаи эълонҳо',
            'menu_name'     => 'Tajikistan Ads',
        ),
        'public'              => true,
        'publicly_queryable'  => true,
        'show_ui'             => true,
        'show_in_rest'        => true,
        'exclude_from_search' => false,
        'has_archive'         => 'tajikistan',
        'rewrite'             => array('slug' => 'tajikistan', 'with_front' => false),
        'menu_icon'           => 'dashicons-megaphone',
        'menu_position'       => 26,
        'supports'            => array('title', 'editor', 'excerpt', 'thumbnail', 'custom-fields', 'revisions'),
        'taxonomies'          => array(),
    ));
}, 5);

// One-time rewrite flush after the plugin is first activated/updated.
add_action('init', function () {
    if (get_option('navar_tj_ads_rewrite_v') !== '1.0.0') {
        flush_rewrite_rules(false);
        update_option('navar_tj_ads_rewrite_v', '1.0.0', false);
    }
}, 99);

// Language hint for themes/plugins that read the language from post meta (set by the SQL as well).
add_filter('language_attributes', function ($out) {
    if (is_singular('tajikistan') || is_post_type_archive('tajikistan')) {
        return preg_replace('/lang="[^"]*"/', 'lang="tg-TJ"', $out);
    }
    return $out;
});

// Never index drafts / keep ad posts out of the articles feed.
add_action('pre_get_posts', function ($q) {
    if (!is_admin() && $q->is_main_query() && ($q->is_home() || $q->is_feed()) && !$q->get('post_type')) {
        $q->set('post_type', 'post');
    }
});

// Admin column: place / product / crop (from post meta written by the pipeline).
add_filter('manage_tajikistan_posts_columns', function ($cols) {
    $cols['navar_tj_meta'] = 'Макон · маҳсулот · зироат';
    return $cols;
});
add_action('manage_tajikistan_posts_custom_column', function ($col, $id) {
    if ($col === 'navar_tj_meta') {
        echo esc_html(implode(' · ', array_filter(array(
            get_post_meta($id, '_navar_tj_place_name', true),
            get_post_meta($id, '_navar_tj_product', true),
            get_post_meta($id, '_navar_tj_crop', true),
        ))));
    }
}, 10, 2);
