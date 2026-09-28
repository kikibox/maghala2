-- Roll back generated article translations.
SET NAMES utf8mb4;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-141:tg-TJ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-141:en-US' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-141:ar-IQ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-138:tg-TJ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-138:en-US' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-138:ar-IQ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-137:tg-TJ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-137:en-US' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-137:ar-IQ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;
