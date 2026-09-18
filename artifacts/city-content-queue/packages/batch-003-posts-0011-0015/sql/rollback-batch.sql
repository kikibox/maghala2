-- Rollback SQL for this 5-post package

-- rollback: 10000010002017-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='خشکرود-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='خشکرود-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='خشکرود-مرکزی-navar-tip-20cm' AND p.post_type='arak'; DELETE FROM `ha_posts` WHERE post_name='خشکرود-مرکزی-navar-tip-20cm' AND post_type='arak'; COMMIT;


-- rollback: 10000010002017-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='خشکرود-مرکزی-looleh-nakhi-tashoo' AND post_type='arak' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='خشکرود-مرکزی-looleh-nakhi-tashoo' AND post_type='arak' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='خشکرود-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak'; DELETE FROM `ha_posts` WHERE post_name='خشکرود-مرکزی-looleh-nakhi-tashoo' AND post_type='arak'; COMMIT;


-- rollback: 10000010002378-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رازقان-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رازقان-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='رازقان-مرکزی-navar-tip-20cm' AND p.post_type='arak'; DELETE FROM `ha_posts` WHERE post_name='رازقان-مرکزی-navar-tip-20cm' AND post_type='arak'; COMMIT;


-- rollback: 10000010002378-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رازقان-مرکزی-looleh-nakhi-tashoo' AND post_type='arak' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رازقان-مرکزی-looleh-nakhi-tashoo' AND post_type='arak' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='رازقان-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak'; DELETE FROM `ha_posts` WHERE post_name='رازقان-مرکزی-looleh-nakhi-tashoo' AND post_type='arak'; COMMIT;


-- rollback: 10000010001108-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='زاویه-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='زاویه-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='زاویه-مرکزی-navar-tip-20cm' AND p.post_type='arak'; DELETE FROM `ha_posts` WHERE post_name='زاویه-مرکزی-navar-tip-20cm' AND post_type='arak'; COMMIT;

