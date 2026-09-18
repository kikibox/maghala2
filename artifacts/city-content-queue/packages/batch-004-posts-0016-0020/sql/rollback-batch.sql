-- Rollback SQL for this 5-post package

-- rollback: 10000010001108-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='زاویه-مرکزی-looleh-nakhi-tashoo' AND post_type='arak' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='زاویه-مرکزی-looleh-nakhi-tashoo' AND post_type='arak' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='زاویه-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak'; DELETE FROM `ha_posts` WHERE post_name='زاویه-مرکزی-looleh-nakhi-tashoo' AND post_type='arak'; COMMIT;


-- rollback: 10000010001109-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='مامونیه-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='مامونیه-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='مامونیه-مرکزی-navar-tip-20cm' AND p.post_type='arak'; DELETE FROM `ha_posts` WHERE post_name='مامونیه-مرکزی-navar-tip-20cm' AND post_type='arak'; COMMIT;


-- rollback: 10000010001109-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='مامونیه-مرکزی-looleh-nakhi-tashoo' AND post_type='arak' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='مامونیه-مرکزی-looleh-nakhi-tashoo' AND post_type='arak' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='مامونیه-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak'; DELETE FROM `ha_posts` WHERE post_name='مامونیه-مرکزی-looleh-nakhi-tashoo' AND post_type='arak'; COMMIT;


-- rollback: 10000010002228-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='پرندک-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='پرندک-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='پرندک-مرکزی-navar-tip-20cm' AND p.post_type='arak'; DELETE FROM `ha_posts` WHERE post_name='پرندک-مرکزی-navar-tip-20cm' AND post_type='arak'; COMMIT;


-- rollback: 10000010002228-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='پرندک-مرکزی-looleh-nakhi-tashoo' AND post_type='arak' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='پرندک-مرکزی-looleh-nakhi-tashoo' AND post_type='arak' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='پرندک-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak'; DELETE FROM `ha_posts` WHERE post_name='پرندک-مرکزی-looleh-nakhi-tashoo' AND post_type='arak'; COMMIT;

