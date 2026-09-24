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


-- rollback: 10100017001060-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='چوکام-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='چوکام-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='چوکام-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='چوکام-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010005001125-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='خشکبیجار-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='خشکبیجار-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='خشکبیجار-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='خشکبیجار-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010005001125-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='خشکبیجار-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='خشکبیجار-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='خشکبیجار-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='خشکبیجار-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010005001129-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رشت-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رشت-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='رشت-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='رشت-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010005001129-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رشت-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رشت-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='رشت-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='رشت-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010005001130-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='سنگر-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='سنگر-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='سنگر-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='سنگر-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010005001130-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='سنگر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='سنگر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='سنگر-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='سنگر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010005002075-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لولمان-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لولمان-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='لولمان-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='لولمان-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010005002075-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لولمان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لولمان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='لولمان-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='لولمان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010005001007-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='پیربازار-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='پیربازار-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='پیربازار-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='پیربازار-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010005001007-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='پیربازار-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='پیربازار-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='پیربازار-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='پیربازار-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010005001127-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='کوچصفهان-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='کوچصفهان-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='کوچصفهان-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='کوچصفهان-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010005001127-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='کوچصفهان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='کوچصفهان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='کوچصفهان-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='کوچصفهان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 10100014001122-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رضوانشهر-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رضوانشهر-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='رضوانشهر-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='رضوانشهر-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 10100014001122-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رضوانشهر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رضوانشهر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='رضوانشهر-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='رضوانشهر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010006002229-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='توتکابن-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='توتکابن-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='توتکابن-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='توتکابن-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010006002229-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='توتکابن-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='توتکابن-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='توتکابن-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='توتکابن-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010006002138-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='جیرنده-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='جیرنده-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='جیرنده-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='جیرنده-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010006002138-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='جیرنده-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='جیرنده-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='جیرنده-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='جیرنده-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010006001132-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رودبار-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رودبار-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='رودبار-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='رودبار-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010006001132-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رودبار-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رودبار-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='رودبار-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='رودبار-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010006001131-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لوشان-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لوشان-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='لوشان-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='لوشان-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010006001131-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لوشان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='لوشان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='لوشان-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='لوشان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010006001133-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='منجیل-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='منجیل-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='منجیل-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='منجیل-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010006001133-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='منجیل-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='منجیل-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='منجیل-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='منجیل-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010007001137-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رودسر-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رودسر-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='رودسر-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='رودسر-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010007001137-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رودسر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='رودسر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='رودسر-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='رودسر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010007001139-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='واجارگاه-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='واجارگاه-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='واجارگاه-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='واجارگاه-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010007001139-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='واجارگاه-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='واجارگاه-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='واجارگاه-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='واجارگاه-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010007001135-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='چابکسر-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='چابکسر-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='چابکسر-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='چابکسر-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010007001135-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='چابکسر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='چابکسر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='چابکسر-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='چابکسر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010007001138-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='کلاچای-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='کلاچای-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='کلاچای-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='کلاچای-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010007001138-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='کلاچای-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='کلاچای-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='کلاچای-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='کلاچای-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 10100015002329-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='دیلمان-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='دیلمان-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='دیلمان-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='دیلمان-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 10100015002329-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='دیلمان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='دیلمان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='دیلمان-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='دیلمان-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 10100015001146-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='سیاهکل-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='سیاهکل-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='سیاهکل-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='سیاهکل-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 10100015001146-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='سیاهکل-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='سیاهکل-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='سیاهکل-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='سیاهکل-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 10100012001141-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='شفت-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='شفت-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='شفت-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='شفت-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 10100012001141-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='شفت-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='شفت-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='شفت-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='شفت-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010008001059-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ضیابر-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ضیابر-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='ضیابر-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='ضیابر-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;


-- rollback: 1010008001059-layflat
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ضیابر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='ضیابر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='ضیابر-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='ضیابر-گیلان-looleh-nakhi-tashoo' AND post_type='gilan'; COMMIT;


-- rollback: 1010008002140-tape20
START TRANSACTION; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='مرجقل-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `ha_posts` WHERE post_parent=(SELECT ID FROM `ha_posts` WHERE post_name='مرجقل-گیلان-navar-tip-20cm' AND post_type='gilan' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` p ON p.ID=pm.post_id WHERE p.post_name='مرجقل-گیلان-navar-tip-20cm' AND p.post_type='gilan'; DELETE FROM `ha_posts` WHERE post_name='مرجقل-گیلان-navar-tip-20cm' AND post_type='gilan'; COMMIT;

