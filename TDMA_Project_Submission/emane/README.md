# EMANE integration

Run from the project root.

1. Generate 16-NEM EMANE configuration:
```bash
./emane/setup_emane.sh
```

2. Generate the schedule:
```bash
python3 main.py --input input/nodes.json --range 500 --emane-xml emane/schedule.xml
```

3. Start EMANE:
```bash
sudo ./emane/run_emane.sh
```

4. In another terminal publish the schedule:
```bash
./emane/publish_schedule.sh
```

5. Verify:
```bash
emanesh localhost get stat 1 mac | grep scheduler
emanesh localhost get table 1 mac scheduler.ScheduleInfoTable scheduler.StructureInfoTable
```

The Python Part 1 scheduler is independently validated. EMANE packet-level correctness
still requires actual schedule acceptance and traffic testing on the target WSL machine.
