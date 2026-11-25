# Pod operations: checks, terminate pass, measured costs

- Downloads: start them detached with `nohup setsid SCRIPT MODELS_DIR > LOG 2>&1 < /dev/null &` using `templates/pod-model-download.sh`. Poll with `timeout 25 ssh ... 'tail -3 LOG'` inside a loop with `sleep`.
- The deploy form can silently reset container disk to 15 GB when a template is saved. In the `Deploying ... Total / hour` block, check the "Total disk" line before clicking Deploy Pod. If it reverted, save the disk size as a template override and recheck.
- Terminate in one scripted pass: open the pod page, Stop, confirm Stop Pod, then Terminate, then confirm Terminate Pod. Verify the pod id is gone from the page text, then read the balance.
- Measured 2026-10-31: A40 48 GB at $0.59/hr plus $0.021/hr for a 150 GB disk. Two test pods plus downloads cost about $0.32 in total.
- Creating or terminating a pod needs the RunPod MCP connected, or the console through BrowserOS when it is logged in. Check before promising a pod.
