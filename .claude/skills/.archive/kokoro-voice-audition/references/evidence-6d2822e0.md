the video is a good one, but naration audio sound is not good enough for the video. so first we will generate few sample voice from kokoro tts, we have multiple voice available in kokoro tts

Called Bash: for v in am_adam am_echo am_eric am_fenrir am_liam am_michael am_onyx am_puck am_santa bm_daniel bm_fable bm_george bm_lewis; do curl -s -A "Mozilla/5.0" -H 'Content-Type: application/json' "$U/v1/audio/speech" -d "{...\"voice\":\"$v\",...\"speed\":0.85,\"response_format\":\"mp3\"}" -o $D/$v.mp3; printf '%s %s\n' $v $(stat -c %s $D/$v.mp3); done
-> am_adam 166700 ... bm_lewis 199340

Called Bash: for v in "am_onyx+bm_george" "am_onyx+am_michael" "am_onyx+am_fenrir" "bm_george+bm_lewis"; do ...; done
-> fusion_am_onyx_bm_george 11.088000 ... fusion_bm_george_bm_lewis 12.408000