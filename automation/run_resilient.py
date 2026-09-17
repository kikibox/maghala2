#!/usr/bin/env python3
import re
import translate_queue as tq

MAX_TEXT_CHARS=700
MAX_BATCH_ITEMS=4


def add_data_part(parser,data):
    if parser.skip or not tq.PERSIAN.search(data):
        parser.parts.append(data)
        return
    m=re.match(r'^(\s*)(.*?)(\s*)$',data,re.S)
    pre,core,post=m.groups()
    item={'id':len(parser.items),'text':core}
    parser.items.append(item)
    parser.parts.append({'id':item['id'],'pre':pre,'post':post})


def resilient_handle_data(parser,data):
    remaining=data
    while len(remaining)>MAX_TEXT_CHARS:
        candidates=[remaining.rfind(ch,0,MAX_TEXT_CHARS) for ch in ('\n','؟','.','!',' ')]
        cut=max(candidates)
        if cut<250:
            cut=MAX_TEXT_CHARS-1
        piece=remaining[:cut+1]
        remaining=remaining[cut+1:]
        add_data_part(parser,piece)
    if remaining:
        add_data_part(parser,remaining)


original_batch=tq.translate_segment_batch


def small_batch(items,lang):
    if len(items)<=MAX_BATCH_ITEMS:
        return original_batch(items,lang)
    merged={}
    for index in range(0,len(items),MAX_BATCH_ITEMS):
        merged.update(original_batch(items[index:index+MAX_BATCH_ITEMS],lang))
    return merged


tq.PreserveHTML.handle_data=resilient_handle_data
tq.translate_segment_batch=small_batch

if __name__=='__main__':
    tq.main()
