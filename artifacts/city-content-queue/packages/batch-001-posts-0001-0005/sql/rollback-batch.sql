-- Rollback SQL for this 5-post package

-- rollback: 1000001002536-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='داودآباد-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='داودآباد-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='داودآباد-مرکزی-navar-tip-20cm' AND p.post_type='arak'; DELETE FROM `ha_posts` WHERE post_name='داودآباد-مرکزی-navar-tip-20cm' AND post_type='arak'; COMMIT;


-- rollback: 1000001002536-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='داودآباد-مرکزی-looleh-nakhi-tashoo' AND post_type='arak' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='داودآباد-مرکزی-looleh-nakhi-tashoo' AND post_type='arak' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='داودآباد-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak'; DELETE FROM `ha_posts` WHERE post_name='داودآباد-مرکزی-looleh-nakhi-tashoo' AND post_type='arak'; COMMIT;


-- rollback: 1000001002074-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ساروق-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ساروق-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='ساروق-مرکزی-navar-tip-20cm' AND p.post_type='arak'; DELETE FROM `ha_posts` WHERE post_name='ساروق-مرکزی-navar-tip-20cm' AND post_type='arak'; COMMIT;


-- rollback: 1000001002074-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ساروق-مرکزی-looleh-nakhi-tashoo' AND post_type='arak' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ساروق-مرکزی-looleh-nakhi-tashoo' AND post_type='arak' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='ساروق-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak'; DELETE FROM `ha_posts` WHERE post_name='ساروق-مرکزی-looleh-nakhi-tashoo' AND post_type='arak'; COMMIT;


-- rollback: 1000001001600-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='کارچان-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='کارچان-مرکزی-navar-tip-20cm' AND post_type='arak' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='کارچان-مرکزی-navar-tip-20cm' AND p.post_type='arak'; DELETE FROM `ha_posts` WHERE post_name='کارچان-مرکزی-navar-tip-20cm' AND post_type='arak'; COMMIT;

