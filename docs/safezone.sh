#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
workspace_root="$(cd -- "${script_dir}/.." && pwd)"

if [[ ! -f "${workspace_root}/setup_ekd.bash" ]]; then
  printf 'EKD workspace setup helper not found: %s/setup_ekd.bash\n' "${workspace_root}" >&2
  exit 1
fi

source "${workspace_root}/setup_ekd.bash"

if ! command -v roslaunch >/dev/null 2>&1; then
  printf 'ROS Noetic is not available in this terminal environment.\n' >&2
  exit 1
fi

printf '[%s] SafeZone | Starting continuous camera detection. Say a wake phrase to save and send one scene image.\n' \
  "$(date '+%H:%M:%S')"
exec roslaunch jupiterobot2_vision_yolov5 safezone_demo.launch "$@"
