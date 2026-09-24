-- Rollback SQL for this 50-post package

-- rollback: 1010008002140-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='مرجقل-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='مرجقل-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='مرجقل-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='مرجقل-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010004002382-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='اسالم-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='اسالم-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='اسالم-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='اسالم-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010004002382-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='اسالم-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='اسالم-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='اسالم-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='اسالم-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010004002584-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='حویق-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='حویق-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='حویق-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='حویق-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010004002584-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='حویق-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='حویق-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='حویق-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='حویق-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010004002381-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لیسار-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لیسار-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='لیسار-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='لیسار-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010004002381-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لیسار-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لیسار-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='لیسار-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='لیسار-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010004002585-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='چوبر-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='چوبر-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='چوبر-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='چوبر-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010004002585-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='چوبر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='چوبر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='چوبر-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='چوبر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010009001142-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='فومن-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='فومن-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='فومن-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='فومن-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010009001142-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='فومن-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='فومن-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='فومن-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='فومن-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010009001143-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ماسوله-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ماسوله-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='ماسوله-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='ماسوله-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010009001143-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ماسوله-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ماسوله-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='ماسوله-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='ماسوله-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010009002804-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ماکلوان-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ماکلوان-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='ماکلوان-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='ماکلوان-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010009002804-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ماکلوان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ماکلوان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='ماکلوان-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='ماکلوان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 10100011002386-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رودبنه-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رودبنه-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='رودبنه-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='رودبنه-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 10100011002386-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رودبنه-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رودبنه-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='رودبنه-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='رودبنه-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 10100011001147-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لاهیجان-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لاهیجان-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='لاهیجان-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='لاهیجان-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 10100011001147-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لاهیجان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لاهیجان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='لاهیجان-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='لاهیجان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 10100010002385-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='اطاقور-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='اطاقور-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='اطاقور-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='اطاقور-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 10100010002385-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='اطاقور-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='اطاقور-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='اطاقور-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='اطاقور-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 10100010002141-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='شلمان-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='شلمان-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='شلمان-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='شلمان-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 10100010002141-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='شلمان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='شلمان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='شلمان-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='شلمان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 10100010001145-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لنگرود-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لنگرود-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='لنگرود-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='لنگرود-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 10100010001145-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لنگرود-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لنگرود-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='لنگرود-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='لنگرود-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 10100010001144-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='کومله-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='کومله-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='کومله-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='کومله-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 10100010001144-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='کومله-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='کومله-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='کومله-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='کومله-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 10100016001123-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ماسال-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ماسال-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='ماسال-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='ماسال-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 10100016001123-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ماسال-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ماسال-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='ماسال-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='ماسال-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1020001001149-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='آمل-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='آمل-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='آمل-مازندران-navar-tip-20cm' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='آمل-مازندران-navar-tip-20cm' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020001001149-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='آمل-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='آمل-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='آمل-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='آمل-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020001002875-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='بابکان-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='بابکان-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='بابکان-مازندران-navar-tip-20cm' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='بابکان-مازندران-navar-tip-20cm' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020001002875-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='بابکان-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='بابکان-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='بابکان-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='بابکان-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020001002586-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='دابودشت-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='دابودشت-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='دابودشت-مازندران-navar-tip-20cm' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='دابودشت-مازندران-navar-tip-20cm' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020001002586-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='دابودشت-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='دابودشت-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='دابودشت-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='دابودشت-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020001001148-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رینه-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رینه-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='رینه-مازندران-navar-tip-20cm' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='رینه-مازندران-navar-tip-20cm' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020001001148-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رینه-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رینه-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='رینه-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='رینه-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020001002388-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='گزنک-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='گزنک-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='گزنک-مازندران-navar-tip-20cm' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='گزنک-مازندران-navar-tip-20cm' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020001002388-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='گزنک-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='گزنک-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='گزنک-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='گزنک-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020002001153-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='امیرکلا-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='امیرکلا-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='امیرکلا-مازندران-navar-tip-20cm' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='امیرکلا-مازندران-navar-tip-20cm' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020002001153-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='امیرکلا-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='امیرکلا-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='امیرکلا-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='امیرکلا-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020002001154-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='بابل-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='بابل-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='بابل-مازندران-navar-tip-20cm' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='بابل-مازندران-navar-tip-20cm' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020002001154-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='بابل-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='بابل-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='بابل-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='بابل-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020002002392-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='زرگر-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='زرگر-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='زرگر-مازندران-navar-tip-20cm' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='زرگر-مازندران-navar-tip-20cm' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020002002392-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='زرگر-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='زرگر-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='زرگر-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='زرگر-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020002002391-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='مرزیکلا-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='مرزیکلا-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='مرزیکلا-مازندران-navar-tip-20cm' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='مرزیکلا-مازندران-navar-tip-20cm' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020002002391-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='مرزیکلا-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='مرزیکلا-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='مرزیکلا-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='مرزیکلا-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020002002587-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='گتاب-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='گتاب-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='گتاب-مازندران-navar-tip-20cm' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='گتاب-مازندران-navar-tip-20cm' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020002002587-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='گتاب-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='گتاب-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='گتاب-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='گتاب-مازندران-looleh-nakhi-tashoo' AND post_type='mazandaran'; COMMIT;


-- rollback: 1020002002390-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='گلوگاه-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='گلوگاه-مازندران-navar-tip-20cm' AND post_type='mazandaran' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='گلوگاه-مازندران-navar-tip-20cm' AND p.post_type='mazandaran'; DELETE FROM `ha_posts` WHERE post_name='گلوگاه-مازندران-navar-tip-20cm' AND post_type='mazandaran'; COMMIT;

