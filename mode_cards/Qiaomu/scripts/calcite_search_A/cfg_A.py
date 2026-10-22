import os
SCRATCH = "C:/Users/yqm12/AppData/Local/Temp/claude/G--My-Drive-Qiaomu-Coding-LLM-Hackason/6904f568-fbff-48aa-b9f2-a1642df7e094/scratchpad"
CACHE = os.environ.get("CALA_XML_DIR") or SCRATCH + "/calciteA_xml"   # xml cache + scores.json
STAGE = SCRATCH + "/calciteA_stage"                                     # downloads are staged here, then copied into calcite/CALnnn_*
