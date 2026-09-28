-- Roll back generated article translations.
SET NAMES utf8mb4;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-130:tg-TJ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-130:en-US' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-130:ar-IQ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-119:tg-TJ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-119:en-US' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-119:ar-IQ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-114:tg-TJ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-114:en-US' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;

START TRANSACTION; SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='article-translation:crop-114:ar-IQ' LIMIT 1); DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;
