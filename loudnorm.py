import ffmpy
import subprocess
import os
import json

for i in os.listdir("."):
    if not os.path.exists("processed"):
        os.makedirs("processed")
        if not os.path.exists("processed/wavs"):
            os.makedirs("processed/wavs")
        if not os.path.exists("processed/txt"):
            os.makedirs("processed/txt")
    outfilebase = "processed/" 
    outwav = outfilebase + "/wavs/" + os.path.splitext(i)[0] + ".wav"
    outtxt = outfilebase + "/txt/" + os.path.splitext(i)[0] + ".txt"

    if i[0] == "." or i[0] == "_" or i[-3:] == ".py" or i[-3:] == ".sh" or os.path.isdir(i) or i == "loudnorm":
        continue

    ff = ffmpy.FFmpeg(
        global_options="-hide_banner -loglevel info",
        inputs={i: None},
        outputs={'pipe:': '-f null -af loudnorm=print_format=json'}
    )
    none, loudstats = ff.run(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    """index = loudstats.decode().find("loudnorm")
    for a in loudstats.decode()[index:]:
        if a == "{":
            break
        index += 1
    loudstats = loudstats.decode()[index:]"""
    index = 0
    loudstats = loudstats.split(b'\n')
    for a in loudstats:
        if a == b"{":
            break
        index += 1
    loudstats = b"".join(loudstats[index:]) 
    loudstats = json.loads(loudstats)
    outflags = '-f wav -af loudnorm=measured_I=' + loudstats['input_i'] + ":measured_TP=" + loudstats['input_tp'] \
               + ":measured_LRA=" + loudstats['input_lra'] + ":measured_thresh=" + loudstats['input_thresh'] \
               + ":offset=" + loudstats['target_offset'] + ":print_format=summary"
    ff = ffmpy.FFmpeg(
        global_options="-hide_banner -loglevel info -y",
        inputs={i: None},
        outputs={outwav: outflags}
    )
    test, loudstats2 = ff.run(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    index = loudstats2.decode().find("[Parsed_loudnorm_0")
    loudstats2 = loudstats2.decode()[index:]
    open(outtxt, 'w').write(loudstats2)
