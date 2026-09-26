-- Roll back generated article translations.
SET NAMES utf8mb4;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-033:tg-TJ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-033:en-US' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-033:ar-IQ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-031:tg-TJ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-031:en-US' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-031:ar-IQ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-030:tg-TJ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-030:en-US' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-030:ar-IQ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-029:tg-TJ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-029:en-US' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-029:ar-IQ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;
