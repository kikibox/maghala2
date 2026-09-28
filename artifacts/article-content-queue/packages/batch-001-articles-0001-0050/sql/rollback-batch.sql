-- Roll back 50 generated articles (batch-001-articles-0001-0050)
SET NAMES utf8mb4;
USE `navaraby_wp569`;

-- article: crop-001
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-001' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-002
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-002' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-003
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-003' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-004
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-004' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-005
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-005' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-006
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-006' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-007
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-007' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-009
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-009' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-008
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-008' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-012
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-012' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-013
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-013' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-015
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-015' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-011
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-011' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-014
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-014' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-010
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-010' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-017
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-017' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-018
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-018' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-019
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-019' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-016
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-016' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-020
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-020' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-021
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-021' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-022
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-022' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-026
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-026' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-025
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-025' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-024
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-024' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-023
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-023' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-028
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-028' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-027
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-027' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-030
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-030' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-029
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-029' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-033
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-033' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-031
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-031' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-035
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-035' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-034
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-034' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-032
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-032' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-036
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-036' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-039
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-039' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-037
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-037' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-038
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-038' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-040
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-040' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-041
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-041' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-043
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-043' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-042
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-042' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-046
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-046' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-045
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-045' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-044
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-044' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-047
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-047' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-048
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-048' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-049
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-049' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;


-- article: crop-050
START TRANSACTION; SET @post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='article-content-queue:crop-050' LIMIT 1); DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=@post_id AND post_type='attachment'; DELETE FROM `ha_postmeta` WHERE post_id=@post_id; DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; DELETE FROM `ha_posts` WHERE ID=@post_id; COMMIT;

