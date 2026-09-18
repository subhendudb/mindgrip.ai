# Optional LeRobot core patches

These diffs were extracted from the SO-101 Lab working tree. They are **not** required
for MuJoCo / keyboard plugins (those install as third-party packages).

Apply onto a LeRobot source checkout:

```bash
./scripts/apply_lerobot_patches.sh /path/to/lerobot
```

Or at Docker build time: `--build-arg APPLY_PATCHES=1`.

MindGrip project docs are separate (`docs/html/`). Official LeRobot docs:
https://huggingface.co/docs/lerobot
