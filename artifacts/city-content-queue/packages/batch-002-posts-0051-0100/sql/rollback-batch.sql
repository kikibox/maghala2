-- Rollback SQL for this 50-post package

-- rollback: 10100013001134-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='املش-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='املش-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='املش-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='املش-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 10100013001134-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='املش-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='املش-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='املش-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='املش-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 10100013002519-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رانکوه-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رانکوه-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='رانکوه-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='رانکوه-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010003001120-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='بندرانزلی-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='بندرانزلی-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='بندرانزلی-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='بندرانزلی-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010003001120-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='بندرانزلی-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='بندرانزلی-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='بندرانزلی-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='بندرانزلی-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 10100017001126-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='خمام-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='خمام-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='خمام-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='خمام-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 10100017001126-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='خمام-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='خمام-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='خمام-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='خمام-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 10100017001060-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='چوکام-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='چوکام-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='چوکام-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='چوکام-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;

